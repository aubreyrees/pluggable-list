"""
Test setter functionallity. These tests assumed __iter__ is working correctly;
if tests in test_basic.py are failing then fix those before looking at the 
results from these tests.
"""

import itertools as it
import string
import pytest
from pluggable_list.bases import SetItemMixin, AppendMixin, InsertMixin


l = pytest.pluggable_list

fset_item_constructor_fixture = l.custom_baselist_class_fixture(
    'set_item_constructor', (SetItemMixin,),
)

append_list_constructor_fixture = l.custom_baselist_class_fixture(
    'append_list_constructor', (AppendMixin,),
)


insert_list_constructor_fixture = l.custom_baselist_class_fixture(
    'insert_list_constructor', (InsertMixin,),
)


@pytest.mark.parametrize("access_seq,value_seq", l.test_sequences(5))
def test_set_single_item(set_item_constructor, access_seq, value_seq):
    """
    Test __setitem__ with integer parameter
    """
    rig = l.function_test_rig(
        set_item_constructor(),
        value_seq,
        allowed_exceptions=(IndexError,)
    )
    feed = l.set_element_feed()
    for n in access_seq:
        rig.assert_equiv('__setitem__', n, next(feed))


@pytest.mark.parametrize(
    "slice_params,count", 
    [
       ((None, None, None), 4),
       ((5, None, None), 4),
       ((None, 3, None), 4),
       ((2, 5, None), 5),

       ((None, None, 3), 4),
       ((2, None, 3), 3),
       ((None, 6, 2), 3),
       ((2, 8, 3), 2),

       ((None, None, -3), 4),
       ((7, None, -3), 3),
       ((None, 1, -4), 2),
       ((8, 2, -2), 3),

       ((-4, None, None), 4),
       ((None, -3, None), 7),
       ((-5, -2, None), 3),
       ((-5, 9, None), 4),
       ((6, -2, None), 2),

       ((-5, None, 3), 2),
       ((None, -4, 4), 2),
       ((-6, -1, 2), 3),
       ((-7, 8, 2), 3),
       ((2, -6, 2), 1),

       ((-2, None, -2), 5),
       ((None, -4, -3), 2),
       ((-2, -7, -2), 3),
       ((-2, 4, -1), 4),
       ((9, -7, -2), 3),

       ((2, 2, None), 3),
       ((3, 1, None), 6),
       ((-4, -5, None), 2),
       ((-4, 2, None), 5),
       ((7, -6, None), 4),
       ((-1000000, None, None), 4),
       ((None, 1000000000, None), 5),
       ((-300035345, 1000000000, None), 3),

       ((None,None,3), 0),
       ((None,None,3), 0),
       ((2, None, 3), 0),
       ((2, None, 3), 0),
       ((None, 6, 2), 0),
       ((None, 6, 2), 0),
       ((2, 8, 3), 0),
       ((2, 8, 3), 0),
       ((2, 2, 3), 0),
       ((3, 1, 3), 0),

       ((None,None,3), 1),
       ((None,None,3), 10),
       ((2, None, 3), 1),
       ((2, None, 3), 3),
       ((None, 6, 2), 2),
       ((None, 6, 2), 5),
       ((2, 8, 3), 1),
       ((2, 8, 3), 4),
       ((2, 2, 3), 4),
       ((3, 1, 3), 4),
    ]
)
def test_setitem_with_slice(set_item_constructor, slice_params, count):
    """
    Test __setitem__ with slice parameter
    """
    value_seq = l.lr(10)
    rig = l.function_test_rig(
        set_item_constructor(),
        value_seq,
        allowed_exceptions=(ValueError,)
    )
    feed = l.set_element_feed()
    rig.assert_equiv('__setitem__', slice(*slice_params), [next(feed) for _ in range(count)])


@pytest.mark.parametrize("value_seq", l.value_sequences(4))
def test_append(append_list_constructor, value_seq):
    """
    Test append
    """
    rig = l.function_test_rig(append_list_constructor(), value_seq)
    feed = l.set_element_feed()
    for _ in range(10):
        rig.assert_equiv('append', next(feed))


@pytest.mark.parametrize("value_seq", l.value_sequences(4))
def test_extend(append_list_constructor, value_seq):
    """
    Test extend
    """
    rig = l.function_test_rig(append_list_constructor(), value_seq)
    feed = l.set_element_feed()
    for n in range(3):
        rig.assert_equiv('extend', [next(feed) for _ in range(5)])


@pytest.mark.parametrize("access_seq,value_seq", l.test_sequences(4))
def test_insert(insert_list_constructor, access_seq, value_seq):
    """
    Test insert.
    """
    rig = l.function_test_rig(insert_list_constructor(), value_seq)
    feed = l.set_element_feed()
    for n in access_seq:
        rig.assert_equiv('insert', n, next(feed))


