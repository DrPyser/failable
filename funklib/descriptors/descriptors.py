from funklib.core.prelude import identity

class Filter:
    def __init__(self, on_get=identity, on_set=identity):
        self.on_get = on_get
        self.on_set = on_set
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, type):
        if instance is None:
            return self
        else:
            return self.on_get(vars(instance)[self.name])

    def __set__(self, instance, value):
        if instance is not None:
            vars(instance)[self.name] = self.on_set(value)
    
