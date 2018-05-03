import sys
import functools as ft
import funklib.core.reducible as reducible
import funklib.core.prelude as prelude
import collections
import abc

def coroutine(f):
    @ft.wraps(f)
    def wrapper(*args, **kwargs):
        coro = f(*args, **kwargs)
        next(coro)
        return coro
    return wrapper


class Sink:
    def __init__(self):
        self._receiver = self.run()

    def send(self, x):
        return self._receiver.send(x)

    def throw(self, ex):
        self._receiver.throw(ex)

    def close(self):
        self._receiver.close()

    @abc.abstractmethod
    def run(self): pass
    
    def reopen(self):
        self._receiver.close()
        self._receiver = self.run()


class FunctionSink(Sink):
        def __init__(self, f, *args, **kwargs):
            self.f = coroutine(f)
            self.args = args
            self.kwargs = kwargs
            super().__init__()

        def run(self):
            return self.f(*self.args, **self.kwargs)

        
def as_sink(f):
    return ft.partial(FunctionSink, f)


@as_sink
def printer(sep="\n", end="", stream=sys.stdout):
    try:
        item = (yield)
        stream.write(str(item))
        stream.flush()
        while True:
            item = (yield)
            stream.write(sep)
            stream.write(str(item))
            stream.flush()
    except GeneratorExit:
        stream.write(end)
        stream.flush()
        raise
            

@as_sink
def null():
    while True:
        x = (yield)


class collect(Sink):
    def __init__(self, init=(), maxlen=None):
        super().__init__()
        self._buffer = collections.deque(init, maxlen=maxlen)
        
    @property
    def buffer(self):
        return list(self._buffer)

    @coroutine
    def run(self):
        while True:
            item = (yield)
            self._buffer.append(item)


class yielder(Sink):
    def send(self, x):
        x = self._receiver.send(x)
        next(self._receiver)
        return x

    @coroutine
    def run(self):
        while True:
            item = (yield)
            yield item

        
@prelude.singleton()
class Sending(reducible.Reducer):
    def __init__(self): pass
    def init(self):
        return null_sink()

    def step(self, acc, x):
        try:
            acc.send(x)
        except StopIteration:
            raise Reduced(acc)
        else:
            return acc

    def complete(self, result):
        result.close()
        return result


@coroutine    
def reactive_transduce(transducer, sink=None):
    r = transducer(Sending)
    sink = sink or r()
    try:        
        while True:
            x = (yield)
            sink = r(sink, x)               
    except (reducible.Reduced, StopIteration) as ex:
        return r(ex.value)
    except GeneratorExit:
        return r(sink)
        
    
