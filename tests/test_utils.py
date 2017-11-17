from wagtail_extensions.utils import first_true, nth, true_or_nth


def test_first_true_empty():
    out = first_true([])
    assert out == None


def test_first_true_default():
    out = first_true([], default='fish')
    assert out == 'fish'


def test_first_true_match():
    match = {'match': True}
    items = [{}, match]
    item = first_true(items, predicate=lambda x: x.get('match') == True)
    assert item == match


def test_first_true_nomatch():
    items = [{'match': False}, {'another': 5}]
    item = first_true(items, predicate=lambda x: x.get('match') == True)
    assert item == None


def test_true_or_nth_nomatch():
    first = {'match': False}
    items = [first, {'another': 5}]
    item = true_or_nth(items, predicate=lambda x: x.get('match') == True)
    assert item == first


def test_nth_empty():
    out = nth([], 2)
    assert out == None


def test_nth_default():
    out = nth([], 2, default=5)
    assert out == 5


def test_nth_works():
    out = nth([1, 2, 3, 4, 5], 2)
    assert out == 3
