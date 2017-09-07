from datatypes.functionals import (Monad, FunctoidalSingletonType)
from currying import curry
import basics
from abc import abstractmethod


class maybe(Monad, tuple):
    """Result of a partial computation"""

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

    @classmethod
    def pure(cls, x):
        return just(x)

    @classmethod
    def fail(cls, x):
        return nothing()

    @staticmethod
    def from_none(value):
        if value is None:
            return nothing()
        else:
            return just(value)

    @staticmethod
    def from_truthiness(value):
        if value:
            return just(value)
        else:
            return nothing()

    @staticmethod
    def validate(pred, value):
        if pred(value):
            return just(value)
        else:
            return nothing()

    @staticmethod
    def invalidate(pred, value):
        if not pred(value):
            return just(value)
        else:
            return nothing()

    @staticmethod
    @curry(2, True)
    def catch(exns, f, *args, **kwargs):
        try:
            return just(f(*args, **kwargs))
        except exns:
            return nothing()

        
class nothing(maybe, metaclass=FunctoidalSingletonType):
    __slots__ = []
    def __new__(cls):
        return super().__new__(cls)
    
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

    def __repr__(self):
        return "nothing"
        
    def from_just(self, default=None):
        return default


class just(maybe):
    def __new__(cls, x):
        return super().__new__(cls, (x,))

    def is_just(self):
        return True
    
    def is_nothing(self):
        return False

    @property
    def value(self):
        return self[0]

    def fmap(self, f):
        return just(f(self.value))

    def then(self, f):
        return f(self.value)

    def ap(self, other):
        return other.fmap(self.value)

    def from_just(self, default=None):
        return self.value

    def __rshift__(self, other):
        return other

    def __repr__(self):
        return "just({!r})".format(self.value)
