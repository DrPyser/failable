from abc import (ABCMeta, abstractmethod)
from typing import *
from itertools import (tee,)


def is_none(x):
    return x is None

def is_not_none(x):
    return x is not None



class failable(tuple, metaclass=ABCMeta):
    def __new__(cls, x):
        return super().__new__(cls, (x,))

    @property
    def value(self):
        return self[0]
    
    @abstractmethod
    def is_failure(self):
        pass

    @abstractmethod
    def is_success(self):
        pass

    @abstractmethod
    def then(self, f):
        pass

    @abstractmethod
    def catch(self, f):
        pass

    @abstractmethod
    def change(self, f):
        pass

    @abstractmethod
    def change_error(self, f):
        pass

    @abstractmethod
    def throw(self, exnf):
        pass
    

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
        return tuple(x for x in failables if x.is_success())

    @staticmethod
    def failures(failables):
        return tuple(x for x in failables if x.is_failure())

    @staticmethod
    def attempt(exns, f, *args, **kwargs):
        try:
            return success(f(*args, **kwargs))
        except exns as ex:
            return failure(ex)

    @staticmethod        
    def validate(pred, value):
        if pred(value):
            return success(value)
        else:
            return failure(value)

    @staticmethod        
    def invalidate(pred, value):
        if pred(value):
            return failure(value)
        else:
            return success(value)


        

class failure(failable):
    def is_failure(self):
        return True

    def is_success(self):
        return False

    def then(self, f):
        return self

    def catch(self, f):
        return success(f(self.value))

    def change_error(self, f):
        return fail(f(self.value))

    def throw(self, exnf):
        raise exnf(self.value)

    def __repr__(self):
        return "failure({!r})".format(self.value)

    
class success(failable):
    def is_failure(self):
        return False

    def is_success(self):
        return True

    def then(self, f):
        return f(self.value)

    def catch(self, f):
        return self

    def change(self, f):
        return success(f(self.value))

    def change_error(self, f):
        return self

    def throw(self, exnf):
        return self

    def __repr__(self):
        return "success({!r})".format(self.value)
