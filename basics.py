import functools as ft
from operator import *
import cachetools as ct
from typing import GenericMeta
from .currying import curried, curry
from abc import ABCMeta, ABC

# from .functoid import Functoid

## Basic functional programming tools


def identity(x):
    return x


def const(x):
    return lambda _: x


def compose2(f, g):
    return lambda x:f(g(x))


def compose(*callables):
    return ft.reduce(compose2, callables)


def uncurry(f):
    return lambda args: f(*args)


def flip(f):
    return lambda *args, **kwargs: f(*reversed(args), **kwargs)


class SingletonWrapper:
    __slots__ = ['_instance', '_singleton_class']
    def __init__(self, singleton_class):
        super().__setattr__('_singleton_class', singleton_class)
        super().__setattr__('_instance', None)
        
    def __call__(self, *args, **kwargs):
        instance = super().__getattribute__('_instance')
        if instance is not None:
            if len(args) + len(kwargs) > 0:
                super().__getattribute__('update')(*args, **kwargs)
            return instance
        else:
            singleton_class = super().__getattribute__('_singleton_class')
            instance = singleton_class(*args, **kwargs)
            super().__setattr__('_instance', instance)
            return instance
        
    def update(self, *args, **kwargs):
        instance = super().__getattribute__('_instance')
        singleton_class = super().__getattribute__('_singleton_class')
        if instance is None:
            raise Exception("Cannot update singleton class {}: singleton instance not yet instantiated"\
                            .format(singleton_class))
        else:
            instance.__singleton_update__(*args, **kwargs)
            
    def __repr__(self):
        singleton_class = super().__getattribute__('_singleton_class')
        return "Singleton class {!r}".format(singleton_class)
    
    def __str__(self):
        singleton_class = super().__getattribute__('_singleton_class')
        return "Singleton class {!s}".format(singleton_class)
    
    def __getattribute__(self, name):
        delegate = super().__getattribute__('_singleton_class')
        return getattr(delegate, name)
    

class SingletonType(type):
    def __init__(cls, name, bases, nmspc):
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        instance = cls._instance
        if instance is not None:
            if len(args) + len(kwargs) > 0:
                cls.update(*args, **kwargs)
            return instance
        else:
            cls._instance = super().__call__(*args, **kwargs)
            return cls._instance

    def update(cls, *args, **kwargs):
        if cls._instance is None:
            raise Exception("Cannot update singleton instance of singleton class {}: singleton class not instantiated yet".format(cls))
        else:
            cls._instance.__singleton_update__(*args, **kwargs)


class SingletonBase(metaclass=SingletonType):
    pass


class Functoid(curried):
    """Wrapper class for functions and callables"""

    def __init__(self, function, *args, **kwargs):
        # print("Initializing")
        super().__init__()
        self.__name__ = "functoid {}".format(getattr(function, "__name__", str(function)))
        self.__doc__ = getattr(function, "__doc__", "a functoid")

    def before(self, f):
        return type(self)(lambda *args, **kwargs: f(self(*args, **kwargs)), self._autocurried, self._curry_last)
    
    def after(self, f):
        return type(self)(lambda *args, **kwargs: self(f(*args, **kwargs)), self._autocurried, self._curry_last)

    def flip(self):
        return type(self)(lambda *args, **kwargs: self.func(*reversed(args), **kwargs),
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
        return "<{}:({},{})>".format(self.__name__, self.args, self.keywords)

    def __str__(self):
        return self.__name__

    def __get__(self, instance, owner):
        return type(self)(self._func.__get__(instance, owner))

    def __set__(self, instance, value):
        return self.func.__set__(instance, value)


def functoid(n=0, curry_last=False):
    def decorator(f):        
        return Functoid(f,n,curry_last)
    return decorator


class ADTMeta(ABCMeta):
    """Metaclass for ADT-like types"""
    def __new__(cls, name, bases, attrs, cached=False, maxsize=100, **kwargs):
        return super(ADTMeta, cls).__new__(cls, name, bases, attrs, **kwargs)

    def __init__(cls, name, bases, attrs, functoid=True, cached=False, maxsize=100, **kwargs):
        super().__init__(name, bases, attrs, **kwargs)
        annots = tuple(getattr(cls, "__annotations__", {}))        
        
        cls._fields = fields = tuple(cls._fields) if "_fields" in vars(cls)\
            else tuple(frozenset(getattr(cls, "_fields", ())).union(annots))

        for i, field in enumerate(fields):
            setattr(cls, field, property(itemgetter(i)))
        cls._cache = ct.LRUCache(maxsize=(1 if len(fields) == 0 else maxsize)) if cached else None
        cls._cached = cached

        # if functoid:
        #     # print(name, cls)
        #     exclude = frozenset(getattr(cls, "__functoid_exclude__", ())).union(dir(object))
        #     # print(exclude)
        #     #print(frozenset(dir(cls)))
        #     include = frozenset(attrs.get("__functoid_include__")) if "__functoid_include__" in attrs \
        #         else frozenset(getattr(cls, "__functoid_include__", ())).union(attrs)
        #     # print(include)
        #     cls.__functoid_exclude__ = exclude
        #     cls.__functoid_include__ = include - exclude
        # else:
        #     cls.__functoid_include__ = cls.__functoid_exclude__ = frozenset(())
        

    # def __getattribute__(cls, name):
    #     attr = super().__getattribute__(name)
    #     functoids = super().__getattribute__("__functoid_include__")
    #     if name in functoids and callable(attr):
    #         return Functoid(attr, n=0, curry_last=False)
    #     else:
    #         return attr
            
    
class data(tuple, ABC, metaclass=ADTMeta):
    def __new__(cls, *args, **kwargs):
        if len(kwargs) + len(args) != len(cls._fields):
            raise TypeError(("Wrong number of arguments given to constructor of class {}." +\
                            " Expected {}, got {}.").format(cls.__name__,
                                                            len(cls._fields),
                                                            len(args)+len(kwargs)))
        else:
            values = tuple(args[i] if i < len(args) else kwargs[field]
                           for (i,field) in enumerate(cls._fields))
            if cls._cached:
                cached = cls._cache.get(values, None)
                if cached is None:
                    new = cls._cache[values] = super(data, cls).__new__(cls, values)
                    return new
                else:
                    return cached
            else:
                return super(data, cls).__new__(cls, values)

    def __repr__(self):
        return "{}({})".format(type(self).__name__, ",".join(map(str, self)))

    # def __getattribute__(self, name):
    #     attr = super().__getattribute__(name)
    #     functoids = super().__getattribute__("__functoid_include__")
    #     if name in functoids and callable(attr):
    #         return Functoid(attr, n=0, curry_last=False)
    #     else:
    #         return attr

# class SingletonDatatype(SingletonType, datatype):
#     def __init__(cls, name, bases, attrs):
#         datatype.__init__(cls, name, bases, attrs)
#         SingletonType.__init__(cls, name, bases, attrs)

        
# class singleton(tuple, metaclass=SingletonType):
#     def __init__(self, *args, **kwargs):
#         print("Initialized with parameters {}, {}".format(args, kwargs))
#         self._args = args
#         self._kwargs = kwargs

#     def __singleton_update__(self, *args, **kwargs):
#         self._args = args
#         self._kwargs = kwargs

#     def __repr__(self):
#         return "instance of class {} with attributes {}".format(self.__class__, vars(self))

    

# class singleton2(singleton):
#     def __init__(self, *args, **kwargs):
#         print("singleton2 initalized")
#         super().__init__(*args, **kwargs)
        

