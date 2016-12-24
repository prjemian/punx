
'''
singletons: Python 2 and 3 Compatible Version

:see: http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
'''
class _Singleton(type):
    """ A metaclass that creates a Singleton base class when called. """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton(_Singleton('SingletonMeta', (object,), {})): pass


class One(Singleton):
    thing = 'thing'

class Two(Singleton):
    thing = 'bob'

if __name__ == '__main__':
    print(One().thing)
    o = One()
    o.thing = 1
    print(One().thing)
    
    o = Two()
    o.thing = 2
    print(Two().thing)
    print(Two().thing)
