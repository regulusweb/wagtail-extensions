from itertools import islice


def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(islice(iterable, n, None), default)


def first_true(iterable, predicate=None, default=None):
    """
    Returns first value for which predicate(item) is true

    If no true value is found, returns the first value.

    If the iterable is empty, return default.
    """
    return next(filter(predicate, iterable), nth(iterable, 0, default=default))
