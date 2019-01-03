"""
This module defines ABCs for common functional concepts
"""

import abc
from typing import Callable, Generic
import typing
from funklib.core.prelude import identity


A = typing.TypeVar("A")
B = typing.TypeVar("B")


class Functor(abc.ABC, Generic[A]):
    @abc.abstractmethod
    def map(self, f: Callable[[A], B]) -> "Functor[B]": pass


# alias
Mappable = Functor


class Filterable(abc.ABC, Generic[A]):
    @abc.abstractmethod
    def filter(self, f: Callable[[A], bool]) -> "Filterable[A]": pass


class Applicative(Functor[A]):
    @classmethod
    @abc.abstractmethod
    def pure(cls, x: A) -> "Applicative[A]": pass

    @abc.abstractmethod
    def apply(
        self: "Applicative[Callable[[A], B]]",
        other: "Applicative[A]"
    ) -> "Applicative[B]": pass

    def map(self, f):
        return self.pure(f).ap(self)


class Monad(Applicative[A]):
    @abc.abstractmethod
    def then(self, f: Callable[[A], "Monad[B]"]) -> "Monad[B]": pass

    @abc.abstractmethod
    def flatten(self: "Monad[Monad[A]]") -> "Monad[A]": pass


def applicative_then(m: Monad[A], f: Callable[[A], Monad[B]]) -> Monad[B]:
    """Implementation of Monad.then for applicatives with a Monad.flatten implementation."""
    return m.pure(f).apply(m).flatten()


def default_flatten(m: Monad[Monad[A]]) -> Monad[A]:
    return m.then(identity)


def monad_apply(mf: Monad[Callable[[A], B]], ma: Monad[A]) -> Monad[B]:
    """Implementation of Applicative.apply for functors with Monad.then implementation."""
    return mf.then(ma.map)
    
