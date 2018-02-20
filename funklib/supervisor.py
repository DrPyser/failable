from contextlib import ExitStack
from functools import wraps

def with_handler(exceptions, handler):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except tuple(exceptions) as e:
                return handler(e)
        return wrapper
    return decorator


def find(pred, iterable, default=None):
    return next((x for x in iterable if pred(x)), default)

class Supervisor:
    def __init__(self, handlers=(), contexts=()):
        self.handlers = list(handlers)
        self.contexts = list(contexts)

    def register_context(self, context):
        self.contexts.append(context)

    def register_handler(self, ex_types, handler=None):
        decorator = lambda h: self.handlers.append((ex_types, h))
        if handler is None:
            return decorator
        else:
            decorator(handler)

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return self.supervise(f, *args, **kwargs)
        return wrapper

    def supervise(self, f, *args, **kwargs):
        with ExitStack() as stack:
            for c in self.contexts:
                stack.enter_context(c)
            try:
                return f(*args, **kwargs)
            except Exception as e:
                try:
                    handler = next(h[1] for h in self.handlers if any(isinstance(e, ext) for ext in h[0]))
                except StopIteration:
                    raise e
                else:
                    return handler(e)
