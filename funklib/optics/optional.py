import abc
import typing
from typing import Generic, Callable
from funklib.datatypes.option import Option, Some, Nothing
import types

S = typing.TypeVar("S")
A = typing.TypeVar("A")
B = typing.TypeVar("B")


class Optional(abc.ABC, Generic[S, A]):
    @abc.abstractmethod
    def modify(self, f: Callable[[A], A]) -> Callable[[S], S]: pass

    def set(self, a: A) -> Callable[[S], S]:
        return self.modify(lambda _: a)
    
    @abc.abstractmethod
    def try_get(self, s: S) -> Option[A]: pass

