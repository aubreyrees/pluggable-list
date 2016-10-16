import pytest
from pluggable_list.bases import ReverseMixin


l = pytest.pluggable_list


reversable_list_fixture = l.custom_baselist_class_fixture(
    'reversable_list', (ReverseMixin,)
)


@pytest.mark.parametrize("value_seq", l.value_sequences(4))
def test_reverse(reversable_list, value_seq):
    """
    Test reverse().
    """
    rig = l.function_test_rig(reversable_list(), value_seq)
    rig.assert_equiv('reverse')
