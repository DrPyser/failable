from abc import (ABC, ABCMeta, abstractmethod)
from typing import *
from itertools import (tee,)
from datatypes.functionals import Monad

def is_none(x):
    return x is None

def is_not_none(x):
    return x is not None


class failable(Monad, tuple):
    def __new__(cls, x):
        return tuple.__new__(cls, (x,))

    @property
    def value(self):
        return self[0]
    
    @abstractmethod
    def is_failure(self):
        """Returns True if self is a failure,
        and False if self is a success"""
        pass

    @abstractmethod
    def is_success(self):
        """Returns True if self is a success,
        and False if self is a failure"""
        pass

    @abstractmethod
    def catch(self, f):
        """Transforms a failure into a success
        by applying the given function on the failure value"""
        pass

    @abstractmethod
    def change_error(self, f):
        """Transforms the error value"""
        pass

    @abstractmethod
    def throw(self, exnf):
        """If self is a failure, raise an exception 
        by applying provided function on error value"""
        pass


    @classmethod
    def pure(cls, x):
        return success(x)

    @classmethod
    def fail(cls, e):
        return failure(e)

    @staticmethod
    def collect(failables):
        """Try and collect all success values into one,
        or return the first fail if any"""
        (failables, failables2) = tee(failables)
        if any(x.is_failure() for x in failables):
            return next(x for x in failables2 if x.is_failure())
        else:
            return success(tuple(x.value for x in failables2))


    @staticmethod
    def collect_all(failables):
        """Try and collect all success values into one,
        or returns a fail containing all failure values"""
        (failables, failables2) = tee(failables)
        if any(x.is_failure() for x in failables):
            return failure(tuple(x.value for x in failables2 if x.is_failure()))
        else:
            return success(tuple(x.value for x in failables2))

    @staticmethod
    def successes(failables):
        """Filter that return """
        return (x for x in failables if x.is_success())

    @staticmethod
    def failures(failables):
        return (x for x in failables if x.is_failure())

    @staticmethod
    def attempt(exns, f, *args, **kwargs):
        """Wraps result of function in a success, 
        catching specified exceptions into a failure"""
        try:
            return success(f(*args, **kwargs))
        except exns as ex:
            return failure(ex)

    @staticmethod        
    def validate(pred, value):
        """Wrap value in success if pred is true
        and failure otherwise"""
        if pred(value):
            return success(value)
        else:
            return failure(value)

    @staticmethod        
    def invalidate(pred, value):
        """Wrap value in failure if pred is true
        and success otherwise"""
        if pred(value):
            return failure(value)
        else:
            return success(value)

    @staticmethod
    def from_none(value):
        if value is None:
            return failure(None)
        else:
            return success(value)

    @staticmethod
    def from_truthiness(value):
        if value:
            return success(value)
        else:
            return failure(value)    

        
class failure(failable):
    def is_failure(self):
        return True

    def is_success(self):
        return False

    def then(self, f):
        return self

    def catch(self, f):
        return success(f(self.value))

    def fmap(self, f):
        return self
    
    def change_error(self, f):
        return fail(f(self.value))

    def throw(self, exnf):
        raise exnf(self.value)

    def __repr__(self):
        return "failure({!r})".format(self.value)

    def __rshift(self, other):
        return self

    def __add__(self, other):
        if isinstance(other, failure):
            return failure(self.value + other.value)
        elif isinstance(other, success):
            return self
        else:
            raise TypeError("unsupported operand type(s) for +: '{}' and '{}'".format(type(self).__name__, type(other).__name__))

    def __iter__(self):
        while False:
            yield None
        return self.value
    
class success(failable):
    def is_failure(self):
        return False

    def is_success(self):
        return True

    def then(self, f):
        return f(self.value)

    def catch(self, f):
        return self

    def fmap(self, f):
        return success(f(self.value))

    def change_error(self, f):
        return self

    def throw(self, exnf):
        return self

    def __repr__(self):
        return "success({!r})".format(self.value)

    def __rshift__(self, other):
        return other

    def __add__(self, other):
        if isinstance(other, success):
            return success(self.value + other.value)
        elif isinstance(other, failure):
            return other
        else:
            raise TypeError("unsupported operand type(s) for +: '{}' and '{}'".format(type(self).__name__, type(other).__name__))
