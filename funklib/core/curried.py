from funklib.core.functoid import functoid
import funklib.core.prelude as prelude
import operator as op

std_filter = filter
std_map = map

@functoid
def filter(pred):
    return functoid(std_filter, pred)

@functoid
def map(f):
    return functoid(std_map, f)

@functoid
def contained(container):
    return functoid(op.contains, container)


@functoid
def keyfilter(pred):
    return functoid(prelude.keyfilter, pred)
