class represent:
    def __init__(self, fields):
        self.fields = fields
        
    def __repr__(self):
        fields = self.fields
        return lambda self:"{}({})".format(
            type(self).__name__,
            ", ".join(
                "{}={}".format(k, getattr(self, k))
                for k in fields
            )
        )

class Obj:
    __repr__ = represent(["x", "y"]).__repr__
    def __init__(self, x, y):
        self.x = x
        self.y = y

