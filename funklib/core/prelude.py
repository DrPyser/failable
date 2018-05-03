## Basic simple functional programming tools
import functools as ft
import itertools as it
import operator as op
from collections import namedtuple
from typing import TypeVar, Any, Callable, Optional, Mapping, Iterator, Iterable, Dict, Tuple, Union

T = TypeVar("T")
U = TypeVar("U")


def identity(x: T) -> T:
    return x


def const(x: T) -> Callable[..., T]:
    return lambda *args, **kwargs: x


def compose2(f: Callable, g: Callable) -> Callable:
    """Binary function composition, or `f after g`"""
    return lambda *args, **kwargs: f(g(*args, **kwargs))


def compose(*callables: Callable) -> Callable:
    """Compose functions"""
    return ft.reduce(compose2, callables)


def uncurry(f: Callable[..., T]) -> Callable[[Tuple, Optional[Mapping]], T]:
    lambda args=(),kwargs=None: f(*args, **(kwargs or {}))


def flip(f: Callable) -> Callable:
    """Return a function with the order of positional parameters 
    flipped relative to the argument function"""
    return lambda *args, **kwargs: f(*reversed(args), **kwargs)


def unit(x: T) -> Iterator[T]:
    """Yield x"""
    yield x

    
def flatmap(it: Iterable[T], f: Callable[[T], Iterable[U]]) -> Iterable[U]:
    """
    Chain iterable-producing functions
    """
    for x in it:
        yield from f(x)
    

def flatten(it: Iterable[Iterable[T]]) -> Iterable[T]:
    for x in it:
        yield from x

        
def caller(*args, **kwargs) -> Callable[[Callable[..., T]], T]:
    """Creates a function which calls its input on the arguments"""
    return lambda f: f(*args, **kwargs)

    
def singleton(*args, **kwargs):
    """Decorator which replaces a class definition
    by an instance of this class"""
    def decorator(f):
        return f(*args, **kwargs)
    return decorator


def throw(ex: Exception) -> None:
    raise ex


def thrower(excf: Callable[[Any], Exception]) -> Callable[[Any], None]:
    """Create a function that produce an exception from its argument and raises it"""
    return lambda x:throw(excf(x))


Predicate = Callable[[T], bool]

def comp(p: Predicate[T]) -> Predicate[T]:
    """Complement of a predicate"""
    return lambda x: not p(x)


def sep_by(pred: Predicate[T], iterable: Iterable[T]) -> (Iterable[T], Iterable[T]):
    """Separate an iterable's elements into two groups according to a predicate"""
    a, b = it.tee(iterable)
    return filter(pred, a), it.filterfalse(pred, b)


def split_by(pred: Predicate[T], iterable: Iterable[T]) -> (Iterable[T], Iterable[T]):
    """Split an iterable in two according to a predicate"""
    a, b = it.tee(iterable)
    return it.takewhile(pred, a), it.dropwhile(pred, b)


K, V = TypeVar("K"), TypeVar("V")

def merge_by(mappings: Iterable[Mapping[K,V]], combiner: Callable[[T, V], T]) -> Dict[K, T]:
    mappings = list(mappings)
    keys = set(it.chain.from_iterable(map(op.methodcaller("keys"), mappings)))
    return {
        k: ft.reduce(combiner, (m[k] for m in mappings if k in m))
        for k in keys
    }


def project(obj: T, keys: Iterable[str], accessor: Callable[[T, str], V]=op.getitem) -> Dict[str, V]:
    """
    Extract fields from an object into a dict
    :param accessor: function to access a field on the object
    """
    return {
        k: accessor(obj, k)
        for k in keys
    }


def get(k: K, default:T=None) -> Callable[[Mapping[K, V]], Union[V,T]]:
    return op.methodcaller("get", k, default)


def autozip(it: Iterable, f: Callable):
    return zip(it, map(f,it))


def tupleclass(*fields):
    def decorator(klass):
        struct = namedtuple(klass.__name__, tuple(fields))
        return type(klass.__name__, (*klass.__bases__, struct), dict(vars(klass)))
    return decorator


def keyfilter(pred: Predicate[K], m: Mapping[K, V]) -> Mapping[K, V]:
    return {
        k: v
        for k, v in m.items()
        if pred(k)
    }


def valfilter(pred: Predicate[V], m: Mapping[K, V]) -> Mapping[K, V]:
    return {
        k: v
        for k, v in m.items()
        if pred(v)
    }

def itemfilter(pred: Predicate[Tuple[K,V]], m: Mapping[K, V]) -> Mapping[K, V]:
    return {
        k: v
        for k, v in m.items()
        if pred((k,v))
    }

def seq(*args):
    return args[-1]


_missing = namedtuple("_missing", ())
