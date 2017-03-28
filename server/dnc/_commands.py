# Standard modules

# Custom utility functions
from dnc._data import ConnectionStatus, Client
from utils.errors import abort_if
from utils.patterns import Dispatcher
import logging

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

@CommandDispatcher.register_cmd
def connect(connection, args):
    abort_if(lambda: connection.status == ConnectionStatus.CONNECTED, "200 ERR_ALREADYCONNECTED")
    abort_if(lambda: len(args) < 1, "203 ERR_NOTENOUGHARGS")
    abort_if(lambda: args[0] in connection._protocol.clients, "205 ERR_NICKNAMEINUSE")

    pseudo = args[0]
    
    if len(pseudo) > 10 or pseudo.startswith('@') or ',' in pseudo:
        return "206 ERR_INVALIDNICKNAME"
    
    connection.status = ConnectionStatus.CONNECTED    
    connection.client = Client(pseudo, connection)
    connection._protocol.clients[pseudo] = connection.client
    return "100 RPL_DONE"

@CommandDispatcher.register_cmd
def quit(connection, args):  # @ReservedAssignment
    abort_if(lambda: connection.status == ConnectionStatus.NOT_CONNECTED, "201 ERR_NOTCONNECTED")

    connection.write_all(":" + connection.client.pseudo + " QUIT " + " ".join(args))
        
    connection.close();
        
    # no reply will be sent
    return None

@CommandDispatcher.register_cmd
def message(connection, args):
    abort_if(lambda: connection.status == ConnectionStatus.NOT_CONNECTED, "201 ERR_NOTCONNECTED")
    abort_if(lambda: connection.status == ConnectionStatus.AWAY, "-202 ERR_BADSTATUS")
    abort_if(lambda: len(args) < 1, "203 ERR_NOTENOUGHARGS")
        
    if args[0].startswith('!'):                
        return connection._protocol.chat_bot.react(*args)

    connection.write_all(":" + connection.client.pseudo + " MESSAGE " + " ".join(args))
            
    return "100 RPL_DONE"

@CommandDispatcher.register_cmd
def whisper(connection, args):
    abort_if(lambda: connection.status == ConnectionStatus.NOT_CONNECTED, "201 ERR_NOTCONNECTED")
    abort_if(lambda: connection.status == ConnectionStatus.AWAY, "202 ERR_BADSTATUS")
    abort_if(lambda: len(args) < 2, "203 ERR_NOTENOUGHARGS")

    dest = args[0]
    
    try:
        abort_if(lambda: not connection in connection._protocol[dest].connection.private, "207 ERR_WHISPERNOTALLOWED")
        message = " ".join(args[1:])

        connection.write_to(dest, ":" + connection.client.pseudo + " WHISPER " + message)
    except KeyError:
        return "204 ERR_NICKNAMENOTEXIST"
    
    return "100 RPL_DONE"

@CommandDispatcher.register_cmd
def ask_whisper(connection, args):
    abort_if(lambda: connection.status == ConnectionStatus.NOT_CONNECTED, "201 ERR_NOTCONNECTED")
    abort_if(lambda: connection.status == ConnectionStatus.AWAY, "-202 ERR_BADSTATUS")
    abort_if(lambda: len(args) < 1, "203 ERR_NOTENOUGHARGS")
    
    dest = args[0]
    
    try:
        connection.write_to(dest, ":" + str(connection.client.pseudo) + " ASK_WHISPER")
    except KeyError:
        return "204 ERR_NICKNAMENOTEXIST"
    
    return "100 RPL_DONE"

@CommandDispatcher.register_cmd
def reply_whisper(connection, args):
    abort_if(lambda: connection.status == ConnectionStatus.NOT_CONNECTED, "201 ERR_NOTCONNECTED")
    abort_if(lambda: connection.status == ConnectionStatus.AWAY, "-202 ERR_BADSTATUS")
    abort_if(lambda: len(args) < 2, "203 ERR_NOTENOUGHARGS")
    
    dest = args[0]
    answer = str(args[1]).strip()
    
    try:
        connection.write_to(dest, ":" + str(connection.client.pseudo) + " REPLY_WHISPER " + str(answer))
    except KeyError:
        return "204 ERR_NICKNAMENOTEXIST"
    else:
        if answer.lower() == "yes":
            dest_connection = connection._protocol[dest].connection
            connection.private.append(dest_connection)
            dest_connection.private.append(connection)
    
    return "100 RPL_DONE"

