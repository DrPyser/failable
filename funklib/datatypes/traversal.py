from itertools import count, accumulate
from operator import add

def average(iterable):
    for i, x in zip(count(1), accumulate(iterable, add)):
        yield x/i
