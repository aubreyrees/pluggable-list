import pytest


l = pytest.pluggable_list


basic_list = l.custom_baselist_class_fixture(
    'basic_list_constructor', tuple(),
)


@pytest.mark.parametrize("seq", l.value_sequences(5))
def test_iter(basic_list_constructor, seq):
    """
    Ensure init + iteration is working.
    """
    assert list(basic_list_constructor()(seq)) == list(seq)


@pytest.mark.parametrize("seq", l.index_sequences(5))
def test_getitem(basic_list_constructor, seq):
    """
    Ensure __getitem__ is returning the right values
    """
    rig = l.function_test_rig(
        basic_list_constructor(), l.lr(4), allowed_exceptions=(IndexError,)
    )
    for n in seq:
        rig.assert_equiv('__getitem__', n)


@pytest.mark.parametrize(
    "slice_params", 
    [
       (None, None, None),
       (5, None, None),
       (None, 3, None),
       (2, 5, None),

       (None, None, 3),
       (2, None, 3),
       (None, 6, 2),
       (2, 8, 3),

       (None, None, -3),
       (7, None, -3),
       (None, 1, -4),
       (8, 2, -2),

       (-4, None, None),
       (None, -3, None),
       (-5, -2, None),
       (-5, 9, None),
       (6, -2, None),

       (-5, None, 3),
       (None, -4, 4),
       (-6, -1, 2),
       (-7, 8, 2),
       (2, -6, 2),

       (-2, None, -2),
       (None, -4, -3),
       (-2, -7, -2),
       (-2, 4, -1),
       (9, -7, -2),

       (2, 2, None),
       (3, 1, None),
       (-4, -5, None),
       (-4, 2, None),
       (7, -6, None),
       (-1000000, None, None),
       (None, 1000000000, None),
       (-300035345, 1000000000, None),

       (None,None,3),
       (None,None,3),
       (2, None, 3),
       (2, None, 3),
       (None, 6, 2),
       (None, 6, 2),
       (2, 8, 3),
       (2, 8, 3),
       (2, 2, 3),
       (3, 1, 3),

       (None,None,3),
       (None,None,3),
       (2, None, 3),
       (2, None, 3),
       (None, 6, 2),
       (None, 6, 2),
       (2, 8, 3),
       (2, 8, 3),
       (2, 2, 3),
       (3, 1, 3),
    ]
)
def test_setitem_with_slice(basic_list_constructor, slice_params):
    """
    Test __setitem__ with slice parameter
    """
    value_seq = l.lr(10)
    rig = l.function_test_rig(
        basic_list_constructor(),
        value_seq,
        allowed_exceptions=(ValueError,)
    )
    rig.assert_equiv('__getitem__', slice(*slice_params))


@pytest.mark.parametrize("seq", l.value_sequences(5))
def test_eq(basic_list_constructor, seq):
    """
    Ensure __eq__ is working
    """
    cls = basic_list_constructor()
    assert cls(seq) == cls(seq)


@pytest.mark.parametrize("seq", l.value_sequences(5))
def test_iter_callbacks(basic_list_constructor, seq):
    """
    Ensure iteration is invoking the right callbacks.
    """
    rig = l.callback_test_rig(basic_list_constructor(), seq)
    iter_obj = iter(rig.obj)
    idx = 0
    for idx, value in enumerate(seq):
        with rig.assert_op_callbacks({'fetch'}, [l.get_cb(seq, idx, value)]):
            next(iter_obj)


@pytest.mark.parametrize("access_seq,value_seq", l.test_sequences(5, safe=True))
def test_getitem_callbacks(basic_list_constructor, value_seq, access_seq):
    """
    Ensure __getitem__ is invoking the right callbacks.
    """
    rig = l.callback_test_rig(basic_list_constructor(), value_seq)
    with rig.assert_callbacks(l.get_cb(value_seq, n, value_seq[n]) for n in access_seq) as invoke:
        for n in access_seq:
            invoke('__getitem__', {'fetch'}, n)


@pytest.mark.parametrize(
    "slice_params", 
    [
       (None, None, None),
       (5, None, None),
       (None, 3, None),
       (2, 5, None),

       (None, None, 3),
       (2, None, 3),
       (None, 6, 2),
       (2, 8, 3),

       (None, None, -3),
       (7, None, -3),
       (None, 1, -4),
       (8, 2, -2),

       (-4, None, None),
       (None, -3, None),
       (-5, -2, None),
       (-5, 9, None),
       (6, -2, None),

       (-5, None, 3),
       (None, -4, 4),
       (-6, -1, 2),
       (-7, 8, 2),
       (2, -6, 2),

       (-2, None, -2),
       (None, -4, -3),
       (-2, -7, -2),
       (-2, 4, -1),
       (9, -7, -2),

       (2, 2, None),
       (3, 1, None),
       (-4, -5, None),
       (-4, 2, None),
       (7, -6, None),
       (-1000000, None, None),
       (None, 1000000000, None),
       (-300035345, 1000000000, None),

       (None,None,3),
       (None,None,3),
       (2, None, 3),
       (2, None, 3),
       (None, 6, 2),
       (None, 6, 2),
       (2, 8, 3),
       (2, 8, 3),
       (2, 2, 3),
       (3, 1, 3),

       (None,None,3),
       (None,None,3),
       (2, None, 3),
       (2, None, 3),
       (None, 6, 2),
       (None, 6, 2),
       (2, 8, 3),
       (2, 8, 3),
       (2, 2, 3),
       (3, 1, 3),
    ]
)
def test_setitem_callbacks_with_slice(basic_list_constructor, slice_params):
    """
    Test __setitem__ with slice parameter
    """
    value_seq = l.lr(10)
    rig = l.callback_test_rig(basic_list_constructor(), value_seq)
    cbs = [
        l.get_cb(value_seq, n, value_seq[n])
        for n in range(*slice(*slice_params).indices(len(value_seq)))
    ]
    with rig.assert_callbacks(cbs) as invoke:
        invoke('__getitem__', {'fetch'}, slice(*slice_params))

