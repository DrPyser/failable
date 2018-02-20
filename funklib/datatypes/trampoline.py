from functools import wraps
from funklib.datatypes.adt import data

class Bounce(data):    
    _fields = ["bouncer", "args", "kwargs"]

    def resume(self):
        return self[0].jump(*self[1], **self[2])
    
    def __repr__(self):
        return "Bounce({}{}{}{}{})".format(
            self[0].__name__,
            ", " if any(self[1]) else "",
            ", ".join(repr(arg) for arg in self[1]),
            ", " if any(self[2]) else "",
            ", ".join("{}={!r}".format(k,v) for k,v in self[2].items())
        ) 
    
class Return(data):
    _fields = ["value"]
    
    def __repr__(self):
        return "Return({})".format(self[0])

def bounce(f, *args, **kwargs):
    return Bounce(f, args, kwargs)
    
class Trampolined:
    """
    Wrapper class for trampoline functions
    """
    def __init__(self, func):
        """
        
        """
        self.func = func
        wraps(func)(self)
        
    def jump(self, *args, **kwargs):
        return self.func(*args, **kwargs)
    
    def __call__(self, *args, **kwargs):
        res = self.jump(*args, **kwargs)
        while isinstance(res, Bounce):
            res = res.resume()
        else:
            return res.value
    
def trampoline(f):
    """
    Make a trampolined function from a generator.
    The generator should yield calls to itself or another trampoline,
    and return the result when it reaches a base case.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            bounce = f(*args, **kwargs)
            while bounce:
                bounce = next(bounce)
        except StopIteration as ex:
            return ex.value
    return wrapper
