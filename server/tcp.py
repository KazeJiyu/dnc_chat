# Standard libraries
import socket
import select
import threading
import logging

class TcpServer():
    """
    
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
            except Exception as e:
                logging.error(f"an error occured: {e}")
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
        logging.info("socket closed for " + str(connection.client))
        
        if connection_lost:
            connection.on_connection_lost()
        else:
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
        connection.write = lambda message: client_socket.send(message.encode())
        connection.write_to = lambda pseudo, message: self._protocol[pseudo].connection.write(message.encode())
        connection.write_all = lambda message: self._broadcast(client_socket, message.encode())
        connection.close = lambda: self._close_socket(client_socket)
        
        self._connection_per_socket[client_socket] = connection
        self._protocol.on_new_connection_completed(connection)
        
        connection.on_connection_started()
        
        logging.info("New client : " + str(client_addr))
        
    def _handle_existing_connection(self, client_socket):
        """
        Called by `:func:run_forever` when a message is received from `client_socket`,
        that is an already connected socket.
        
        This method reads the content of the socket, and then lets the associated connection
        deal with it.
        """
        try:
            request = client_socket.recv(2048).decode()
            
            if request:
                client = self._connection_per_socket[client_socket]
                client.on_data_received(request)
            else:
                self._close_socket(client_socket)

        except:
            self._close_socket(client_socket)
            raise