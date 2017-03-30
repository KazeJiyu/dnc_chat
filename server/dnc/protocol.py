# Standard imports
import logging
from threading import Lock

# Local imports
from server.dnc._commands import CommandDispatcher
from server.dnc._data import ConnectionStatus, Clients, Client
from server.tcp import Connection, Protocol

class _DncConnection(Connection):
    """
    Represents a connection with a client using the DNC protocol.
    
    Attributes:
    -----------
        protocol (Protocol): the DNC protocol
        status (ConnectionStatus): the status of the client
        client (User): store data about the client
        private (set[Connection]): the connection with which a private conversation has been started
    """

    def __init__(self, protocol):
        self._protocol = protocol
        self.status = ConnectionStatus.NOT_CONNECTED
        self.client = None
        self.private = set()
        self.ignored = set()
        
    def __eq__(self, rhs):
        return self.client == rhs.client
    
    def __hash__(self):
        return hash(self.client.pseudo) if self.client else "None" 
        
    def on_data_received(self, data):
        if self.client:
            logging.info(f"FROM {self.ip()} - {self.client.pseudo}: {data}")
        else:
            logging.info(f"FROM {self.ip()}: {data}")
        
        try:
            response = self._protocol.commands.react(data, self)
        except ValueError as e:
            response = str(e)
        except:
            response = "299 ERR_INTERNALERROR"
            self.write(response)
            raise
            
        if response:
            self.write(response)
        
    def on_connection_closed(self):
        if self.client is None:
            return
            
        self._protocol.clients -= self.client
        
        for friend in self.private:
            friend.private.remove(self)
            
    def on_connection_lost(self):
        self.write_all(f":{self.client.pseudo} QUIT")
        self.on_connection_closed()
        
class DncProtocol(Protocol):
    """
    
    """
    
    def __init__(self):
        self.clients = Clients()
        self.commands = CommandDispatcher()
        
        self.lock = Lock()
        self.file_id = 0
        self.sender_per_file_request = {}
        
    def generate_file_id(self, file_name):
        with self.lock:
            self.file_id += 1
            
        return str(self.file_id)
    
    def create_new_connection(self):
        return _DncConnection(self)
    
    def get_connection(self, key):
        #return self.clients.all.get(key)
        return self.clients[key]
    
    def allows_to_send(self, sender, receiver, message):
        return receiver.client is not None \
           and sender not in receiver.ignored \
           and sender.status is not ConnectionStatus.NOT_CONNECTED 
    
    def add_client(self, login):
        self.clients[login] = Client(login)