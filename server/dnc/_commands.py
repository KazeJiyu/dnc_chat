# Standard modules

# Custom utility functions
from server.utils.patterns import Dispatcher

# Restrict "from _commands import *"
__all__ = ['CommandDispatcher']

class CommandDispatcher(Dispatcher):
    
    @classmethod
    def register_cmd(cls, callback):
        name = callback.__name__.upper()
        return cls.set_callback(name, callback)

    def react(self, message, connection):
        cmd, *args = message.split()
        
        handler = self.dispatch(cmd.upper(), lambda *_: "298 ERR_MALFORMEDREQUEST")
        return handler(connection, args)
