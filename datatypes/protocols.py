import abc
import collections
import functools
import itertools
from funklib import basics

class Foldable(abc.ABC):
    @abc.abstractmethod
    def foldl(self, f, init):
        pass

    @abc.abstractmethod
    def foldr(self, f, init):
        pass

    @abc.abstractmethod
    def scanl(self, f):
        pass

    @abc.abstractmethod
    def scanr(self, f):
        pass

    @abc.abstractmethod
    def fold_map(self, f):
        if instance(self, Functor):
            return self.map(f).fold()

    @abc.abstractmethod
    def fold(self):
        return self.fold_map(basics.identity)

    
@functools.singledispatch
def foldl(col, f, init):
    raise NotImplementedError

@foldl.register(Foldable)
def foldl_foldable(seq, f, init):
    return seq.foldl(f, init)

@foldl.register(collections.abc.Iterator)
def foldl_collection(col, f, init):
    return functools.reduce(f, col, init)


@functools.singledispatch
def foldr(col, f, init):
    raise NotImplemented

@foldr.register(Foldable)
def foldr_foldable(seq, f, init):
    return seq.foldr(f, init)

@foldr.register(collections.abc.Sequence)
def foldr_sequence(seq, f, init):
    acc = init
    for i in range(1, len(seq)+1):
        acc = f(seq[-i], acc)
    return acc



class Functor(abc.ABC):
    @abc.abstractmethod
    def map(self, f):
        raise NotImplementedError

    
class Semigroup(abc.ABC):
    @abc.abstractmethod
    def mappend(self, other): pass
    

class Monoid(Semigroup):
    @classmethod
    @abc.abstractmethod
    def empty(cls): pass


    
class Applicative(Functor):
    @classmethod
    @abc.abstractmethod
    def pure(cls, x): pass

    @abc.abstractmethod
    def ap(self, other): pass

    
class Monad(Applicative):
    @abc.abstractmethod
    def flatmap(self, f): pass


@Functor.register
@Applicative.register
@Monad.register
class Identity(tuple):
    def __new__(cls, value):
        return tuple.__new__(cls, (value,))

    def map(self, f):
        return Identity(f(self[0]))
    
    @classmethod
    def pure(cls, x):
        return cls(x)

    def flatmap(self, f):
        return f(self[0])
    
    def ap(self, other):
        return Identity(self[0](other[0]))

    def fold_map(self, f):
        return f(self[0])

    def __repr__(self):
        return "{}({})".format(type(self).__name__, self[0])

    
@Functor.register
@Monoid.register
@Applicative.register
class Constant(tuple):
    def __new__(cls, value):
        return tuple.__new__(cls, (value,))

    def map(self, f):
        return self

    @classmethod
    def empty(cls):
        return NotImplemented

    def mappend(self, other):
        return Constant(self[0].mappend(other[0]))

    @classmethod
    def pure(cls, x):
        return cls(cls.empty())

    def ap(self, other):
        return Constant(self[0].mappend(other[0]))

    def fold_map(self, f):
        return self.empty()

    def __repr__(self):
        return "{}({})".format(type(self).__name__, self[0])

    
@Monoid.register
class Sum(int):
    def mappend(self, other):
        return Sum(self + other)

    @classmethod
    def empty(cls):
        return cls(0)

@Monoid.register
class Product(int):
    def mappend(self, other):
        return Product(self * other)

    @classmethod
    def empty(cls):
        return cls(1)
    
    
@Monad.register
@Functor.register
@Foldable.register
class List(list):
    def foldl(self, f, init):
        print("foldl method called for List")
        return functools.reduce(f, self, init)

    def foldr(self, f, init):
        print("foldr method called for List")
        acc = init
        for i in range(1, len(self)+1):
            acc = f(self[-i], acc)
        return acc

    def scanl(self, f):
        acc = List((init,))
        for x in self:
            acc.append(f(acc[-1], x))
        return acc
        
    def map(self, f):
        return List(map(f, self))

    def flatmap(self, f):
        return List(y for x in self for y in f(x))

    @classmethod
    def pure(cls, x):
        return cls((x,))

    
@Monad.register
@Functor.register
class Either(tuple):
    __slots__ = []
    def fold(self, left, right):
        if type(self) is Left:
            return left(self[0])
        elif type(self) is Right:
            return right(self[0])
        else:
            raise TypeError

    @property
    def is_left(self):
        return self.fold(basics.const(True), basics.const(False))

    @property    
    def is_right(self):
        return self.fold(basics.const(False), basics.const(True))

    def get(self, default=None):
        return self.fold(basics.const(default), basics.identity)
    
    @property
    def swap(self):
        return self.fold(Right, Left)

    def map(self, f):
        return self.fold(Left, basics.compose(Right, f))

    def flatmap(self, f):
        return self.fold(basics.const(self), f)

    def __or__(self, other):
        return self.fold(basics.const(other), basics.const(self))

    def __and__(self, other):
        return self.fold(basics.const(self), basics.const(other))

    def __repr__(self):
        return "{}({})".format(type(self).__name__, self[0])
    
    
class Left(Either):
    def __new__(cls, x):
        return tuple.__new__(cls, (x,))

class Right(Either):
    def __new__(cls, x):
        return tuple.__new__(cls, (x,))
    

def throw(ex):
    raise ex

def thrower(excf):
    return lambda x:throw(excf(x))
