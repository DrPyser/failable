from abc import ABCMeta
from operator import itemgetter
from cachetools import LRUCache
from ..patmat import MatchFailure

def tuple_itemgetter(i):
    def tuple_itemgetter2(x):
        return tuple.__getitem__(x, i)
    return tuple_itemgetter2

class ADTMeta(ABCMeta):
    """Metaclass for ADT-like types"""
    def __new__(cls, name, bases, attrs, cached=False, maxsize=100, **kwargs):
        if not (tuple in bases or any(issubclass(c, tuple) for c in bases)):
            bases = bases + (tuple,)
        attrs["__slots__"] = ()
        return super(ADTMeta, cls).__new__(cls, name, bases, attrs, **kwargs)

    def __init__(cls, name, bases, attrs, functoid=True, cached=False, maxsize=100, **kwargs):
        super().__init__(name, bases, attrs, **kwargs)
        annots = tuple(getattr(cls, "__annotations__", {}))        
        
        cls._fields = fields = tuple(cls._fields) if "_fields" in vars(cls)\
            else tuple(annots) or tuple(getattr(cls, "_fields", ()))

        for i, field in enumerate(fields):
            setattr(cls, field, property(tuple_itemgetter(i)))
        cls._cache = LRUCache(maxsize=(1 if len(fields) == 0 else maxsize)) if cached else None
        cls._cached = cached

        # if functoid:
        #     # print(name, cls)
        #     exclude = frozenset(getattr(cls, "__functoid_exclude__", ())).union(dir(object))
        #     # print(exclude)
        #     #print(frozenset(dir(cls)))
        #     include = frozenset(attrs.get("__functoid_include__")) if "__functoid_include__" in attrs \
        #         else frozenset(getattr(cls, "__functoid_include__", ())).union(attrs)
        #     # print(include)
        #     cls.__functoid_exclude__ = exclude
        #     cls.__functoid_include__ = include - exclude
        # else:
        #     cls.__functoid_include__ = cls.__functoid_exclude__ = frozenset(())
        
            
    
class data(tuple, metaclass=ADTMeta):
    def __new__(cls, *args, **kwargs):
        if len(kwargs) + len(args) != len(cls._fields):
            raise TypeError(("Wrong number of arguments given to constructor of class {}."
                             " Expected {}, got {}.").format(cls.__name__,
                                                             len(cls._fields),
                                                             len(args)+len(kwargs)))
        else:
            values = tuple(args[i] if i < len(args) else kwargs[field]
                           for (i,field) in enumerate(cls._fields))
            if cls._cached:
                cached = cls._cache.get(values, None)
                if cached is None:
                    new = cls._cache[values] = super(data, cls).__new__(cls, values)
                    return new
                else:
                    return cached
            else:
                return super(data, cls).__new__(cls, values)

    def __repr__(self):
        return "{}({})".format(type(self).__name__, ",".join(map(str, self)))

    @classmethod
    def __match__(cls, x):
        if isinstance(x, cls):
            return tuple.__iter__(x)
        else:
            raise MatchFailure()
