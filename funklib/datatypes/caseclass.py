import funklib.core.prelude as prelude
import collections


def dispatch(self, actions):
    return actions[type(self)](self)


def abstract_new(cls, *args, **kwargs):
    raise TypeError("Cannot construct instance of abstract class {}".format(
        cls.__name__
    ))


def default_repr(self):
    return "{}({})".format(
        type(self).__name__,
        ", ".join(
            "{}={}".format(
                f, getattr(self, f)
            ) for f in self._fields
        )
    )


def singleton_factory_factory(constructor):
    def __new__(cls, *args, **kwargs):
        instance = getattr(cls, "__singleton_instance__", None)
        if instance is None:
            instance = constructor(cls, *args, **kwargs)
            setattr(cls, "__singleton_instance__", instance)
        return instance
    return __new__


class Caseclass(type):
    def __new__(cls, name, bases, nmspc, sealed=True, fields=None, instance_dict=False, singleton=False, **kwds):
        nmspc = nmspc or {}
        if len(bases) == 0:
            # creating superclass here
            nmspc.update(dispatch=dispatch, __new__=abstract_new, __slots__=())
            base = super(Caseclass, cls).__new__(cls, name, bases, nmspc, **kwds)
            base.__sealed__ = sealed
            base.__caseclass_root__ = True
            base.__subclasses__ = []
            return base
        else:
            base = next(b for b in bases if isinstance(b, cls))
            if (sealed or base.__sealed__):
                if nmspc["__module__"] != base.__module__:
                    raise TypeError(
                        "Subclass {} of sealed caseclass {} is defined in module {}, "
                        "but parent is defined in module {}.".format(
                            name, base.__name__, nmspc["__module__"], base.__module__)
                    )
            fields = fields if fields is not None else nmspc.get("__annotations__", None)
            if fields is not None:
                bases = (
                    collections.namedtuple("{}_skeleton".format(name), tuple(fields)),
                    *bases
                )
            else:
                bases = (
                    tuple,
                    *bases
                )
                nmspc.update(_fields=())
                if singleton:
                    nmspc.update(__new__=singleton_factory_factory(tuple.__new__))
                else:
                    nmspc.update(__new__=tuple.__new__)
                    
            nmspc.update(__repr__=default_repr)
            if not instance_dict:
                nmspc.update(__slots__=())
            new = super(Caseclass, cls).__new__(cls, name, bases, nmspc, **kwds)
            new.__sealed__ = sealed
            new.__caseclass_root__ = False
            base.__subclasses__.append(new)
            return new

    def add_method(self, method):
        setattr(self, method.__name__, method)
        return method

    
