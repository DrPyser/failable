from operator import methodcaller, attrgetter, itemgetter
from functools import partial
from funklib.basics import flatmap
from collections.abc import Sequence, Mapping
import abc

def pluck(obj, path):
    t = obj
    for p in path:
        t = p(t)
    else:
        return t


class Path(abc.ABC):
    def get(self, obj, default):
        """Follow the path and 
        return the value at the end, 
        or the 'default' argument if"""
        pass

    def set(self, obj, value):
        """
        Follow the path and set the 
        pointed location to the provided value
        """
        pass

    def from_string(cls, path):
        """
        Produce a path object from a string encoding
        """
        pass

    
@Path.register
class JSONPath(tuple):
    def __new__(cls, *components):
        return tuple.__new__(cls, components)

    def get(self, obj, default=None):
        t = obj
        for c in self:
            if isinstance(t, Sequence):
                try:
                    t = t[int(c)]
                except IndexError:
                    return default
            elif isinstance(t, Mapping):
                try:
                    t = t[c]
                except KeyError:
                    return default
            else:
                raise TypeError("Pointer component {!r} cannot be followed through object {!r} of type {!r}".format(
                    c, t, type(t).__name__
                ))
        else:
            return t

    def set(self, obj, value):
        t = obj
        for c in self[:-1]:
            if isinstance(t, Sequence):
                t = t[int(c)]
            elif isinstance(t, Mapping):
                t = t[c]
            else:
                raise TypeError("Pointer component {!r} cannot be followed through object {!r} of type {!r}".format(
                    c, t, type(t).__name__
                ))
        else:            
            if isinstance(t, Sequence):
                t[int(self[-1])] = value
            elif isinstance(t, Mapping):
                t[self[-1]] = value
            else:
                raise TypeError("Pointer component {!r} cannot be followed through object {!r} of type {!r}".format(
                    self[-1], t, type(t).__name__
                ))
                
    
    @classmethod
    def from_string(cls, path):
        if len(path) == 0:
            return cls()
        elif path[0] == "/":
            cs = path[1:].split("/")
            cs1 = map(methodcaller("replace", "~1", "/"), cs)
            cs2 = map(methodcaller("replace", "~0", "~"), cs1)
            return cls(*cs2)
        else:
            raise ValueError("A path must beging with a slash, or be an empty string")

@Path.register
class AttrPath(tuple):
    def __new__(cls, *components):
        return tuple.__new__(cls, components)
    
    def get(self, obj, default=None):
        t = obj
        for c in self:
            try:
                t = getattr(t, c)
            except AttributeError:
                return default
        else:
            return t

    def set(self, obj, value):
        if len(self) > 0:
            t = obj
            for c in self[:-1]:
                t = getattr(t, c)
            else:
                setattr(t, self[-1], value)

    
    @classmethod
    def from_string(cls, path):
        if len(path) == 0:
            return cls()
        else:
            cs = path[1:].split(".")
            return cls(*cs)
    
