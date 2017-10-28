## Basic simple functional programming tools


def identity(x):
    return x


def const(x):
    return lambda *args, **kwargs: x


def compose2(f, g):
    return lambda *args, **kwargs: f(g(*args, **kwargs))


def compose(*callables):
    return ft.reduce(compose2, callables)


def uncurry(f):
    lambda args=(),kwargs=None: f(*args, **(kwargs or {}))


def flip(f):
    """Return a function which calls the argument function 
    with its positional arguments flipped"""
    return lambda *args, **kwargs: f(*reversed(args), **kwargs)


def unit(x):
    yield x


def applier(*args, **kwargs):
    return lambda f: f(*args, **kwargs)

    
def caller(f):
    return lambda *args, **kwargs: f(*args, **kwargs)


def singleton(*args, **kwargs):
    """Decorator which replaces a class definition
    by an instance of this class"""
    def decorator(f):
        return f(*args, **kwargs)
    return decorator



