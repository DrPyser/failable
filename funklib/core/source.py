import random
import time
import abc

class Source:
    @abc.abstractmethod
    def __call__(self, sink):
        pass
    

class iterable_source(Source):
    def __init__(self, iterable):
        self.iterable = iterable

    def __call__(self, sink):
        for item in self.iterable:
            try:
                self.send(sink, item)
            except StopIteration as ex:
                return ex.value
        else:
            sink.close()
            return None

    def send(self, sink, item):
        sink.send(item)

        
class poisson_source(iterable_source):
    def __init__(self, rate, iterable):
        self.rate = rate
        self.iterable = iterable

    def send(self, sink, item):
        time.sleep(random.expovariate(self.rate))
        sink.send(item)

