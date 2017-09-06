from abc import (ABCMeta, abstractmethod, ABC)
import itertools as it
import functools as ft
import operator as op
from basics import *
from multimethods.multimethods import (multimethod, method, type_dispatch)
from collections.abc import Iterable

class Functoid:
    def __init__(self, function):
        self._func = function
        self.__name__ = getattr(function, "__name__", "functoid")
        self.__doc__ = getattr(function, "__doc__", "a functoid")

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)

    def curry(self, *args, **kwargs):
        return Functoid(ft.partial(self._func, *args, **kwargs))
    
    def before(self, f):
        return Functoid(lambda *args, **kwargs: f(self._func(*args, **kwargs)))

    def after(self, f):
        return Functoid(lambda *args, **kwargs: self._func(f(*args, **kwargs)))
    
    def uncurry(self):
        return Functoid(lambda args: self._func(*args))

    def __repr__(self):
        return "<functoid of {}>".format(str(self._func))


class FunctoidDescriptor:
    def __init__(self, descriptor):
        self._underlying = descriptor

    def __get__(self, instance, owner=None):
        return Functoid(self._underlying.__get__(instance, owner))

    def __set__(self, instance, value):
        self._underlying.__set__(instance, value)

    def __delete__(self, instance):
        self._underlying.__delete__(instance)

    
class FunctoidalType(type):
    def __getattribute__(cls, name):
        attr = super(FunctoidalAbstractType, cls).__getattribute__(name)
        return Functoid(attr) if callable(attr) else attr
    
class FunctoidalAbstractType(ABCMeta):    
    def __getattribute__(cls, name):
        attr = super(FunctoidalAbstractType, cls).__getattribute__(name)
        return Functoid(attr) if callable(attr) and name not in cls.non_functoids else attr


class FunctoidalABC(metaclass=FunctoidalAbstractType):
    non_functoids = [x for x in vars(object)]
    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        return Functoid(attr) if callable(attr) and name not in type(self).non_functoids else attr
    

class Functor(FunctoidalABC):
    @abstractmethod
    def fmap(self, f):
        raise NotImplementedError()


class Applicative(Functor):
    @classmethod
    @abstractmethod
    def pure(cls, x):
        raise NotImplementedError()
    
    @abstractmethod
    def ap(self, fa):
        raise NotImplementedError()

    def fmap(self, f):
        return self.pure(f).ap(self)

    
class Monad(Applicative):
    @abstractmethod
    def bind(self, f):
        raise NotImplementedError()

    def fmap(self, f):
        return self.then(Functoid(f).before(self.pure))

    def join(self):
        return self.then(identity)

    def ap(self, g):
        return self.then(g.fmap)

    @classmethod
    @abstractmethod
    def fail(cls, msg):
        raise NotImplementedError()
    
class Monoid(FunctoidalABC):
    def __init__(self, op, identity):
        self.op = op
        self.identity = identity
    
    def __call__(self, x, y):
        return self.op(x, y)

    def fold(self, iterable):
        return reduce(self.op, iterable, self.identity)

    
class ArrayList(Monad, list):
    def __init__(self, iterable):
        list.__init__(self, iterable)

    def fmap(self, f):
        return ArrayList(map(f, self))

    @classmethod
    def pure(cls, x):
        return cls((x,))

    def then(self, f):
        return ArrayList(ft.reduce(lambda y, x: it.chain(y, f(x)), self, []))

    
        
@multimethod
def then(m, f):
    return type_dispatch(m, f)

@method(then, Monad)
def then(m, f):
    return m.then(f)

@method(then, Iterable)
def then(m, f):
    return it.chain.from_iterable(map(f, m))
    
    
@multimethod
def fmap(f, g):
    """Multimethod for 'fmap' functor operation"""
    return type_dispatch(g, f)

@method(fmap, Functor)
def fmap(f, g):
    return g.fmap(f)

@method(fmap, Iterable)
def fmap(f,g):
    return map(f, g)

@multimethod
def ap(f, g):
    """Multimethod for 'ap' applicative operation"""
    return type_dispatch(f, g)

@method(ap, Applicative, Applicative)
def ap(f,g):
    return f.ap(g)

@method(ap, Iterable, Iterable)
def ap(f,g):
    return (ff(gx) for ff in f for gx in g)


@multimethod
def join(m):
    return type_dispatch(m)

@method(join, Monad)
def join(m):
    return m.join()
    
@method(join, Iterable)
def join(i):
    return it.chain.from_iterable(i)
