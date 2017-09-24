# Funklib

This is a library package for functional programming in Python.

The goal is to provide various functional programming tools and utilities 
that complement standard libraries, make use of the cool features of the language,
play off its strengths and compromise on its weaknesses.

For example, recursion is avoided, 
"object-oriented-style interfaces"(i.e. abc's and methods) are used and defined.

## Functional datatypes 

This subpackage implements many datatypes commonly used in functional programming,
and associated utilities.

### "Algebraic datatype"-style classes

Most datatypes implemented here are immutable, persistent data structures.

Algebraic datatypes are types defined as unions("sum") of "product types", which 
are basically tuples of fields. 
In python, a product type could be defined using a `namedtuple`.
An algebraic datatype could be defined by defining an abstract base class
representing the datatype, and subclasses of that base class for each product type
(or "constructor" in Haskell) in the datatype.

This package defines a metaclass `ADTMeta` and a base class `data`, instance of that metaclass,
that implement similar functionalities to `namedtuple`s, 
in that they are tuples with named fields(implemented as getter properties).
`ADTMeta` and `data` together also implement optional instance caching.
This is particularly useful for "empty" types that have no fields and contain no data,
and so are essentially singleton types. 
However, since these data structures are immutable, generalized instance caching
can also be valuable in saving memory when creating lots of objects containing immutable values.

Subclassing `data` allows one to easily define a product type.

### Abstract base classes and functional API
The "functionals" module implement ABCs that define some functional APIs, 
such as `Functor`(declaring the `fmap` method),
`Applicative`(inheriting from `Functor` and declaring the `pure` classmethod and the `ap` method)
and `Monad`(inheriting from `Applicative` and declaring the `bind` and `join` methods and the `fail` classmethod).

### Failable computation
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

### Linked list

The "linkedlist" module implement a singly linked list, as well as a lazy version 
which stores its tail as a "suspended computation", a thunk which is cached once evaluated
(subsequent evaluations returning the cached value).
A generator or iterator can be transformed into a lazy list even if the generated sequence is infinite.
The linked list will be constructed incrementally as required. Of course, in this case,
the linked list will consume more and more memory as the list grow and the generator is consumed, 
unless the heads of the list are freed at the same time.

## Pattern matching

Yet another pattern matching attempt in Python.

Python would be a strictly better language with pattern matching natively supported,
and despite all the various hacks and attempts at implementing some form of it by the community,
there's not a single PEP for it.

My implementation use context managers, of course.
It's a bit heavy on the boilerplate for my taste, but it doesn't
use any ast/compile hack.

Example

~~~
a = 
~~~
