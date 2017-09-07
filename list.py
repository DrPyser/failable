from datatypes.functionals import (Monad, FunctoidalSingletonType)
import functools as ft
import itertools as it
import basics


class Cons(tuple):
    __slots__ = []
    def __new__(cls, car, cdr):
        return tuple.__new__(cls, (car, cdr))

    @property
    def car(self):
        return tuple.__getitem__(self, 0)

    @property
    def cdr(self):
        return tuple.__getitem__(self, 1)

    def __repr__(self):
        return "Cons({},{})".format(self.car,self.cdr)



class Empty(Monad, metaclass=FunctoidalSingletonType):
    __slots__ = []
    def __new__(cls):
        return super().__new__(cls)

    def __repr__(self):
        return "Empty"

    def __str__(self):
        return "Empty"

    def __iter__(self):
        while False:
            yield None

    def __len__(self):
        return 0

    @property
    def tail(self):
        raise AttributeError("Empty list has no tail")

    @property
    def head(self):
        raise AttributeError("Empty list has no head")

    def is_empty(self):
        return True

    def prepend(self, x):
        return List(x)

    def __add__(self, other):
        return other

    def fmap(self, f):
        return self

    def then(self, f):
        return self

    def ap(self, other):
        return self

    
class List(Monad, Cons):
    Empty = Empty()
    
    non_functoids = Monad.non_functoids.union(["head", "tail", "car", "cdr"])
    
    def __new__(cls, *elements):
        return ft.reduce(lambda y,x: super(List, cls).__new__(cls, x, y), reversed(elements), List.Empty)
        
    @classmethod
    def from_iterable(cls, iterable):
        if isinstance(iterable, cls):
            return iterable
        else:
            return cls(*iterable)
    
    @property
    def head(self):
        return self.car
        
    @property
    def tail(self):
        return self.cdr
    
    def __iter__(self):
        x = self
        while not x.is_empty():
            yield x.head
            x = x.tail

    def inits(self):
        x = self
        while not x.is_empty():
            yield x
            x = x.tail
        
        
    def is_empty(self):
        return False

    def __len__(self):
        return sum(1 for x in self)
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            start = index.start or 0            
            x = self.drop(start)
            y = x if index.stop == None else x.take(index.stop-start)
            if index.step == None or index.step == 1:
                return y
            else:
                return type(self).from_iterable(a for (i, a) in enumerate(y) if i%index.step == 0)
        elif index >= 0:
            for (i, x) in enumerate(self):
                if i == index:
                    return x
            else:
                raise Exception("List index out of bounds")
        else:
            raise TypeError("Invalid index: expected natural number")
    
    def __repr__(self):
        return "List({})".format(", ".join(map(str, iter(self))))
        
    
    @classmethod
    def cons(cls, a, b):
        return b.prepend(a)
        
    def prepend(self, x):
        return super().__new__(type(self), x, self)
    
    def __add__(self, other):
        return ft.reduce(type(self).prepend, reversed(self), other)

    @classmethod
    def pure(cls, x):
        return cls(x)

    @classmethod
    def fail(cls, e):
        return Empty
    
    def then(self, f):
        return ft.reduce(lambda y,x: y + f(x), self, type(self).Empty)
    
    def fmap(self, f):
        return type(self).from_iterable(map(f,self))
    
    def ap(self, other):
        return type(self).from_iterable(f(x) for f in self for x in other)

    def take(self, n):
        return type(self).from_iterable(it.islice(iter(self), n))

    def drop(self, n):
        tail = self
        for x in range(n):
            tail = tail.tail
        return tail

class suspended:
    """Data type for cachable suspended computations"""
    __slots__ = ['_thunk', '_cached', '_value']
    def __init__(self, thunk):
        self._thunk = thunk
        self._cached = False
        self._value = None

    def is_cached(self):
        return self._cached
        
    @property
    def value(self):
        """Returns the result of the computation,
        resuming the computation if not already cached"""
        if self._cached:
            return self._value
        else:
            return self.compute()
        
    def compute(self):
        """Resume the suspended computation, caching the result"""
        self._value = self._thunk()
        self._cached = True
        return self._value
    
    def __call__(self):
        """same as `compute`"""
        return self.compute()

    def __repr__(self):
        return "<suspended {!r}: {!s}>".format(self._thunk, self._value if self._cached else "<not computed>")
    
class LazyList(List):    

    class LazyEmpty(Empty):
        def prepend(self, x):
            return LazyList(x)

    Empty = LazyEmpty()
    
    def __new__(cls, *elements):
        return cls.from_iterable(elements)
        
    @classmethod
    def from_iterable(cls, iterable):
        iterator = iter(iterable)
        try:
            return Cons.__new__(cls, next(iterator), suspended(lambda: cls.from_iterable(iterator)))
        except StopIteration:
            return cls.Empty
 
    @property
    def tail(self):
        return self.cdr.value
    
    def __repr__(self):        
        def evaluated(suscomp):
            if suscomp.is_cached():
                yield suscomp.value
                if not suscomp.value.is_empty():
                    yield from evaluated(suscomp.value.cdr)
        precomputed = list(evaluated(self.cdr))
        if len(precomputed) > 0 and precomputed[-1].is_empty():
            return "LazyList({}, {})".format(self.head, ", ".join(str(x.head) for x in precomputed if not x.is_empty()))
        elif len(precomputed) > 0:
            return "LazyList({}, {}, ...)".format(self.head, ", ".join(str(x.head) for x in precomputed))
        else:
            return "LazyList({}, ...)".format(self.head)
        
    
    def __add__(self, other):
        return Cons.__new__(type(self), self.head, suspended(lambda: self.tail + other))

    def prepend(self, x):
        return Cons.__new__(type(self), x, suspended(lambda: self))

    def join(self):
        return Cons.__new__(type(self), self.head.head, suspended(lambda: self.head.tail + self.tail.join()))
    
    def then(self, f):
        x = f(self.head)
        return Cons.__new__(type(self), x.head, suspended(lambda: x.head.tail + self.tail.then(f)))
    
    def fmap(self, f):
        return Cons.__new__(type(self), f(self.head), suspended(lambda: self.tail.fmap(f)))
