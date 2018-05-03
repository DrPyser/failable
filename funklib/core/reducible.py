import abc
import functools as ft
from collections import Iterable
from funklib.multimethods import multimethod, Type
import funklib.core.prelude as prelude

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


class Reducer:
    __slots__ = ["step", "init", "complete"]
    def __init__(self, step, init=None, complete=None):
        self.step = step.step if isinstance(step, Reducer) else step
        self.init = init or (step.init if isinstance(step, Reducer) else step)
        self.complete = complete or (step.complete if isinstance(step, Reducer) else prelude.identity)

    def __call__(self, *args):
        if len(args) == 0:
            return self.init()
        elif len(args) == 1:
            return self.complete(*args)
        else:
            return self.step(*args)
        
    

class Reduced(Exception):
    __slots__ = ["value"]
    def __init__(self, value):
        super().__init__(value)
        self.value = value

    def __repr__(self):
        return "Reduced({})".format(self.value)

    

def with_reduced(f):
    @ft.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Reduced as ex:
            return ex.value
    return wrapper

    
def reduce(rf, reducible, init=prelude._missing):
    try:
        if isinstance(reducible, Iterable):
            return rf(ft.reduce(rf, reducible, init if init is not prelude._missing else rf()))
        elif isinstance(reducible, Reducible) or hasattr(reducible, "reduce"):
            return rf(reducible.reduce(rf, init if init is not prelude._missing else rf()))
    except (StopIteration, Reduced) as ex:
        return rf(ex.value)
        
def appender(acc, x):
    acc.append(x)
    return acc


def extender(acc, x):
    acc.extend(x)
    return acc

def adder(acc, x):
    return acc + x

list_appender = Reducer(step=appender, init=list)
list_extender = Reducer(step=extender, init=list)
tuple_adder = Reducer(step=adder, init=lambda: ())
number_adder = Reducer(step=adder, init=lambda: 0)
string_adder = Reducer(step=adder, init=lambda: "")
