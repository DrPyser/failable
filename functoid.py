from abc import ABC, ABCMeta
from .basics import SingletonType
from .currying import curried, curry


    
class FunctoidDescriptor:
    def __init__(self, descriptor):
        self._underlying = descriptor

    def __get__(self, instance, owner=None):
        return Functoid(self._underlying.__get__(instance, owner))

    def __set__(self, instance, value):
        self._underlying.__set__(instance, value)

    def __delete__(self, instance):
        self._underlying.__delete__(instance)



class FunctoidalType(type):
    # def __new__(cls, name, bases, attrs):
    #     ignored_defaults = vars(object)
    #     ignored = attrs.get("non_functoids", ignored_defaults)
    #     attrs = {k:(Functoid(f) if callable(f) and k not in ignored else f) for (k,f) in attrs.items()}
    #     return super().__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if 'non_functoids' in dir(cls):
            ignored = type.__getattribute__(cls, 'non_functoids')
            type.__setattr__(cls, 'non_functoids', frozenset(ignored).union(dir(object)))
        else:
            cls.non_functoids = dir(object)
       
        
    def __getattribute__(cls, name):
        attr = type.__getattribute__(cls, name)
        ignored = type.__getattribute__(cls, 'non_functoids')
        return Functoid(attr) if callable(attr) and name not in ignored else attr
    
class FunctoidalAbstractType(FunctoidalType, ABCMeta):
    def __init__(cls, name, bases, attrs):
        FunctoidalType.__init__(cls, name, bases, attrs)
        ABCMeta.__init__(cls, name, bases, attrs)

class FunctoidalABC(metaclass=FunctoidalAbstractType):
    non_functoids = dir(object)
    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        return Functoid(attr) if callable(attr) and name not in type(self).non_functoids else attr

        
class FunctoidalSingletonType(FunctoidalAbstractType, SingletonType):
    def __init__(cls, name, bases, attrs):
        FunctoidalAbstractType.__init__(cls, name, bases, attrs)
        SingletonType.__init__(cls, name, bases, attrs)
        

if __name__ == "__main__":
    @functoid(n=2)
    def add(x,y):
        return x+y
