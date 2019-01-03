import abc
from typing import Generic, Union, Callable
import typing
from funklib.core.prelude import singleton
from collections.abc import Iterable
from funklib.datatypes.abc import Monad, Filterable, default_flatten, monad_apply


T = typing.TypeVar("T")
A = typing.TypeVar("A")
B = typing.TypeVar("B")


class Option(Monad[A], Iterable, Filterable[A]):
    @abc.abstractmethod
    def get(self, default: B) -> Union[A, B]: pass
    
    flatten = default_flatten
    apply = monad_apply


class Some(tuple, Option[T]):
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

    def __or__(self, other):
        return self

    def __and__(self, other):
        return other

    def __repr__(self):
        return "Some({!r})".format(self[0])


@singleton()
class Nothing(tuple, Option[T]):
    def __new__(cls):
        return tuple.__new__(cls, ())

    def get(self, default=None):
        return default

    def then(self, f):
        return self

    def map(self, f):
        return self

    def __or__(self, other):
        return other

    def __and__(self, other):
        return self
    
    def __repr__(self):
        return "Nothing"
