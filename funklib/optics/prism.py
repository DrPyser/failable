import abc
import typing
from typing import Generic, Callable, Any
import functools as ft
import operator as op
from funklib.datatypes.option import Option, Some, Nothing
from funklib.core.prelude import singleton
import types


S = typing.TypeVar("S")
A = typing.TypeVar("A")
B = typing.TypeVar("B")


class Prism(abc.ABC, Generic[S, A]):
    __slots__ = ()

    @abc.abstractmethod
    def recover(self, a: A) -> S: pass

    @abc.abstractmethod
    def try_get(self, s: S) -> Option[A]: pass

    def try_modify(self, f: Callable[[A], A]) -> Callable[[S], Option[S]]:
        recover = self.recover
        try_get = self.try_get
        return lambda s: try_get(s).map(lambda a: recover(f(a)))

    def __call__(self, a: A):
        return self.recover(a)

    def then(self, prism):
        return ComposedPrism(
            *self if isinstance(self, ComposedPrism) else self,
            *prism if isinstance(self, prism) else prism
        )

    @classmethod
    def from_functions(
            cls,
            try_get: Callable[[S], Option[A]],
            recover: Callable[[A], S],
            modify: Callable[[Callable[[A], A]], Callable[[S], Option[S]]]=None,
            name=None) -> "Prism[S, A]":
        def update_ns(ns):
            ns["__slots__"] = ()
            ns["try_get"] = staticmethod(try_get)
            ns["recover"] = staticmethod(recover)
            ns["__repr__"] = lambda self: type(self).__name__
            if modify is not None:
                ns["modify"] = staticmethod(modify)
       
        # create new type for implementation, but directly return instance, like a singleton
        return types.new_class(
            name or "Prism.from_functions(try_get={}, recover={}, modify={})".format(try_get, recover, modify),
            (Prism,),
            exec_body=update_ns
        )()

    @classmethod
    def from_partial(cls, partial_get: Callable[[S], A], recover: Callable[[A], S], modify=None, name=None) -> "Prism[S, A]":
        def try_get(s):
            try:
                a = partial_get(s)
            except (TypeError, ValueError):
                return Nothing
            else:
                return Some(a)

        def update_ns(ns):
            ns["__slots__"] = ()
            ns["try_get"] = staticmethod(try_get)
            ns["recover"] = staticmethod(recover)
            ns["__repr__"] = lambda self: type(self).__name__
            if modify is not None:
                ns["modify"] = staticmethod(modify)
        
        # create new type for implementation, but directly return instance, like a singleton
        return types.new_class(
            name or "Prism.from_partial(try_get={}, recover={}, modify={})".format(try_get, recover, modify),
            (Prism,),
            exec_body=update_ns
        )()


class ComposedPrism(tuple, Prism[S, A]):
    def __new__(cls, *prisms):
        return tuple.__new__(cls, prisms)

    def try_get(self, s: S):
        return ft.reduce(lambda x, p: x.then(p.try_get), self, Some(s))

    def recover(self, a: A):
        return ft.reduce(lambda x, p: p.recover(x), reverse(self), a)


@singleton()
class None_(Prism[Any, None]):
    __slots__ = ()
    
    def try_get(self, s):
        return Some(s) if s is None else Nothing

    def recover(self, a):
        return a


Nothing_: Prism[Any, Option] = Prism.from_functions(
    try_get=lambda s: Some(s) if s is Nothing else Nothing,
    recover=lambda a: Nothing
)


Some_: Prism[Option[A], A] = Prism.from_functions(
    try_get=lambda s: s,
    recover=Some
)


def attribute(attr: str, constructor: Callable[[A], S]) -> Prism[S, A]:
    """
    Prism for objects exposing an attribute
    """
    return Prism.from_functions(
        try_get=lambda s: Some(getattr(s, attr)) if hasattr(s, attr) else Nothing,
        recover=constructor
    )


FormattedInt = Prism.from_partial(
    partial_get=int,
    recover=str
)
