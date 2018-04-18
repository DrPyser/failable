from abc import abstractmethod
import itertools as it
import functools as ft
import funklib.core.prelude as prelude
import abc

#@Monad.register
class Maybe(abc.ABC):
    __slots__ = ()
    def maybe(self, something, default):
        if isinstance(self, Something):
            return something(*self)
        elif isinstance(self, Nothing):
            return default
        else:
            raise TypeError

    def is_something(self):
        return self.maybe(prelude.const(True), False)

    def is_nothing(self):
        return self.maybe(prelude.const(False), True)

    def flatmap(self, f):
        return self.maybe(f, self)

    def map(self, f):
        return self.maybe(prelude.compose(Something, f), self)

    @classmethod
    def from_exceptions(cls, *exceptions):
        def decorator(f):
            @ft.wraps
            def wrapper(*args, **kwargs):
                try:
                    result = f(*args, **kwargs)
                except exceptions:
                    return Nothing
                else:
                    return Something(result)


@prelude.tupleclass("value")
class Something(Maybe): pass

#@prelude.singleton()
@prelude.tupleclass()
class Nothing(Maybe):
    


if __name__ == "__main__":
    @Maybe.from_exceptions((Exception,))
    def test(x):
        if x:
            return x
        else:
            raise Exception("Oh no!")
        
