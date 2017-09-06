# Functional datatypes 

This package implements many datatypes commonly used in functional programming.

## Failable computation
Data type for failable computations, akin to `Data.Either` in Haskell, or Promises in Javascript(minus the async).

The data type is defined using an abstract base class `failable`(also serving as a namespace for various utility functions)
and two subclasses, `failure` and `success`.

Both subclasses implement the same methods declared in the ABC. As a consequence, 
a value of either type can be treated the same, 
allowing code using this datatype to wait until
the end of a sequence of failable computations before having to look and see whether one of the step failed,
and display the error/use the value, or switch to another error-handling API(e.g. exceptions).

Utility functions and methods on the data type allow easy interfacing with an exception-based API,
as well as a None-as-failure or similar API, and back.

## Linked list

The "list" module implement a singly linked list, as well as a lazy version 
which stores its tail as a "suspended computation", a thunk which is cached once evaluated
(subsequent evaluations returning the cached value).
A generator or iterator can be transformed into a lazy list even if the generated sequence is infinite.
The linked list will be constructed incrementally as required. Of course, in this case,
the linked list will consume more and more memory as the generator is consumed, unless the heads of the list
are freed at the same time.

## Abstract base classes and functional API
The "functionals" module implement ABCs that define some functional APIs, 
such as `Functor`(declaring the `fmap` method),
`Applicative`(inheriting from `Functor` and declaring the `pure` classmethod and the `ap` method)
and `Monad`(inheriting from `Applicative` and declaring the `bind` and `join` methods and the `fail` classmethod).

This module also defines a subclass of Python's list datatype, `ArrayList`, which inherits from and implements the methods
of those functional APIs.

Datatypes defined in the "failable" and "list" module of this package also implement those functional APIs.
