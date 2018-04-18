import abc
import functools as ft

class Reducible(abc.ABC):
    @abc.abstractmethod
    def reduce(self, f, *args):
        pass

old_list = list

class list(old_list):
    __slots__ = ()

    def reduce(self, f, *args):
        if len(self) == 0:
            return args[0] if args else f()
        else:
            return ft.reduce(f, self, args[0]) if args else ft.reduce(f, self)



class ReduceIter(Reducible):
    def __init__(self, iterable):
        self.iterable = iterable

    def reduce(self, f, *args):
        return ft.reduce(f, self.iterable, *args) if args else\
            ft.reduce(f, self.iterable, f())
        