@pytest.mark.parametrize("access_seq,value_seq", l.test_sequences(4, safe=True))
def test_set_single_item_callbacks(set_item_constructor, access_seq, value_seq):
    """
    Test what callbacks are invoked when __setitem__ is invoked with an
    integer.
    """
    rig = l.callback_test_rig(set_item_constructor(), value_seq)
    feed = l.set_element_feed()

    pointer = value_seq

    for n in access_seq:
        value_to_set = next(feed)

        proxy = pointer.copy()
        pointer = proxy

        expected_callbacks = [l.remove_cb(proxy, n, proxy[n])]

        proxy = pointer.copy()
        pointer = proxy

        del proxy[n]

        expected_callbacks.append(l.set_cb(proxy, n, value_to_set))

        proxy.insert(n, value_to_set)

        with rig.assert_callbacks(expected_callbacks) as invoke:
            invoke('__setitem__', {'modify'}, n, value_to_set)



@pytest.mark.parametrize(
    "slice_params,del_targets,set_targets",
    [
        ((2, None, None),   range(2, 10), range(2, 6)),
        ((None, 3, None),   range(3),     range(4)),
        ((2, 5, None),      range(2, 5),  range(2, 7)),
        ((2, 2, None),      [],           range(2, 6)),
        ((4, 1, None),      [],           range(4, 8)),
        ((None, None, 3),   (0, 3, 6, 9), (0, 3, 6, 9)),
        ((2, None, 3),      (2, 5, 8),    (2, 5, 8)),
        ((None, 6, 2),      (0, 2, 4),    (0, 2, 4)),
        ((2, 8, 3),         (2, 5),       (2, 5)),
    ]
)
def test_setitem_callbacks_with_slice(set_item_constructor, slice_params,
                                      del_targets, set_targets):
    """
    Test what callbacks are invoked when __setitem__ is invoked with a slice.
    """
    value_seq = l.lr(10)

    set_targets = list(set_targets)
    value_to_set = list(it.islice(l.set_element_feed(), len(set_targets)))
    rig = l.callback_test_rig(set_item_constructor(), value_seq)

    set_value_seq = value_seq.copy()
    del set_value_seq[slice(*slice_params)]

    callbacks = (
        l.build_remove_cb_seq(value_seq, del_targets, shifting=True) +
        l.build_set_cb_seq(set_value_seq, set_targets, value_to_set)
    )
    with rig.assert_callbacks(callbacks) as invoke:
        invoke('__setitem__', {'modify'}, slice(*slice_params), value_to_set)



@pytest.mark.parametrize("value_seq", l.value_sequences(4))
def test_append_callbacks(append_list_constructor, value_seq):
    """
    Test what callbacks are invoked when append is invoked.
    """
    rig = l.callback_test_rig(append_list_constructor(), value_seq)
    feed = l.set_element_feed()
    pointer = list(value_seq)

    for _ in range(5):
        value_to_set = next(feed)
        proxy = pointer.copy()
        pointer = proxy

        with rig.assert_callbacks([l.set_cb(proxy, len(proxy), value_to_set)]) as invoke:
            invoke("append", {"modify"}, value_to_set)

        proxy.append(value_to_set)
    

@pytest.mark.parametrize("value_seq", l.value_sequences(4))
def test_extend_callbacks(append_list_constructor, value_seq):
    """
    Test what callbacks are invoked when extend is invoked.
    """
    rig = l.callback_test_rig(append_list_constructor(), value_seq)
    feed = l.set_element_feed()
    pointer = value_seq

    for _ in range(5):
        values_to_add = [next(feed) for _ in range(4)]

        callbacks = []
        for val in values_to_add:
            proxy = list(pointer)
            pointer = proxy

            callbacks.append(l.set_cb(proxy, len(proxy), val))
            proxy.append(val)

        with rig.assert_callbacks(callbacks) as invoke:
            invoke("extend", {"modify"}, values_to_add)


@pytest.mark.parametrize("access_seq,value_seq", l.test_sequences(4))
def test_insert_callbacks(insert_list_constructor, access_seq, value_seq):
    """
    Test insert.
    """
    rig = l.callback_test_rig(insert_list_constructor(), value_seq)
    feed = l.set_element_feed()
    pointer = value_seq

    for n in access_seq:
        value_to_insert = next(feed)

        proxy = list(pointer)
        pointer = proxy

        if n < 0:
            cb_n = max(n + len(proxy), 0)
        else:
            cb_n = min(n, len(proxy))

        with rig.assert_callbacks([l.set_cb(proxy, cb_n, value_to_insert)]) as invoke:
            invoke('insert', {'modify'}, n, value_to_insert)

        proxy.insert(n, value_to_insert)
