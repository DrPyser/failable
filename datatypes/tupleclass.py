from operator import itemgetter

def constructor_factory(fields):
    def __new__(cls, *args, **kwargs):
        if any(k not in fields for k in kwargs):
            raise TypeError("Constructor received invalid keyword arguments")
        if len(args) + len(kwargs.values()) > len(fields):
            raise TypeError("Constructor received too many arguments")
        if len(args) + len(kwargs.values()) < len(fields):
            raise TypeError("Constructor received too few arguments")
        return tuple.__new__(cls, args + tuple(kwargs[f] for f in fields[len(args):]))
    return __new__


def printer_factory(fields):
    def __repr__(self):
        return "{}({})".format(
            type(self).__name__,
            ",".join("{}={}".format(f, getattr(self, f)) for f in fields)
        )
    return __repr__


class TupleClass(type):
    def __new__(cls, name, bases, nmspc, **kwds):
        bases = bases + (tuple,) if not any(issubclass(x, tuple) for x in bases) else bases
        nmspc["__new__"] = constructor_factory(nmspc.get("_fields", ()))
        readers = map(lambda p: (p[1], property(itemgetter(p[0]))), enumerate(nmspc.get("_fields", ())))
        nmspc.update(readers)
        return type.__new__(cls, name, bases, nmspc, **kwds)



def tupleclass(fields):
    def decorator(klass):
        readers = dict(map(lambda p: (p[1], property(itemgetter(p[0]))), enumerate(fields))        )
        bases = (tuple, ) + klass.__bases__ if not any(issubclass(b, tuple) for b in klass.__bases__) else klass.__bases__
        return type(klass.__name__, bases, dict(
            klass.__dict__,
            **readers,
            __new__=constructor_factory(fields),
            __repr__=printer_factory(fields)
        ))
    return decorator


