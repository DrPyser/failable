from .functionals import *
from collections import UserList

class ArrayList(Monad, UserList):
    def fmap(self, f):
        return ArrayList(map(f, self))

    @classmethod
    def pure(cls, x):
        return cls((x,))

    def then(self, f):
        return ArrayList(ft.reduce(lambda y, x: it.chain(y, f(x)), self, []))

    @classmethod
    def fail(cls, msg):
        return cls(())
