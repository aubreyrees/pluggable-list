"""
Test setter functionallity. These tests assumed __iter__ is working correctly;
if tests in test_basic.py are failing then fix those before looking at the 
results from these tests.
"""

import string
import pytest
from pluggable_list.bases import DelMixin

l = pytest.pluggable_list

remove_list_constructor_fixture = l.custom_baselist_class_fixture(
    'remove_list_constructor', (DelMixin,),
)


@pytest.mark.parametrize("access_seq,value_seq", l.test_sequences(5))
def test_pop(remove_list_constructor, value_seq, access_seq):
    """
    Test pop.
    """
    rig = l.function_test_rig(
        remove_list_constructor(),
        value_seq,
        allowed_exceptions=(IndexError,)
    )
    for n in access_seq:
        rig.assert_equiv('__delitem__', n)


@pytest.mark.parametrize("access_seq,value_seq", l.test_sequences(5))
def test_del_single_item(remove_list_constructor, value_seq, access_seq):
    """
    Test __delitem__ with integer parameter
    """
    rig = l.function_test_rig(
        remove_list_constructor(),
        value_seq,
        allowed_exceptions=(IndexError,),
    )
    for n in access_seq:
        rig.assert_equiv('__delitem__', n)


@pytest.mark.parametrize(
    "slice_params",
    [
       (None, None, None),
       (5, None, None),
       (None, 3, None),
       (2, 5, None),
       (2, 2, None),
       (3, 1, None),
       (None, None, 3),
       (2, None, 3),
       (None, 6, 2),
       (2, 8, 3),
    ]
)
def test_del_slice(remove_list_constructor, slice_params):
    """
    Test __delitem__ with slice parameter
    """
    rig = l.function_test_rig(remove_list_constructor(), l.lr(10))
    rig.assert_equiv('__delitem__', slice(*slice_params))


@pytest.mark.parametrize("access_seq,value_seq", l.test_sequences(4, decr=True))
def test_del_single_item_callbacks(remove_list_constructor, value_seq, access_seq):
    """
    Test what callbacks are invoked when __delitem__ is invoked with an
    integer.
    """
    rig = l.callback_test_rig(remove_list_constructor(), value_seq)
    cbs = l.build_remove_cb_seq(value_seq, access_seq)
    with rig.assert_callbacks(cbs) as invoke:
        for n in access_seq:
            invoke('__delitem__', {'modify'}, n)


@pytest.mark.parametrize("access_seq,value_seq", l.test_sequences(4, decr=True))
def test_pop_callbacks(remove_list_constructor, value_seq, access_seq):
    """
    Test what callbacks are invoked when pop is invoked.
    """
    rig = l.callback_test_rig(remove_list_constructor(), value_seq)
    cbs = l.build_remove_cb_seq(value_seq, access_seq)
    with rig.assert_callbacks(cbs) as invoke:
        for n in access_seq:
            invoke('pop', {'modify', 'fetch'}, n)


@pytest.mark.parametrize(
    "slice_params,target_indices",
    [
        ((None, None, None), range(10)),
        ((2, None, None),    range(2, 10)),
        ((None, 3, None),    range(0, 3)),
        ((2, 5, None),       range(2, 5)),
        ((2, 2, None),       []),
        ((4, 1, None),       []),
        ((None, None, 3),    (0, 3, 6, 9)),
        ((2, None, 3),       (2, 5, 8)),
        ((None, 6, 2),       (0, 2, 4)),
        ((2, 8, 3),          (2, 5)),
    ]
)
def test_del_slice_callbacks(remove_list_constructor, slice_params, target_indices):
    """
    Test what callbacks are invoked when __delitem__ is invoked with a slice.
    """
    seq = l.lr(10)
    rig = l.callback_test_rig(remove_list_constructor(), seq)
   
    cbs = l.build_remove_cb_seq(seq, target_indices, shifting=True)
    with rig.assert_callbacks(cbs) as invoke:
        invoke('__delitem__', {'modify'}, slice(*slice_params))
