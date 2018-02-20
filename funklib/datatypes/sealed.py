from functools import wraps

class Sealed(type):
    def __new__(cls, name, bases, nmspc, final=False, **kwds):
        nmspc = nmspc or {}
        for k in bases:
            if isinstance(k, Sealed) and nmspc["__module__"] != k.__module__:
                raise TypeError("Cannot subclass sealed class {} outside its module({}).".format(k.__name__, k.__module__))
            if isinstance(k, Sealed) and k.__final__:
                raise TypeError("Cannot subclass final sealed class {}".format(k.__name__))
        nmspc.setdefault("__final__", final)
        return super(Sealed, cls).__new__(cls, name, bases, nmspc, **kwds)

    
class SealedTest(metaclass=Sealed):
    def add(self):
        return sum(self)

class CachedFunction:
    def __init__(self, f):
        self.func = f
        self._cache = {}

    def __call__(self, *args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in self._cache:
            self._cache[key] = self.func(*args, **kwargs)
        return self._cache[key]

def cache(f):
    return wraps(f)(CachedFunction(f))

def make_printer(fields):
    def __repr__(self):
        return "{}({})".format(type(self).__name__, ",".join(repr(getattr(self, f)) for f in fields))
    return __repr__

    
def make_getters(fields):
    return dict(map(lambda f: (f[1], property(lambda self: self[f[0]])), enumerate(fields)))


def caseclass(base, fields, final=False, cached=False):
    def decorator(f):        
        def new(cls, *args, **kwargs):
            return tuple.__new__(cls, f(*args, **kwargs))                
        return Sealed(f.__name__, (base, tuple), dict(
            make_getters(fields),
            __new__=cache(new) if cached else new,
            __module__=f.__module__, __repr__=make_printer(fields)), final=final)
    return decorator


           
def Single(fields, cached=False, final=False):
    def decorator(f):        
        def new(cls, *args, **kwargs):
            return tuple.__new__(cls, f(*args, **kwargs))
        readers = make_getters(fields)
        return Sealed(f.__name__, (tuple,), dict(
            readers,
            __new__=cache(new) if cached else new,
            __module__=f.__module__, __repr__=make_printer(fields)), final=final)
    return decorator
        

def datatype(fields, final=False):
    def decorator(klass):
        def new(cls, *args, **kwargs):
            return tuple.__new__(cls, tuple(map(lambda p: args[p[0]] if p[0] < len(args) else kwargs[p[1]], enumerate(fields))))

        return Sealed(klass.__name__, (tuple,), dict(
            klass.__dict__,
            **make_getters(fields),
            __new__=new,
            __repr__=make_printer(fields)
        ), final=final)
    return decorator
    
    
