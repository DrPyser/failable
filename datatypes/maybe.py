from abc import abstractmethod
from itertools import tee
from ..currying import curry
from .adt import data
from .functionals import (Monad,)
from typing import Any

@Monad.register
class Maybe(data):
    """Result of a partial computation(computation not defined onn all its inputs)"""
#    __functoid_include__ = locals()
    @abstractmethod
    def is_just(self):
        raise NotImplementedError()

    @abstractmethod
    def is_nothing(self):
        raise NotImplementedError()

    @abstractmethod
    def from_just(self):
        raise NotImplementedError()

    @abstractmethod
    def __rshift__(self, other):
        raise NotImplementedError()

    @abstractmethod
    def maybe(self, something, nothing):
        pass
    
    @classmethod
    def pure(cls, x):
        return Just(x)

    @classmethod
    def fail(cls, x):
        return Nothing()

    @staticmethod
    def from_none(value):
        if value is None:
            return Nothing()
        else:
            return Just(value)

    @staticmethod
    def from_truthiness(value):
        if value:
            return Just(value)
        else:
            return Nothing()

    @staticmethod
    def validate(pred, value):
        if pred(value):
            return Just(value)
        else:
            return Nothing()

    @staticmethod
    def invalidate(pred, value):
        if not pred(value):
            return Just(value)
        else:
            return Nothing()

    @staticmethod
    @curry(2, True)
    def catch(exns, f, *args, **kwargs):
        try:
            return Just(f(*args, **kwargs))
        except exns:
            return Nothing()

    def collect(maybes):
        (maybes, maybes2) = tee(maybes)
        if any(x.is_nothing() for x in maybes):
            return Nothing()
        else:
            return Just(tuple(x.value for x in maybes2))
        
        
class Nothing(Maybe, cached=True):
    _fields = ()

    def is_just(self):
        return False
    
    def is_nothing(self):
        return True
    
    def __rshift__(self, other):
        return self
    
    def then(self, f):
        return self

    def fmap(self, f):
        return self

    def ap(self, other):
        return self

    def join(self):
        return self
        
    def from_just(self, default=None):
        return default

    def __repr__(self):
        return "Nothing"

    def __add__(self, other):
        return self

    def __rshift__(self, other):
        return self

    def maybe(self, something, nothing):
        return nothing()

class Just(Maybe):
    value: Any
    
    def is_just(self):
        return True
    
    def is_nothing(self):
        return False

    def fmap(self, f):
        return Just(f(self.value))

    def then(self, f):
        return f(self.value)

    def ap(self, other):
        return other.fmap(self.value)

    def from_just(self, default=None):
        return self.value

    def __rshift__(self, other):
        return other

    def __repr__(self):
        return "Just({!r})".format(self.value)

    def __add__(self, other):
        if other.is_just():
            return Just(self.value + other.value)
        else:
            return other

    def maybe(self, something, nothing):
        return something(self.value)

if __name__ == "__main__":
    @Maybe.catch((Exception,))
    def test(x):
        if x:
            return x
        else:
            raise Exception("Oh no!")
        
