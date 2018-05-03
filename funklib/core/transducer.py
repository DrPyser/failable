import funklib.core.functoid as functoid
from funklib.core.reducible import Reducer, reduce, Reduced, list_appender
import funklib.core.prelude as prelude
import collections
import abc
import functools as ft
import itertools as it
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
        

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
        
        
class Transducer(functoid.Functoidal):
    def __init__(self, init=None, complete=None, step=None, name=None):
        self.init = init
        self.complete = complete
        self.step = step
        self.__name__ = name
        
    def __call__(self, reducer: Reducer):
        state = Box(None)
        return Reducer(
            step=self.step(reducer, state=state) if self.step else reducer,
            init=self.init(reducer, state=state) if self.init else reducer,
            complete=self.complete(reducer, state=state) if self.complete else reducer
        )

    def before(self, f):
        return functoid.compose(f, self)

    def after(self, f):
        return functoid.compose(self, f)

    def flip(self):
        return NotImplemented

    def curry(self, *args, **kwargs):
        return NotImplemented

    def uncurry(self):
        return NotImplemented

    
def make_transducer(*args, **kwargs):
    return Transducer(*args, **kwargs)

def mapping(f):
    def step(rf, state=None):
        LOGGER.info("In map step transform")
        return lambda acc, *items: prelude.seq(LOGGER.info("In map.step"), rf(acc, f(*items)))
    return make_transducer(step=step, name="mapping({})".format(f))
    

def filtering(pred):
    def step(rf, state=None):
        LOGGER.info("In filter step")
        return lambda acc, item: prelude.seq(LOGGER.info("In filter.step"), rf(acc, item) if pred(item) else acc)
    return make_transducer(step=step, name="filtering({})".format(pred))


def batching(batch_size):
    def init(rf, state):
        LOGGER.info("batch init transform")
        return lambda: prelude.seq(LOGGER.info("In batch.init"), state.swap([]), rf())
    
    def step(rf, state):
        LOGGER.info("batch step transform")
        def new_step(acc, *args):
            LOGGER.info("In batch.step")
            for x in args:
                if len(state.value) < batch_size:
                    state.value.append(x)
            if len(state.value) < batch_size:
                return acc
            else:
                return rf(acc, state.swap([]))
        return new_step
    
    def complete(rf, state):
        LOGGER.info("In batch complete transform")
        def new_complete(result):
            LOGGER.info("In batch.complete")
            if len(state.value) > 0:                
                return rf(result, state.swap(None))
            else:
                return rf(result)
        return new_complete
            
    return make_transducer(step=step, init=init, complete=complete, name="batching({})".format(batch_size))


def repeating(n):
    """Transducer that repeats each element n times"""
    def step(rf, state):
        LOGGER.info("In repeat step transform")
        return lambda acc, arg: prelude.seq(
            LOGGER.info("In repeat.step"),
            ft.reduce(rf, it.repeat(arg, n), acc))
    return make_transducer(step=step, name="repeating({})".format(n))


def inc(x):
    return x+1


catting = make_transducer(step=lambda rf, state: lambda acc, x: ft.reduce(rf, x, acc), name="catting")
"""Transducer that flattens the input stream"""

def mapcatting(f):
    """Transducer that applies transformation to each element, 
    and then flattens the result"""
    def step(rf, state):
        return lambda acc, x: ft.reduce(rf, f(x), acc)
    return make_transducer(step=step, name="mapcatting({})".format(f))


def taking(n):
    def init(rf, state):
        LOGGER.info("In taking init transform")
        state.swap(0)
        return rf

    def step(rf, state):
        return lambda acc, x: prelude.seq(
            state.change(inc), rf(acc, x)
        ) if state.value < n else prelude.throw(StopIteration(acc))
    return make_transducer(init=init, step=step, name="taking({})".format(n))



def dropping(n):
    def init(rf, state):
        LOGGER.info("In dropping init transform")
        state.swap(0)
        return rf

    def step(rf, state):
        LOGGER.info("In dropping step transform")
        return lambda acc, x: prelude.seq(
            state.change(inc), acc
        ) if state.value < n else rf(acc, x)
    return make_transducer(init=init, step=step, name="taking({})".format(n))


