import types


class class_property:
    """
    Descriptor for class-level properties
    """
    def __init__(self, getter):
        self.getter = getter
        #self.setter = setter

    def __get__(self, instance, owner=None):
        owner = owner if owner is not None \
            else instance.__class__
        return self.getter(owner)


def subclass(parent, name, mixins=(), exec_body=None):
    """
    Create a subclass of parent.
    """
    return types.new_class(name, (parent, *mixins), exec_body=exec_body)


class Subclasser:
    subclass = classmethod(subclass)
