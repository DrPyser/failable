import abc
import typing
from typing import Generic, Callable, Any
import functools as ft
import types


S = typing.TypeVar("S")
A = typing.TypeVar("A")
B = typing.TypeVar("B")


class Getter(abc.ABC, Generic[S, A]):
    @abc.abstractmethod
    def get(self, s: S) -> A:
        pass

    def then(self, getter: "Getter[A, B]") -> "Getter[S, B]":
        return ComposedGetter(
            *self if isinstance(self, ComposedGetter) else self,
            *getter if isinstance(getter, ComposedGetter) else getter
        )

    def __call__(self, s):
        return self.get(s)


class ComposedGetter(tuple, Getter[S, A]):
    def __new__(cls, *getters):
        return tuple.__new__(cls, getters)

    def get(self, s):
        return ft.reduce(lambda x, g: g.get(x), self, s)


class Setter(abc.ABC, Generic[S, A]):
    @abc.abstractmethod
    def modify(self, f: Callable[[A], A]) -> Callable[[S], S]:
        pass

    def set(self, new: A) -> Callable[[S], S]:
        return self.modify(lambda _: new)

    def then(self, setter: "Setter[A, B]") -> "Setter[S, B]":
        return ComposedSetter(
            *self if isinstance(self, ComposedSetter) else self,
            *setter if isinstance(setter, ComposedSetter) else setter
        )


class ComposedSetter(tuple, Setter[S, B]):
    def __new__(cls, *setters):
        return tuple.__new__(cls, setters)

    def modify(self, f):
        modifier = ft.reduce(lambda x, setter: setter.modify(x), reversed(self), f)
        return modifier


class Lens(abc.ABC, Generic[S, A]):
    __slots__ = ()

    @abc.abstractmethod
    def modify(self, f: Callable[[A], A]) -> Callable[[S], S]:
        pass

    def set(self, new: A) -> Callable[[S], S]:
        return self.modify(lambda _: new)

    @abc.abstractmethod
    def get(self, s: S) -> A:
        pass

    def then(self, lens: "Lens[A, B]") -> "Lens[S, B]":
        return ComposedLens(
            *self if isinstance(self, ComposedLens) else self,
            *lens if isinstance(lens, ComposedLens) else lens
        )

    @classmethod
    def from_functions(
        cls,
        get: Callable[[S], Option[A]],
        modify: Callable[[Callable[[A], A]], Callable[[S], Option[S]]],
        set: Callable[[A], Callable[[S], Option[S]]] = None,
        name=None,
    ) -> "Lens[S, A]":
        def update_ns(ns):
            ns["__slots__"] = ()
            ns["get"] = staticmethod(get)
            ns["modify"] = staticmethod(modify)
            if set is not None:
                ns["set"] = staticmethod(set)

        # create new type for implementation, but directly return instance, like a singleton
        return types.new_class(
            name
            or "Lens.from_functions(get={}, modify={})".format(get, modify),
            (Lens,),
            exec_body=update_ns,
        )()


class ComposedLens(tuple, Lens[S, B]):
    def __new__(cls, *lenses):
        return tuple.__new__(cls, lenses)

    def get(self, s):
        return ft.reduce(lambda x, g: g.get(x), self, s)

    def modify(self, f):
        modifier = ft.reduce(lambda x, lens: lens.modify(x), reversed(self), f)
        return modifier


def update_key(m, k, v):
    mm = dict(m)
    mm[k] = v
    return mm


class DictItem(Lens[dict, Any]):
    __slots__ = ["key"]

    def __init__(self, key):
        self.key = key

    def get(self, s: dict):
        return s[self.key]

    def modify(self, f):
        key = self.key
        return lambda s: update_key(s, key, f(s[key]))


class TupleItem(Lens[tuple, Any]):
    __slots__ = ["index"]

    def __init__(self, index: int):
        self.index = index

    def get(self, s):
        return s[self.index]

    def modify(self, f):
        index = self.index
        return lambda s: tuple(f(x) if i == index else x for i, x in enumerate(s))


class Attribute(Lens[Any, Any]):
    __slots__ = ["attr", "constructor"]

    def __init__(self, attr, constructor=None):
        self.attr = attr
        self.constructor = constructor

    def get(self, s):
        return getattr(s, self.attr)

    def modify(self, f):
        attr = self.attr
        cons = self.constructor
        return lambda s: cons(update_key(vars(s), attr, f(getattr(s, attr))))
