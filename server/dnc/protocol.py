# Standard imports
import logging
from threading import Lock

# Local imports
from dnc._commands import CommandDispatcher
from dnc._data import ConnectionStatus, Clients, Client
from tcp import Connection, Protocol

class _DncConnection(Connection):
    """
    Represents a connection with a client using the DNC protocol.
    
    Attributes:
    -----------
        protocol (Protocol): the DNC protocol
        status (ConnectionStatus): the status of the client
        client (User): store data about the client
    """

    def __init__(self, protocol):
        self._protocol = protocol
        self.status = ConnectionStatus.NOT_CONNECTED
        self.client = None
        self.ignored = []
        self.private = []
        
    def __eq__(self, rhs):
        return self.client == rhs.client
        
    def on_data_received(self, data):
        logging.info(f"from {self.client} received: {data}")
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
        if self.client is not None:
            self._protocol.clients -= self.client
            
    def on_connection_lost(self):
        self.write_all(f":{self.client.pseudo} QUIT")
        
class DncProtocol(Protocol):
    
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
           and sender.status is not ConnectionStatus.NOT_CONNECTED \
           and sender not in receiver.ignored 
    
    def add_client(self, login):
        self.clients[login] = Client(login)