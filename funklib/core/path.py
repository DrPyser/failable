import operator as op
import functools as ft
import funklib.core.prelude as prelude


def resolve_straight_attribute_path(obj, path, default=None):
    try:
        return op.attrgetter(path)(obj)
    except AttributeError:
        return default


def attribute_path_resolver(path, default=None):
    if "*" in path:
        return ft.partial(resolve_path, path=path, default=default)
    else:
        return ft.partial(resolve_straight_path, path=path, default=default)


def resolve_attribute_path(obj, path, default=None):
    components = path.split(".")
    if "*" in components:
        branch_point = components.index("*")
        stretch = components[:branch_point]
        getter = op.attrgetter(".".join(stretch))
        try:
            collection = getter(obj)
        except AttributeError:
            return default
        else:
            next_stretch = components[branch_point + 1:]
            if len(next_stretch) > 0:
                return map(
                    attribute_path_resolver(".".join(next_stretch), default),
                    collection)
            else:
                return collection
    else:
        return resolve_straight_attribute_path(obj, path, default)


def resolve_straigth_index_path(obj, path, default=None):
    indexes = path.split("/")
    node = obj
    for i in indexes:
        try:
            node = node[i]
        except KeyError:
            return default
    else:
        return node

    
class Resolver:
    def resolve(self, obj, default=None):
        pass

    def __rshift__(self, next_resolver):
        return ResolverFunction(
            lambda o, d=None: next_resolver.resolve(
                self.resolve(o, d), d
            )
        )


class ResolverFunction(Resolver):
    def __init__(self, function):
        self.function = function

    def resolve(self, obj, default=None):
        print(self.__class__.__name__)
        return self.function(obj, default)


class Attr(Resolver):
    def __init__(self, attr):
        self.attr = attr
        self._attrgetter = op.attrgetter(attr)

    def resolve(self, obj, default=None):
        print(self.__class__.__name__)
        try:
            return self._attrgetter(obj)
        except AttributeError:
            return default

    def resolve_strict(self, obj, default=None):
        return self._attrgetter(obj)


class ForEach(Resolver):
    def resolve(self, obj, default=None):
        print(self.__class__.__name__)
        return iter(obj)

    def __rshift__(self, next_resolver):
        return ResolverFunction(
            lambda o, d=None: (
                next_resolver.resolve(x, d)
                for x in self.resolve(o, d)
            ))


class Index(Resolver):
    def __init__(self, index):
        self.index = index

    def resolve(self, obj, default=None):
        print(self.__class__.__name__)
        try:
            return obj[self.index]
        except (IndexError, KeyError):
            return default
