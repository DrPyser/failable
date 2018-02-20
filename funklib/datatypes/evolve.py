from tupleclass import tupleclass
from contextlib import ExitStack
from itertools import islice, chain
from basics import unit

def window(iterable, size=2):
    slices = (islice(iterable, i, None) for i in range(size))
    return zip(*slices)


class Incubator:
    def __init__(self, init):
        self.initial = self.copy(init)
        self.delta = []
        
    def persist(self):
        """
        Applies all deltas to the initial value, 
        and return the result.
        If any delta application fails, all delta are reverted,
        which should return the prototype to its initial value.
        """
        prototype = self.initial
        with ExitStack() as stack:
            for d in self.delta:            
                rollback = d.rollback(prototype)
                prototype = d.apply(prototype)
                stack.callback(rollback.apply, prototype)
            else:
                stack.pop_all() # on success of all applications, rollbacks are discarded
                # reset
                self.initial = self.copy(prototype)
                self.reset()
                return prototype
   
    def add_delta(self, delta):
        self.delta.append(delta)

    def reset(self, n=None):
        if n is None:
            self.delta.clear()
        else:
            for i in range(n):
                self.delta.pop()
                            
    def __enter__(self):
        return self

    def __exit__(self, ext, ex, tb):
        try:
            if ext is None:
                self.persist()
        finally:
            self.reset()
            
    def __repr__(self):
        return "{}(initial={}, delta=[{}])".format(type(self).__name__, self.initial, ",".join(map(str, self.delta)))


class Delta(tuple):
    def apply(self, initial):
        return NotImplemented

    def rollback(self, initial):
        return NotImplemented

    def __repr__(self):
        return "<{}>".format(type(self).__name__)


def make_delta(attributes, apply, rollback):
    _apply = apply
    _rollback = rollback
    @tupleclass(attributes)
    class AnonymousDelta(Delta):
        def apply(self, initial):
            return _apply(self, initial)

        def rollback(self, initial):
            return _rollback(self, initial)
    return AnonymousDelta
    
@tupleclass([])    
class NoOp(Delta):
    def apply(self, initial):
        return initial

    def rollback(self, initial):
        return NoOp()

@tupleclass(["new"])
class Append(Delta):
    pass

class ListAppend(Append):
    def apply(self, initial):
        initial.append(self.new)
        return initial

    def rollback(self, initial):
        return ListPop()

@tupleclass([])
class Pop(Delta):
    pass

class ListPop(Pop):
    def apply(self, initial):
        initial.pop()
        return initial

    def rollback(self, initial):
        return ListAppend(initial[-1]) if len(initial) > 0 else NoOp()

@tupleclass(["index"])
class PopIndex(Delta):
    pass

class ListPopIndex(PopIndex):
    def apply(self, initial):
        initial.pop(self.index)
        return initial

    def rollback(self, initial):
        return ListInsert(self.index, initial[self.index])


@tupleclass(["index", "new"])    
class Set(Delta):
    pass
        
class ListSet(Set):
    def apply(self, initial):        
        initial[self.index] = self.new
        return initial

    def rollback(self, initial):
        return ListSet(self.index, initial[self.index]) if self.index in range(len(initial)) else NoOp()



class Repeat(Delta):
    def __init__(self, delta, repetitions):
        self.delta = delta
        self.repetitions = repetitions

    def apply(self, initial):
        current = initial
        for i in range(self.repetitions):
            current = self.delta.apply(current)
        return current

    def rollback(self, initial):
        return Repeat(self.delta.rollback(initial), self.repetitions)
    
@tupleclass(["extension"])        
class Extend(Delta):
    pass

class ListExtend(Extend):
    def apply(self, initial):
        initial.extend(self.extension)    
        return initial

    def rollback(self, initial):
        return Repeat(ListPop(), len(self.extension))

@tupleclass(["new", "index"])
class Insert(Delta):
    pass


class ListInsert(Insert):
    def apply(self, initial):
        initial.insert(self.index, self.new)
        return initial

    def rollback(self, initial):
        return ListPopIndex(self.index)

    
@tupleclass(["replacement"])
class Replace(Delta):
    pass


class TupleReplace(Replace):
    def apply(self, initial):
        return self.replacement

    def rollback(self, initial):
        return TupleReplace(initial)


class TupleAppend(Append):
    def apply(self, initial):
        return tuple(chain(initial, unit(self.new)))

    def rollback(self, initial):
        return TupleReplace(initial)

    
class TuplePop(Pop):
    def apply(self, initial):
        return initial[:-1]

    def rollback(self, initial):
        return TupleReplace(initial)

    
class TupleSet(Set):
    def apply(self, initial):
        return tuple(x if i != self.index else self.new for i, x in enumerate(initial))

    def rollback(self, initial):
        return TupleReplace(initial)


class TupleExtend(Extend):
    def apply(self, initial):
        return tuple(chain(initial, self.extension))

    def rollback(self, initial):
        return TupleReplace(initial)


@tupleclass(["start", "stop", "step"])
class Slice(Delta):
    pass

class TupleSlice(Slice):
    def apply(self, initial):
        return initial[self.start:self.stop:self.step]

    def rollback(self, initial):
        return TupleReplace(initial)
    

class ListIncubator(Incubator):
    @classmethod
    def copy(cls, value):
        return value.copy()

    def append(self, x):
        self.delta.append(ListAppend(x))

    def pop(self, index=None):
        delta = ListPopIndex(index) if index is not None else ListPop()
        self.delta.append(delta)

    def extend(self, extension):
        self.delta.append(ListExtend(extension))
        
    def __setitem__(self, index, new):
        self.delta.append(ListSet(index, new))

        
class TupleIncubator(Incubator):
    @classmethod
    def copy(cls, value):
        return value

    def append(self, x):
        self.delta.append(TupleAppend(x))

    def pop(self, index=None):
        if index is None:
        count = 0
        while isinstance(self.delta[-1], Pop):
            count +=1
            self.delta.pop()
        if count > 0:
            delta = TupleSlice(0, -count, 1)
        else:
            delta = TuplePopIndex(index) if index is not None else TuplePop()
        self.delta.append(delta)

    def extend(self, extension):
        self.delta.append(TupleExtend(extension))
        
    def __setitem__(self, index, new):
        self.delta.append(TupleSet(index, new))

    def slice(self, start, stop, step=1):
        self.delta.append(TupleSlice(start, stop, step))
        
if __name__ == "__main__":
    x = []
    i = ListIncubator(x)
    with i:
        i.append(1)
        i.append(2)
        i.append(3)
        i[0] = 0
    print(i.persist())
