# Standard libraries
import socket
import select
import threading
import logging

class Connection():
    '''
    Represents a connection with a server's client.
    
    Besides the methods described in this class, some methods
    can be added to instances according to the type of connection.
    
    For example, in the case of a TCP connection, instances may have
    methods to write to the server. 
    '''

    def on_connection_started(self):
        """
        Called by the server after the initialization of the connection.
        """
    
    def on_connection_closed(self):
        """
        Called by the server after the closure of the connection's socket. 
        """
    
    def on_connection_failed(self):
        """
        """
        
    def on_connection_lost(self):
        """
        Called by the server when the connection with the client is closed prematurely.
        """
        
    def on_data_received(self, data):
        """
        Called by the server when data is received from the client.
        
        Daughters of `Connection` must implement this method in order to handle client's request.
        """
        raise NotImplementedError
    
class Protocol:
    """
    Represents a global communication protocol.
    
    A protocol is like a `:class:Connection` factory, since its role is to create
    a new one for each client. 
    """
    
    def create_new_connection(self):
        raise NotImplementedError
    
    def allows_to_send(self, sender, receiver, message):
        """
        Returns whether the protocol allows `sender` to send `message` to `receiver`.
        
        Arguments:
        ----------
            sender (Connection): the connection of the client that wants to send a message
            receiver (Connection): the connection of the recipient
            message (str): the message to send
        """
        return True

    def get_connection(self, key):
        """
        Returns the connection associated with `key`, 
        which is likely to be the pseudo of the client.
        
        Arguments:
            key (str): the key that identify the connection
        """
        raise NotImplementedError
    
    def __getitem__(self, key):
        """
        A shortcut for `:func:get_connection()`.
        """
        return self.get_connection(key)

class TcpServer():
    """
    A server that can handle TCP requests.
    
    Request processing:
    -----------------
        The process of requests is delegated to the given protocol.
    
        The connections created are filled with the following methods:
            - ip() : returns the client's ip
            - write(str): writes a message to the connection's client
            - write_to(pseudo, message): writes a message to `pseudo`
            - write_all(message): writes a message to all other clients
            - close(): closes the associated socket, then call `:func:on_connection_close`
    
    Attributes:
    -----------
        port (int): the port on which the server listens
        is_over (threading.Event): indicates whether the server is over.
                                   This flag is used to close sub-threads.
        opened_sockets (List[socket]): a list of sockets likely to receive incoming data
        protocol (Protocol): the protocol that deals with requests from clients.
        connection_per_socket (Map[socket,Connection])
    """

    def __init__(self, protocol, port=8123):
        """
        Arguments:
        ----------
        @type protocol: C{Protocol}
        @param protocol: the _protocol charged of dealing with TCP requests 
        @keyword port: the _port on which the server should listen
        """
        self._port = port
        self._protocol = protocol
        self._is_over = threading.Event()
        self._opened_sockets = []
        self._local_socket = None
        self._connection_per_socket = {}
        
    def port(self) -> int:
        """
        Returns the _port on which the server runs.
        """
        return self._port
    
    def _create_local_socket(self):
        """
        Creates and then returns server's socket.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', self._port))
        sock.listen(5)
        sock.setblocking(0)
        logging.info(f"Server is waiting (PORT={self._port})")
        
        return sock 
   
    def run_forever(self, poll_interval=0.5):
        """
        Runs the server so that it loops indefinitely. 
        
        Arguments:
        ----------
            poll_interval (float): the timeout ...
        """
        
        self._is_over.clear()
        
        with self._create_local_socket() as server_sock:
            
            self._opened_sockets = [server_sock]        
            self._local_socket = server_sock

            try:
                while not self._is_over.is_set():
                    # readable is a list that contains server_sock if it have incoming data buffered and available to be read
                    readable_sockets, _, _ = select.select(self._opened_sockets, [], [], poll_interval)
                    
                    for sock in readable_sockets:
                        if sock == self._local_socket:
                            self._handle_new_connection(sock)
                        else:
                            self._handle_existing_connection(sock)
            
            except KeyboardInterrupt:
                logging.info("Closing...")
                self._is_over.set()
            except Exception:
                logging.exception("")
                raise
            finally:
                for sock in self._opened_sockets:
                    sock.close()
            
    def _broadcast(self, sender_socket, message):
        """
        Broadcasts `message` to all sockets except `sender_socket`.
        """
        sender = self._connection_per_socket[sender_socket]
        for socket in self._opened_sockets:
            if socket is not sender_socket and socket is not self._local_socket:
                try:
                    receiver = self._connection_per_socket[socket]
                    if self._protocol.allows_to_send(sender, receiver, message):
                        socket.send(message)
                except:
                    self._close_socket(socket)
                    
    def _close_socket(self, socket, connection_lost=False):
        """
        Closes `socket` and calls `:func:on_connection_close` of the associated connection.
        """
        # ignore the socket if it is already closed
        if socket not in self._connection_per_socket:
            return
        
        socket.close()
        
        connection = self._connection_per_socket[socket]
        
        if connection_lost:
            logging.info(f"CONNECTION LOST: {connection.client}")
            connection.on_connection_lost()
        else:
            logging.info(f"CONNECTION CLOSED: {connection.client}")
            connection.on_connection_closed()

        self._opened_sockets.remove(socket)
            
    def _handle_new_connection(self, server_socket):
        """
        Called by `:func:run_forever` when a new connection is initiated by a client.
        
        This method accepts the incoming socket, and then asks the server's protocol
        to create an associated connection. Finally, utility methods are added to the
        new connection in order to make it able to send messages to other clients.
        """
        client_socket, client_addr = server_socket.accept()
        
        # prepare to receive new data from this socket
        self._opened_sockets.append(client_socket)
        
        # create the new connection
        connection = self._protocol.create_new_connection()
        connection.ip = lambda: server_socket.getsockname()[0]
        connection.write = lambda message: client_socket.send(message.encode())
        connection.write_to = lambda pseudo, message: self._protocol[pseudo].connection.write(message)
        connection.write_all = lambda message: self._broadcast(client_socket, message.encode())
        connection.close = lambda: self._close_socket(client_socket)
        
        self._connection_per_socket[client_socket] = connection
        
        connection.on_connection_started()
        
        logging.info(f"NEW CONNECTION: {client_addr}")
        
    def _handle_existing_connection(self, client_socket):
        """
        Called by `:func:run_forever` when a message is received from `client_socket`,
        that is an already connected socket.
        
        This method reads the content of the socket, and then lets the associated connection
        deal with it.
        """
        connection = self._connection_per_socket[client_socket]
        
        try:
            request = client_socket.recv(2048)
            request = request.decode()
            
            if request:
                connection.on_data_received(request)
            else:
                self._close_socket(client_socket)

        except ConnectionResetError:
            self._close_socket(client_socket, True)