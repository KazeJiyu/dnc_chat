'''
@copyright: the classes implemented in this package have been seen in : https://zestedesavoir.com/tutoriels/1226/le-pattern-dispatcher-en-python/
'''
from collections import ChainMap

class DispatcherMeta(type):
    
    def __new__(cls, name, bases, attrs):
        # Juste avant que la classe ne soit définie par Python

        # On construit le dictionnaire de callbacks en héritant de ceux des
        # classes mères
        callbacks = ChainMap()
        maps = callbacks.maps
        for base in bases:
            if isinstance(base, DispatcherMeta):
                maps.extend(base.__callbacks__.maps)

        # Comme avant, on ajoute le dictionnaire de callbacks et
        # la property "dispatcher" pour y accéder
        attrs['__callbacks__'] = callbacks
        attrs['dispatcher'] = property(lambda obj: callbacks)
        cls = super().__new__(cls, name, bases, attrs)
        return cls

    def set_callback(self, key, callback):
        self.__callbacks__[key] = callback
        return callback

    def register(self, key):
        """
        A decorator method used to register a new callback and associate it
        with the string `key`.
        """
        def wrapper(callback):
            return self.set_callback(key, callback)
        return wrapper

class Dispatcher(metaclass=DispatcherMeta):
    
    def dispatch(self, key, default=None):
        """
        Returns the callback associated to `key`.
        """
        return self.dispatcher.get(key, default)

    def __contains__(self, key):
        return key in self.dispatcher

class Visitor(Dispatcher):
    
    def visit(self, key, *args, **kwargs):
        handler = self.dispatch(type(key))
        if handler:
            return handler(self, key, *args, **kwargs)
        raise RuntimeError("Unknown key: {!r}".format(key))

    @classmethod
    def on(cls, type_):
        return cls.register(type_)