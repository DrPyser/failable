from abc import (ABCMeta, abstractmethod, ABC)
from collections.abc import Iterable
import itertools as it
import functools as ft
import operator as op
import typing
from funklib.basics import *
from multimethods import (multimethod, method, Type, generic)
from functools import wraps


class Functor(ABC):
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
    def flatmap(self, f):
        raise NotImplementedError()

    def fmap(self, f):
        return self.flatmap(Functoid(f).before(self.pure))

    def flatten(self):
        return self.flatmap(identity)

    def ap(self, g):
        return self.flatmap(g.fmap)

    @classmethod
    @abstractmethod
    def fail(cls, msg):
        raise NotImplementedError()

class Monoid:
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

    def flatmap(self, f):
        return ArrayList(ft.reduce(lambda y, x: it.chain(y, f(x)), self, []))


class Stream(Monad):
    """Monadic wrapper for sequences"""
    def __init__(self, iterable):
        self.data = iterable

    def __iter__(self):
        return iter(self.data)
    
    @classmethod
    def pure(cls, x):
        return (yield x)

    def flatmap(self, f):
        for x in self:
            yield from f(x)

    def fmap(self, f):
        return map(f, self)

    def flatten(self):
        return chain.from_iterable(self)    

    def fail(self, msg):
        return (yield from ())
        
@generic(pattern=Type)
def flatmap(m, f):
    pass

@method(flatmap, Monad)
def flatmap(m, f):
    return m.flatmap(f)

@method(flatmap, Iterable)
def flatmap(m, f):
    for x in m:
        yield from f(x)
    
@generic(pattern=Type)
def fmap(f, g):
    """Multimethod for 'fmap' functor operation"""
    pass

@method(fmap, Functor)
def fmap(f, g):
    return g.fmap(f)

@method(fmap, Iterable)
def fmap(f,g):
    return map(f, g)

@generic(pattern=Type)
def ap(f, g):
    """Multimethod for 'ap' applicative operation"""
    pass

@method(ap, Applicative, Applicative)
def ap(f,g):
    return f.ap(g)

@method(ap, Iterable, Iterable)
def ap(f,g):
    for ff in f:
        for gg in g:
            yield ff(gg)


@generic(pattern=Type)
def flatten(m):
    pass 

@method(flatten, Monad)
def flatten(m):
    return m.flatten()
    
@method(flatten, Iterable)
def flatten(i):
    return it.chain.from_iterable(i)
