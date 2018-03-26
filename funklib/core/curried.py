from funklib.core.functoid import functoid
std_filter = filter
std_map = map

@functoid
def filter(pred):
    return functoid(std_filter, pred)

@functoid
def map(f):
    return functoid(std_map, f)