@CommandDispatcher.register_cmd
def stop_whisper(connection, args):
    abort_if(lambda: connection.status == ConnectionStatus.NOT_CONNECTED, "201 ERR_NOTCONNECTED")
    abort_if(lambda: connection.status == ConnectionStatus.AWAY, "-202 ERR_BADSTATUS")
    abort_if(lambda: len(args) < 1, "203 ERR_NOTENOUGHARGS")
    
    dest = args[0]
    
    try:
        dest_connection = connection._protocol[dest].connection
        dest_connection.private.remove(connection)
        
        connection.private.remove(dest_connection)
    except KeyError:
        return "204 ERR_NICKNAMENOTEXIST"
    
    return "100 RPL_DONE"

@CommandDispatcher.register_cmd
def file(connection, args):
    abort_if(lambda: connection.status == ConnectionStatus.NOT_CONNECTED, "201 ERR_NOTCONNECTED")
    abort_if(lambda: len(args) < 3, "203 ERR_NOTENOUGHARGS")
    
    dest, file, size = args[0], args[1], args[2]
    
    try:
        connection.write_to(dest, ":" + connection.client.pseudo + " FILE " + file + " " + size)
    except KeyError:
        return "204 ERR_NICKNAMENOTEXIST"
    
    return "100 RPL_DONE"

@CommandDispatcher.register_cmd
def mute(connection, args):
    abort_if(lambda: connection.status == ConnectionStatus.NOT_CONNECTED, "201 ERR_NOTCONNECTED")
    abort_if(lambda: len(args) < 1, "203 ERR_NOTENOUGHARGS")
    
    in_error = []
    
    for pseudo in args:
        try:
            to_mute = connection._protocol.clients[pseudo]
        except KeyError:
            in_error.append(pseudo)
        else:
            connection.ignored.append(to_mute.connection)
        
    return "100 RPL_DONE" if not in_error else "204 ERR_NICKNAMENOTEXIST " + " ".join(in_error) 
    
@CommandDispatcher.register_cmd
def listen(connection, args):
    abort_if(lambda: connection.status == ConnectionStatus.NOT_CONNECTED, "201 ERR_NOTCONNECTED")
    abort_if(lambda: len(args) < 1, "203 ERR_NOTENOUGHARGS")
    
    in_error = []
    
    for pseudo in args:
        try:
            to_listen = connection._protocol.clients[pseudo]
        except KeyError:
            in_error.append(pseudo)
        else:
            connection.ignored.remove(to_listen.connection)
        
    return "100 RPL_DONE" if not in_error else "204 ERR_NICKNAMENOTEXIST " + " ".join(in_error) 

@CommandDispatcher.register_cmd
def names(connection, args):
    abort_if(lambda: connection.status == ConnectionStatus.NOT_CONNECTED, "201 ERR_NOTCONNECTED")
    
    return "101 RPL_NAMES " + " ".join(client for client in connection._protocol.clients)

@CommandDispatcher.register_cmd
def away(connection, args):
    abort_if(lambda: connection.status == ConnectionStatus.NOT_CONNECTED, "201 ERR_NOTCONNECTED")
    
    connection.status = ConnectionStatus.AWAY
    return "100 RPL_DONE"

@CommandDispatcher.register_cmd
def re(connection, args):
    abort_if(lambda: connection.status == ConnectionStatus.NOT_CONNECTED, "201 ERR_NOTCONNECTED")
    
    connection.status = ConnectionStatus.CONNECTED
    return "100 RPL_DONE"

@CommandDispatcher.register_cmd
def nick(connection, args):
    abort_if(lambda: connection.status == ConnectionStatus.NOT_CONNECTED, "201 ERR_NOTCONNECTED")
    abort_if(lambda: len(args) < 1, "203 ERR_NOTENOUGHARGS")
    abort_if(lambda: args[0] in connection._protocol.clients, "205 ERR_NICKNAMEINUSE")
    
    new_nick = args[0]
    
    if len(new_nick) > 10 or new_nick.startswith('@') or ',' in new_nick:
        return "206 ERR_INVALIDNICKNAME"
    
    connection.write_all(":" + connection.client.pseudo + " NICK " + " " + new_nick)
    connection._protocol.clients.rename(connection.client, args[0])
    
    return "100 RPL_DONE"
