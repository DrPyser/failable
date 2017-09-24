from functools import wraps
from contextlib import AbstractContextManager, ExitStack, contextmanager
from abc import ABC, abstractmethod
from enum import Enum

class OptionalGeneratorContext(AbstractContextManager):
    def __init__(self, generator):
        self._gen = generator

    def __enter__(self):
        return next(self._gen)

    def __exit__(self, *excs):
        try:
            x = next(self._gen)
            return x
        except StopIteration:
            return None


def optionalcontextmanager(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return OptionalGeneratorContext(f(*args, **kwargs))
    return wrapper
        

class MatchFailure(Exception):
    """Exception raised in case of a pattern match failure"""
    pass

class MatchSuccess(Exception):
    """Exception raised in case of match success"""
    pass


class matchstatus(Enum):
    pending = 0
    failed = 1
    succeeded = 2

    

class casecontext:
    def __init__(self, match_context, pattern=None):
        self._pattern = pattern
        self._match_context = match_context

    def __enter__(self):
        self._match_context._activate(self)
        self._match_context._status = matchstatus.pending
        if self._pattern is not None:
            return patterncontext(self._pattern, self._match_context.match_value)
        else:
            return None

    def __exit__(self, tp, value, tb):
        if tp is MatchFailure:
            self._match_context._status = matchstatus.failed
            self._match_context._tried += 1
            self._match_context._exit_case()
            return True
        elif any((tp,value,tb)):
            return None
        else:
            if self._match_context._status == matchstatus.failed:
                self._match_context._tried += 1
                self._match_context._exit_case()
                return True
            else:
                self._match_context._status = matchstatus.succeeded
                self._match_context._exit_case()
                raise MatchSuccess()
            

class match:
    def __init__(self, value):
        self._matching = value
        self._tried = 0
        self._actives = []
        self._status = matchstatus.pending

    @property
    def match_value(self):
        return self._matching
    
    def case(self, pattern=None):
        """Generates a case context.
        If an extractor is provided, binds an extractor context to the 'as' clause.
        Silence MatchFailure exceptions and raise MatchSuccess if all goes okay."""        
        context = casecontext(self, pattern)
        return context
   
    def ignore(self):
        """Equivalent to self.case(ignore), introduce a context without binding anything."""
        return casecontext(self)

    def _activate(self, case):
        self._actives.append(case)

    def _exit_case(self):
        self._actives.pop()
    
    def __enter__(self):
        return self
    
    def __exit__(self, tp, value, trace):
        if tp is MatchSuccess:
            return True
        elif tp is None and value is None and trace is None:
            raise MatchFailure("No provided pattern matched value {!r}".format(self._matching)) from None


class Pattern(ABC):
    def __call__(self, x):
        return self.__match__(x)

    @abstractmethod
    def __match__(self, x):
        """Try and match its argument 
        and return a value or a tuple of values, or raise MatchFailure"""
        pass


class ClassPattern(ABC):
    @classmethod
    @abstractmethod
    def __match__(cls, x):
        """Try and match its argument 
        and return a value or a tuple of values, or raise MatchFailure"""
        pass


class StaticPattern(ABC):
    @staticmethod
    @abstractmethod
    def __match__(x):
        """Try and match its argument 
        and return a value or a tuple of values, or raise MatchFailure"""
        pass

        
def getmatch(pattern, matched):
    return pattern.__match__(matched)


def predicate_method(f):
    @wraps(f)
    def wrapper(self, arg):
        if f(self, arg):
            return arg
        else:
            raise MatchFailure()
    return wrapper

def predicate_classmethod(f):
    @wraps(f)
    def wrapper(cls, arg):
        if f(cls, arg):
            return arg
        else:
            raise MatchFailure()
    return wrapper


def predicate_function(f):
    @wraps(f)
    def wrapper(arg):
        if f(arg):
            return arg
        else:
            raise MatchFailure()
    return wrapper

class pattern(Pattern):
    """Wrapper class to wrap match functions"""
    def __init__(self, f):
        self._matchf = f

    def __match__(self, x):
        return self._matchf(x)

    def __call__(self, x):
        return patterncontext(self, x)

    @classmethod
    def from_exceptions(cls, *exceptions):
        """Generate a decorator to build an extractor 
        from a function that might fail with specified exceptions"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                try:
                    return f(*args, **kwargs)
                except exceptions:
                    raise MatchFailure() from None
            return wraps(f)(cls(wrapper))
        return decorator

    @classmethod
    def from_predicate(cls, f):
        """Generate a decorator to build an extractor from a predicate function"""
        @wraps(f)
        def wrapper(arg):
            if f(arg):
                return arg
            else:
                raise MatchFailure()
        return wraps(f)(cls(wrapper))


class patterncontext:
    """Context manager generator for creating a block
    binding the result of a successful pattern"""

    def __init__(self, pattern, value):
        self._pattern = pattern
        self._match = value

    def __match__(self, x):
        return self._pattern.__match__(x)
        
    def __enter__(self):
        return self._pattern.__match__(self._match)

    def __exit__(self, *excs):
        return None

    def __call__(self):
        return self._pattern.__match__(self._match)

    
class key(Pattern):
    def __init__(self, key):
        self._key = key

    #@Pattern.from_exceptions(KeyError, TypeError)
    def __match__(self, x):
        try:
            return x[self._key]
        except (KeyError, TypeError) as ex:
            raise MatchFailure(str(ex)) from None


def _ignore(x):
    return None
        
ignore = pattern(_ignore)
