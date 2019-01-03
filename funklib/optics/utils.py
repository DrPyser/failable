from collections.abc import Mapping


def singleton(*args, **kwargs):
    return lambda klass: klass(*args, **kwargs)


class DelegatedAttribute:
    def __init__(self, delegate_name, attr=None):
        self.delegate_name = delegate_name
        self.attr = attr

    def __set_name__(self, name):
        if self.attr is None:
            self.attr = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:            
            return getattr(self.delegate(instance), self.attr)

    def __set__(self, instance, value):
        # instance.delegate.attr = value
        setattr(self.delegate(instance), self.attr, value)

    def __delete__(self, instance):
        delattr(self.delegate(instance), self.attr)

    def delegate(self, instance):
        return getattr(instance, self.delegate_name)

    def __str__(self):
        return "DelegatedAttribute({}.{})".format(self.delegate_name, self.attr)


def with_delegate(delegated_attributes, delegate_name):
    def inner(klass):
        attrs = delegated_attributes.items()\
            if isinstance(delegated_attributes, Mapping)\
            else zip(delegated_attributes, delegated_attributes)

        for a, b in attrs:
            setattr(klass, a, DelegatedAttribute(delegate_name, b))
        return klass
    return inner


if __name__ == "__main__":
    class delegate:
        def __init__(self, a, b, c):
            self.a = a
            self.b = b
            self.c = c
            
    @with_delegate({"a", "b"}, "delegate")
    class test:
        def __init__(self, delegate):
            self.delegate = delegate
            

        
