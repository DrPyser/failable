import funklib.core.prelude as prelude
from collections import namedtuple
import abc
import functools as ft

class Box:
    __slots__ = ("value",)
    def __init__(self, value):
        self.value = value

    def change(self, f):
        old = self.value
        self.value = f(self.value)
        return old

    def swap(self, v):
        old = self.value
        self.value = v
        return old
        


reduced = namedtuple("reduced", ("value",))
        
        
class Transducer:
    def __init__(self, init=None, complete=None, step=None):
        self.init = init or (lambda rf, state: rf())
        self.complete = complete or (lambda rf, result, state: rf(result))
        self.step = step or (lambda rf, acc, *args, state: rf(acc, *args))
        
    def __call__(self, step, init=None, complete=None):
        state = Box(None)
        def rf2(*args):
            if len(args) == 0:
                return self.init(init or step, state=state)
            elif len(args) == 1:
                return self.complete(complete or step, args[0], state=state)
            else:
                return self.step(step, *args, state=state)
        return rf2


def map(f):
    def step(rf, acc, *items, state=None):
        return rf(acc, f(*items))
    return Transducer(step=step)
    

def filter(pred):
    def step(rf, acc, item, state=None):
        return rf(acc, item) if pred(item) else acc
    return Transducer(step=step)


def batch(batch_size):
    def init(rf, state):
        state.swap([])
        return rf()
    def step(rf, acc, *args, state):
        for x in args:
            if len(state.value) < batch_size:
                state.value.append(x)
        if len(state.value) < batch_size:
            return acc
        else:
            return rf(acc, state.swap([]))
    def complete(rf, result, state):
        if len(state.value) > 0:
            return rf(result, state.swap(None))
    return Transducer(step=step, init=init, complete=complete)


def transduce(transducer, reducer, reducible, init=None, complete=None):
    return reducible.reduce(transducer(step=reducer, init=init, complete=complete), init)

def sequence(transducer, reducible):
    seq = []
    def step(acc, x):
        seq.append(x)
        return acc
    def complete(result):
        return result
    def init():
        return seq
    return reducible.reduce(transducer(step=step, init=init, complete=complete))

