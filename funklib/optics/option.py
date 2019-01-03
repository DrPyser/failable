import abc
from typing import Generic, Union, Callable
import typing
from utils import singleton
from collections.abc import Iterable

T = typing.TypeVar("T")
A = typing.TypeVar("A")


class Option(abc.ABC, Generic[T], Iterable):
    @abc.abstractmethod
    def get(self, default: A) -> Union[T, A]: pass
    
    @abc.abstractmethod
    def then(self, f: Callable[[T], "Option[A]"]) -> "Option[A]": pass
    
    @abc.abstractmethod
    def map(self, f: Callable[[T], A]) -> "Option[A]": pass

    @abc.abstractmethod
    def filter(self, f: Callable[[A], bool]) -> "Option[A]": pass
    
    
class Some(tuple, Option):
    def __new__(cls, value):
        return tuple.__new__(cls, (value,))

    @property
    def value(self):
        return self[0]

    def get(self, default=None):
        return self[0]

    def then(self, f):
        return f(self[0])

    def map(self, f):
        return Some(f(self[0]))

    def __repr__(self):
        return "Some({!r})".format(self[0])
    
    
@singleton()
class Nothing(tuple, Option):
    def __new__(cls):
        return tuple.__new__(cls, ())

    def get(self, default=None):
        return default

    def then(self, f):
        return self

    def map(self, f):
        return self

    def __repr__(self):
        return "Nothing"