def windowing(n, strict=False):
    def init(rf, state):
        LOGGER.info("In windowing init transform")
        state.swap([])
        return rf

    def step(rf, state):
        LOGGER.info("In windowing step transform")
        def new_step(acc, x):
            if len(state.value) < n:
                state.value.append(x)
                return acc
            else:                
                window = state.change(lambda w:conj_list(w[1:], x)) # window is slid to the right
                return rf(acc, window)
        return new_step
    def complete(rf, state):
        LOGGER.info("In windowing complete transform")
        def new_complete(result):
            if strict or len(state.value) == 0:
                state.swap(None)
                return rf(result)
            else:
                return rf(result, state.swap(None))
        return new_complete
    return make_transducer(step=step, init=init, complete=complete, name="windowing({})".format(n))

identity = make_transducer()


def enumerating(start=0):
    def init(rf, state):
        state.swap(start)
        return rf
    def step(rf, state):
        return lambda acc, x: rf(acc, (state.change(inc), x))
    return make_transducer(step=step, init=init, name="enumerating(start={})".format(start))


def first(pred=None):
    pred = pred if pred is not None else prelude.const(True)
    def step(rf, state):
        return lambda acc, x: prelude.throw(
            Reduced(rf(acc, x))
        ) if pred(x) else acc
    return make_transducer(step=step, name="first(pred={})".format(pred))


def last(pred=None):
    pred = pred if pred is not None else prelude.const(True)
    def step(rf, state):
        def new_step(acc, x):
            if pred(x):
                state.swap(x)
            return acc
        return new_step
    def complete(rf, state):
        def new_complete(result):
            LOGGER.debug("In last transduced complete")
            return rf(rf(result, state.swap(None)))
        return new_complete
    return make_transducer(step=step, complete=complete, name="last(pred={})".format(pred))


def transduce(transducer, reducer, reducible, init=prelude._missing):
    transduced = transducer(reducer)
    return reduce(transduced, reducible, init=init)


def consume_queue(queue):
    while queue:
        yield queue.popleft()
        

def lazy_transduce(transducer, source):
    r = transducer(Reducer(step=conj_list))
    accumulator = collections.deque()
    for x in source:
        try:
            accumulator = r(accumulator, x)
        except (StopIteration, Reduced) as ex:
            accumulator = ex.value
            break
        finally:
            yield from consume_queue(accumulator)
    else:
        final = r(accumulator)
        assert final is accumulator
        yield from consume_queue(final)
        

       
def sequence(transducer, reducible):
    def step(acc, x):
        acc.append(x)
        return acc
    def init():
        return []
    return reduce(transducer(Reducer(step=step, init=init, complete=prelude.identity)), reducible)


@ft.singledispatch
def conj(col, item):
    pass

@conj.register(list)
def conj_list(col, item):
    col.append(item)
    return col

@conj.register(tuple)
def conj_tuple(col, item):
    return (*col, item)

@conj.register(set)
def conj_set(col, item):
    col.add(item)
    return col

@conj.register(frozenset)
def conj_frozenset(col, item):
    return col.union((item,))


@conj.register(dict)
def conj_dict(col, item):
    col[item[0]] = item[1]
    return col


@conj.register(str)
def conj_str(col, item):
    return col + str(item)



@ft.singledispatch
def into(sink, source, transducer=identity):
    """Collect items from source into sink, 
    optionally passing through a transformation"""
    return transduce(transducer, conj, source, init=sink)


@into.register(list)
def into_list(sink, source, transducer=identity):
    return transduce(transducer, Reducer(step=conj_list, complete=prelude.identity), source, init=sink)


@into.register(tuple)
def into_tuple(sink, source, transducer=identity):
    buffer = list(sink)
    return tuple(transduce(transducer, Reducer(step=conj_list, complete=prelude.identity), source, init=buffer))


@into.register(collections.Generator)
def into_coroutine(sink, source, transducer=identity):
    sender = Reducer(
        step=lambda acc, x: prelude.seq(acc.send(x), next(acc), acc),
        complete=lambda sink: sink.close()
    )
    return transduce(transducer, sender, source, init=sink)

