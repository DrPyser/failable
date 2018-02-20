from abc import (ABC, ABCMeta, abstractmethod)
#from typing import *
from itertools import (tee,)
from .adt import data
from ..currying import curry
from .functionals import Monad

def is_none(x):
    return x is None

def is_not_none(x):
    return x is not None

@Monad.register
class Failable(data):
    
    @abstractmethod
    def is_failure(self):
        """Returns True if self is a Failure,
        and False if self is a Success"""
        pass

    @abstractmethod
    def is_success(self):
        """Returns True if self is a Success,
        and False if self is a Failure"""
        pass

    @abstractmethod
    def catch(self, f):
        """Transforms a Failure into a Success
        by applying the given function on the Failure value"""
        pass

    @abstractmethod
    def change_error(self, f):
        """Transforms the error value"""
        pass

    @abstractmethod
    def throw(self, exnf):
        """If self is a Failure, raise an exception 
        by applying provided function on error value"""
        pass

    @abstractmethod
    def either(self, succeed, fail):
        """Handle both success and failure using provided functions"""
        pass
    
    @classmethod
    def pure(cls, x):
        return Success(x)

    @classmethod
    def fail(cls, e):
        return Failure(e)

    @staticmethod
    def collect(failables):
        """Try and collect all Success values into one,
        or return the first fail if any"""
        (failables, failables2) = tee(failables)
        if any(x.is_failure() for x in failables):
            return next(x for x in failables2 if x.is_failure())
        else:
            return Success(tuple(x.value for x in failables2))


    @staticmethod
    def collect_all(failables):
        """Try and collect all Success values into one,
        or returns a fail containing all Failure values"""
        (failables, failables2) = tee(failables)
        if any(x.is_failure() for x in failables):
            return Failure(tuple(x.value for x in failables2 if x.is_failure()))
        else:
            return Success(tuple(x.value for x in failables2))

    @staticmethod
    def successes(failables):
        """Filter that return """
        return (x for x in failables if x.is_success())

    @staticmethod
    def failures(failables):
        return (x for x in failables if x.is_failure())

    @staticmethod
    @curry(2, True)
    def failable_catch(exns, f, *args, **kwargs):
        """Wraps result of function in a Success, 
        catching specified exceptions into a Failure"""
        try:
            return Success(f(*args, **kwargs))
        except exns as ex:
            return Failure(ex)

    @staticmethod        
    def validate(pred, value):
        """Wrap value in Success if pred is true
        and Failure otherwise"""
        if pred(value):
            return Success(value)
        else:
            return Failure(value)

    @staticmethod        
    def invalidate(pred, value):
        """Wrap value in Failure if pred is true
        and Success otherwise"""
        if pred(value):
            return Failure(value)
        else:
            return Success(value)

    @staticmethod
    def from_none(value):
        if value is None:
            return Failure(None)
        else:
            return Success(value)

    @staticmethod
    def from_truthiness(value):
        if value:
            return Success(value)
        else:
            return Failure(value)

    

        
class Failure(Failable):
    _fields = ("value",)

    def is_failure(self):
        return True

    def is_success(self):
        return False

    def then(self, f):
        return self

    def catch(self, f):
        return Success(f(self.value))

    def fmap(self, f):
        return self
    
    def change_error(self, f):
        return Failure(f(self.value))

    def throw(self, exnf):
        raise exnf(self.value)

    def either(self, succeed, fail):
        return fail(self.value)

    def __repr__(self):
        return "Failure({!r})".format(self.value)

    def __rshift__(self, other):
        return self

    def __add__(self, other):
        if isinstance(other, Failure):
            return Failure(self.value + other.value)
        elif isinstance(other, Success):
            return self
        else:
            raise TypeError("unsupported operand type(s) for +: '{}' and '{}'".format(type(self).__name__, type(other).__name__))

    def __iter__(self):
        while False:
            yield None
        return self.value
    
class Success(Failable):
    _fields = ("value",)
    
    def is_failure(self):
        return False

    def is_success(self):
        return True

    def then(self, f):
        return f(self.value)

    def catch(self, f):
        return self

    def fmap(self, f):
        return Success(f(self.value))

    def change_error(self, f):
        return self

    def throw(self, exnf):
        return self

    def either(self, succeed, fail):
        return succeed(self.value)

    def __repr__(self):
        return "Success({!r})".format(self.value)

    def __rshift__(self, other):
        return other

    def __add__(self, other):
        if isinstance(other, Success):
            return Success(self.value + other.value)
        elif isinstance(other, Failure):
            return other
        else:
            raise TypeError("unsupported operand type(s) for +: '{}' and '{}'".format(type(self).__name__, type(other).__name__))
