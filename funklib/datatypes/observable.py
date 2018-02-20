import abc
from typing import Any

class Observable(abc.ABC):
    @abc.abstractmethod
    def subscribe(
            self,
            observer=None,
            on_next=None,
            on_error=None,
            on_complete=None): pass

    

class Observer(abc.ABC):
    @abc.abstractmethod
    def on_next(self, x: Any): pass

    @abc.abstractmethod
    def on_error(self, e: Exception): pass

    @abc.abstractmethod
    def on_complete(self): pass



def throw(e):
    raise e

def identity(x):
    return x

def none(): pass


class GenericObserver(Observer):
    __slots__ = ["on_next", "on_error", "on_complete"]
    def __init__(self, on_next, on_error=throw, on_complete=none):
        self.on_next = on_next
        self.on_error = on_error
        self.on_complete = on_complete
    

class Single(abc.ABC):
    @abc.abstractmethod
    def subscribe(on_success, on_error): pass
    
    

class IdentitySingle(Single):
    __slots__ = ["_value", "_subscribers"]
    def __init__(self, value):
        self._value = value
        self._subscribers = []

    def subscribe(self, on_success, on_error):
        self._subscribers.append(on_success, on_error)

    def __next__(self, default=None):
        for (success, error) in self._subscribers:
            success(self._value)
        return self._value
