import pytest
from pluggable_list.bases import ClearMixin


l = pytest.pluggable_list


clearable_list_fixture = l.custom_baselist_class_fixture(
    'clearable_list', (ClearMixin,)
)


def test_clear(clearable_list):
    """
    Test clear().
    """
    rig = l.function_test_rig(clearable_list(), l.lr(10))
    rig.assert_equiv('clear')


def test_clear_callbacks(clearable_list):
    """
    Test callbacks invoked by clear().
    """
    value_seq = l.lr(10)
    rig = l.callback_test_rig(clearable_list(),  value_seq) 
    cbs = l.build_remove_cb_seq(value_seq, range(len(value_seq)), shifting=True)
    with rig.assert_callbacks(cbs):
        rig.invoke("clear", {'modify'})
