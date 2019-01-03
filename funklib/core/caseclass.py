import types
import inspect
import functools as ft
from collections.abc import Iterable


def simpleclass(f=None, **kwargs):
    slots = kwargs.pop("slots", True)

    def decorator(f):
        sig = inspect.signature(f)

        @ft.wraps(f)
        def __init__(self, *args, **kwargs):
            for k, v in f(*args, **kwargs).items():
                setattr(self, k, v)

        bases = kwargs.pop("bases", ())

        def exec_body(ns):
            if slots:
                if isinstance(slots, Iterable):
                    __slots__ = list(slots)
                else:
                    __slots__ = list(sig.parameters)
                ns.update(__slots__=__slots__)

                def __repr__(self):
                    vs = {k: getattr(self, k) for k in __slots__}
                    return f"{f.__name__}({vs})"
            else:
                def __repr__(self):
                    vs = vars(self)
                    return f"{f.__name__}({vs})"

            ns.update(
                __init__=__init__,
                __repr__=__repr__
            )
            ns.update(kwargs)
        return types.new_class(f.__name__, bases, exec_body=exec_body)
    if f is not None:
        return decorator(f)
    else:
        return decorator


class caseclass:
    @classmethod
    def case(cls, f=None, **kwargs):
        bases = (cls, *kwargs.pop("bases", ()))
        kwargs["bases"] = bases
        return simpleclass(f, **kwargs)

    
if __name__ == "__main__":
    class Option(caseclass): pass
    
    @Option.case
    def Nothing(): return locals()

    @Option.case
    def Some(value): return locals()

    
