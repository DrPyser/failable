from functools import partial, wraps

class curried(partial):
    """Auto-currying function wrapper which partially applies underlying function 
    until `n` arguments or more have been provided"""
    def __new__(cls, func, n, curry_last, args=(), kwargs=None):
        self = super(curried, cls).__new__(cls, func, *args, **(kwargs or {}))
        self._autocurried = n
        self._curry_last = curry_last
        return self

    def __call__(self, *args, **kwargs):
        missing = self._autocurried - len(args) - len(kwargs)
        if missing > 0 or self._curry_last:
            return self.curry(*args, **kwargs)
        else:
            return super().__call__(*args, **kwargs)

    def curry(self, *args, **kwargs):
        missing = max(self._autocurried-len(args)-len(kwargs), 0)
        return curried(self.func, missing, missing > 0 and self._curry_last, self.args+args, dict(self.keywords, **kwargs))

    def __repr__(self):
        return "<curried {}:({}, {})>".format(self.func, self.args, self.keywords)

    def __str__(self):
        return "<curried {}>".format(self.func)
    

def curry(n, curry_last=False):
    """A decorator for making a curried function up to n arguments"""
    def decorator(f):        
        return wraps(f)(curried(f, n, curry_last=curry_last))
    return decorator
