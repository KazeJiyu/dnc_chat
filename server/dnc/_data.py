from enum import Enum
from utils.errors import abort_if

class ConnectionStatus(Enum):
    AWAY = 'away'
    CONNECTED = 'connected'
    NOT_CONNECTED = 'not connected'

class Client():
    """
    A basic chat's client.
    
    Attributes:
    -----------
        pseudo (str): the pseudo used by the client
        connection (Connection): the connection that links the server and the client 
    """

    def __init__(self, pseudo, connection):
        self.pseudo = pseudo
        self.connection = connection
      
    def __eq__(self, rhs):
        if not isinstance(rhs, Client):
            return NotImplemented
        return self.pseudo == rhs.pseudo
      
    def __str__(self):
        return self.pseudo
      
class Clients:
    """
    Represents a list of chat's clients.
    """

    def __init__(self):
        self.__clients = {}
      
    @property
    def all(self):
        return self.__clients
        
    def from_pseudo(self, pseudo):
        return self.__clients[pseudo]
      
    def from_address(self, address):
        return next((client for client in self.all.values() if client.address == address), None)
    
    def rename(self, client, new_pseudo):
        if isinstance(client, str):
            client = self[client]
        
        self -= client
        client.pseudo = new_pseudo
        self += client
        
    def __contains__(self, client):
        if isinstance(client, Client):
            return client.pseudo in self.__clients
        if isinstance(client, str):
            return client in self.__clients
        if isinstance(client, tuple):
            return self.from_address(client) != None
        return False
        
    def __iter__(self):
        # yield from self.all
        for client in self.all:
            yield client
            
    def __getitem__(self, key):
        if isinstance(key, str):
            return self.from_pseudo(key)
        if isinstance(key, tuple):
            return self.from_address(key)
        raise KeyError
            
    def __setitem__(self, pseudo, client):
        self.__clients[pseudo] = client
      
    def __iadd__(self, client):
        abort_if(lambda: not isinstance(client,Client), "cannot add a non Client instance")
        self.__clients[client.pseudo] = client
        return self
        
    def __isub__(self, client):
        if isinstance(client, Client):
            del self.all[client.pseudo]
        elif isinstance(client, tuple):
            del self.all[ self[client].pseudo ]
        elif isinstance(client, str):
            del self.all[client]
        return self