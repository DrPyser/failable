from datatypes.sealed import Sealed, caseclass, datatype
from collections import deque

@datatype(["unfix"])
class Fix:
    def cata(self, f):
        g = lambda x: x.cata(f)
        return f(fmap(self.unfix, g))
    

class List(metaclass=Sealed):
    @classmethod
    def from_iterable(cls, iterable):
        it = deque(iterable)
        res = Empty()
        while it:
            res = Cons(it.pop(), res)
        return res

    def __iter__(self):
        if type(self) is Empty:
            yield from ()
        elif type(self) is Cons:
            t = self
            while type(t) is not Empty:                
                (h,t) = (t.head, t.tail)
                yield h

    def fmap(self, f):
        return self.from_iterable(map(f, self))

    
@caseclass(List, ["head", "tail"])
def Cons(x,xs):
    return (x,xs)

@caseclass(List, [], cached=True)
def Empty():
    return ()


def ana(f, seed):
    x = f(seed)
    while x is not None:
        (value, seed) = x
        yield value
        x = f(seed)

        
   
