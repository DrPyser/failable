import abc
from functools import wraps, partial, reduce, update_wrapper
import logging

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

class Functoidal(abc.ABC):
    """Abstract base class for callables"""
    __slots__ = ()

    @abc.abstractmethod
    def before(self, f):
        pass

    @abc.abstractmethod
    def after(self, f):
        pass

    @abc.abstractmethod
    def flip(self):
        pass

    def __rshift__(self, f):
        LOGGER.info("composing {} before {}".format(self, f))
        return self.before(f)

    def __rrshift__(self, f):
        LOGGER.info("composing {} after {}".format(self, f))
        return self.after(f)

    def __rlshift__(self, f):
        LOGGER.info("composing {} before {}".format(self, f))
        return self.before(f)

    def __lshift__(self, f):
        LOGGER.info("composing {} after {}".format(self, f))
        return self.after(f)

    @abc.abstractmethod
    def curry(self, *args, **kwargs):
        pass
    
    @abc.abstractmethod
    def uncurry(self):
        pass

    def __ror__(self, value):
        return self(value)


class compose(Functoidal, tuple):
    def __new__(cls, *callables):
        if len(callables) == 0:
            raise ValueError("At least one callable must be provided")
        return tuple.__new__(cls, callables)

    def __call__(self, *args, **kwargs):
        return reduce(lambda acc, f: f(acc), self[1:], self[0](*args, **kwargs))

    def curry(self, *args, **kwargs):
        return Functoid(self, *args, **kwargs)

    def uncurry(self):
        return Functoid(lambda args: self(*args))

    def flip(self):
        return Functoid(lambda *args, **kwargs: self(*reversed(args), **kwargs))

    def before(self, f):
        return compose(*self, f)

    def after(self, f):
        return compose(f, *self)

    def __get__(self, instance, owner):
        func = lambda *args, **kwargs: self(*args, **kwargs)
        return Functoid(func.__get__(instance, owner))

    def __set__(self, instance, value):
        func = lambda *args, **kwargs: self(*args, **kwargs)
        func.__set__(instance, value)

    def __repr__(self):
        return "compose({})".format(
            ", ".join(map(repr, self))
        )
    

class Functoid(Functoidal, partial):
    """Wrapper class for callables with functional interface"""
    
    def __init__(self, function, *args, **kwargs):
        partial.__init__(self)
        update_wrapper(self, function)
        
    def before(self, f):
        return compose(self, f)
    
    def after(self, f):
        return compose(f, self)

    def flip(self):
        return Functoid(lambda *args, **kwargs: self.func(*reversed(args), **kwargs))

    def curry(self, *args, **kwargs):
        return Functoid(self.func, *self.args, *args, **dict(self.keywords, **kwargs))
    
    def uncurry(self):
        return Functoid(lambda args: self(*args))

    def __repr__(self):
        return "Functoid(name={}, func={!r}, args={!r}, kwargs={!r})".format(getattr(self, "__name__", None), self.func, self.args, self.keywords)

    def __str__(self):
        return "Functoid {}".format(getattr(self, "__name__", None))

    def __get__(self, instance, owner):
        return Functoid(self.func.__get__(instance, owner), *self.args, **self.keywords)

    def __set__(self, instance, value):
        return self.func.__set__(instance, value)

    
def functoid(f, *args, **kwargs):
    return wraps(f)(Functoid(f, *args, **kwargs))


class FunctoidDescriptor:
    """Descriptor that generate a new functoid from underlying object when accessed"""
    def __init__(self, descriptor, args, kwargs):
        self._underlying = descriptor
        self._args = args
        self._kwargs = kwargs

    def __get__(self, instance, owner=None):
        return functoid(*self._args, **self._kwargs)(self._underlying.__get__(instance, owner))

    def __set__(self, instance, value):
        self._underlying.__set__(instance, value)

    def __delete__(self, instance):
        self._underlying.__delete__(instance)

def functoidmethod(*args, **kwargs):
    def decorator(f):
        return FunctoidDescriptor(f, args, kwargs)
    return decorator


# class FunctoidalType(type):
#     # def __new__(cls, name, bases, attrs):
#     #     ignored_defaults = vars(object)
#     #     ignored = attrs.get("non_functoids", ignored_defaults)
#     #     attrs = {k:(Functoid(f) if callable(f) and k not in ignored else f) for (k,f) in attrs.items()}
#     #     return super().__new__(cls, name, bases, attrs)

#     def __init__(cls, name, bases, attrs):
#         super().__init__(name, bases, attrs)
#         if 'non_functoids' in dir(cls):
#             ignored = type.__getattribute__(cls, 'non_functoids')
#             type.__setattr__(cls, 'non_functoids', frozenset(ignored).union(dir(object)))
#         else:
#             cls.non_functoids = dir(object)
       
        
#     def __getattribute__(cls, name):
#         attr = type.__getattribute__(cls, name)
#         ignored = type.__getattribute__(cls, 'non_functoids')
#         return Functoid(attr) if callable(attr) and name not in ignored else attr
    
# class FunctoidalAbstractType(FunctoidalType, ABCMeta):
#     def __init__(cls, name, bases, attrs):
#         FunctoidalType.__init__(cls, name, bases, attrs)
#         ABCMeta.__init__(cls, name, bases, attrs)

# class FunctoidalABC(metaclass=FunctoidalAbstractType):
#     non_functoids = dir(object)
#     def __getattribute__(self, name):
#         attr = object.__getattribute__(self, name)
#         return Functoid(attr) if callable(attr) and name not in type(self).non_functoids else attr

        
# class FunctoidalSingletonType(FunctoidalAbstractType, SingletonType):
#     def __init__(cls, name, bases, attrs):
#         FunctoidalAbstractType.__init__(cls, name, bases, attrs)
#         SingletonType.__init__(cls, name, bases, attrs)
        

# if __name__ == "__main__":
#     @functoid(n=2)
#     def add(x,y):
#         return x+y
