import functools as ft
from operator import *
import cachetools as ct
from typing import GenericMeta
from .currying import curried, curry
from abc import ABCMeta, ABC

# from .functoid import Functoid

## Basic functional programming tools


def identity(x):
    return x


def const(x):
    return lambda _: x


def compose2(f, g):
    return lambda x:f(g(x))


def compose(*callables):
    return ft.reduce(compose2, callables)


def uncurry(f):
    return lambda args: f(*args)


def flip(f):
    return lambda *args, **kwargs: f(*reversed(args), **kwargs)


def singleton(*args, **kwargs):
    def decorator(f):
        return f(*args, **kwargs)
    return decorator
    
