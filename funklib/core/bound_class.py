"""
bound class

This module implement the bound class pattern.
A class can be associated with a context by subclassing the class for each context.
The context is then accessible in the subclasses through a class-level property, 
or a function.
"""

import functools
import types
import operator as op
from typing import Any, Type
from funklib.core.class_utils import subclass, class_property


class BoundClass:
    """
    Descriptor to wrap a class 
    that will be bound to the context 
    in which the descriptor is installed.
    A subclass of the unbound class is created and cached on
    attribute access, with the context available 
    through a __bound_context__ attribute.
    """
    def __init__(self, unbound):
        self.unbound = unbound
        self._cache = {}

    def __get__(self, obj, owner=None):
        context = obj or owner
        if context not in self._cache:
            bound = bind(self.unbound, context)
            self._cache[context] = bound
        else:
            bound = self._cache[context]
        return bound

    
bound = BoundClass


def get_bound_context(obj, default=None):
    return getattr(obj, "__bound_context__", default)


def bind(unbound: Type, context: Any):
    """
    Create a bound class by subclassing it for the given context
    """
    name = getattr(context, "__name__", None) or type(context).__name__ + f"_{id(context)}"
    def add_context(ns):
        ns["__bound_context__"] = context
        ns["context"] = class_property(op.attrgetter("__bound_context__"))
    return subclass(unbound, unbound.__name__ + "bound_to_" + name, exec_body=add_context)



