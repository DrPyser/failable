from abc import (ABCMeta, abstractmethod, ABC)
from collections.abc import Iterable
import itertools as it
import functools as ft
import operator as op
from ..basics import *
from ..multimethods import (multimethod, method, Type)


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
    def then(self, f):
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

    def then(self, f):
        return ArrayList(ft.reduce(lambda y, x: it.chain(y, f(x)), self, []))

    
        
@multimethod
def then(m, f):
    return Type

@method(then, Monad)
def then(m, f):
    return m.then(f)

@method(then, Iterable)
def then(m, f):
    return it.chain.from_iterable(map(f, m))
    
    
@multimethod
def fmap(f, g):
    """Multimethod for 'fmap' functor operation"""
    return Type

@method(fmap, Functor)
def fmap(f, g):
    return g.fmap(f)

@method(fmap, Iterable)
def fmap(f,g):
    return map(f, g)

@multimethod
def ap(f, g):
    """Multimethod for 'ap' applicative operation"""
    return Type

@method(ap, Applicative, Applicative)
def ap(f,g):
    return f.ap(g)

@method(ap, Iterable, Iterable)
def ap(f,g):
    return (ff(gx) for ff in f for gx in g)


@multimethod
def join(m):
    return Type

@method(join, Monad)
def join(m):
    return m.join()
    
@method(join, Iterable)
def join(i):
    return it.chain.from_iterable(i)
