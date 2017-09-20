from abc import ABC, ABCMeta
# from .basics import SingletonType
from .currying import curried, curry
from functools import wraps

class Functoid(curried):
    """Wrapper class for functions and callables"""

    def __init__(self, function, *args, **kwargs):
        self.__name__ = function.__name__
        self.__doc__ = function.__doc__

    def before(self, f):
        return Functoid(lambda *args, **kwargs: f(self(*args, **kwargs)), self._autocurried, self._curry_last)
    
    def after(self, f):
        return Functoid(lambda *args, **kwargs: self(f(*args, **kwargs)), self._autocurried, self._curry_last)

    def flip(self):
        return Functoid(lambda *args, **kwargs: self.func(*reversed(args), **kwargs),
                          self._autocurried, self._curry_last, self.args, self.keywords)

    def __rshift__(self, f):
        return self.before(f)

    def __lshift__(self, f):
        return self.after(f)

    def curry(self, *args, **kwargs):
        missing = self._autocurried - len(args) - len(kwargs)
        return Functoid(self.func, missing, missing > 0 and self._curry_last, self.args+args, dict(self.keywords, **kwargs))
    
    def uncurry(self):
        return Functoid(lambda args: self(*args))

    def __repr__(self):
        return "<functoid of {}:({},{})>".format(self.func, self.args, self.keywords)

    def __str__(self):
        return "functoid {}".format(self.func)

    def __get__(self, instance, owner):
        return Functoid(self.func.__get__(instance, owner), self._autocurried, self._curry_last, self.args, self.keywords)

    def __set__(self, instance, value):
        return self.func.__set__(instance, value)


def functoid(n=0, curry_last=False):
    def decorator(f):        
        return wraps(f)(Functoid(f,n,curry_last))
    return decorator


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
