from collections import Iterable
from functools import wraps

class Stream(Iterable):
    def __init__(self, iterable):
        self.iterable = iterable

    def __iter__(self):
        return iter(self.iterable)
    
    def map(self, f):
        return Stream(f(x) for x in self)

    def flatmap(self, f):
        return Stream(y for x in self for y in f(x))

    def filter(self, f):
        return Stream(x for x in self if f(x))


def stream(g):
    @wraps(g)
    def wrapper(*args, **kwargs):
        return Stream(g(*args, **kwargs))
    return wrapper
