
'''
singletons: Python 2 and 3 Compatible Version

:see: http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python

USAGE::

    class Logger(Singleton):
        pass

'''

class _Singleton(type):
    """ A metaclass that creates a Singleton base class when called. """
    _instances = {}
    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = super(_Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]

class Singleton(_Singleton('SingletonMeta', (object,), {})): pass
