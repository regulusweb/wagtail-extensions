from itertools import islice


def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(islice(iterable, n, None), default)


def first_true(iterable, predicate=None, default=None):
    """
    Returns first value for which predicate(item) is true

    If no value is found, returns default.
    """
    return next(filter(predicate, iterable), default)


def true_or_nth(iterable, predicate=None, n=0, default=None):
    """
    Returns first value for which predicate(item) is true

    If no value is found, returns the nth (n) value.

    If the iterable is empty, return default.
    """
    return first_true(iterable, predicate=predicate, default=nth(iterable, n, default=default))
