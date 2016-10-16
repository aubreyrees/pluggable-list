import string
import inspect
import itertools as it
import pytest
from contextlib import contextmanager


import pluggable_list
from pluggable_list.bases import BasePluggableList, CallbackMixin
from pluggable_list.constants import (
    DATA_ATTR, GET_HOOK, SET_HOOK, REMOVE_HOOK, SORT_HOOK,
    BEGIN_OPERATION_HOOK, END_OPERATION_HOOK, REVERT_HOOK
)


# PREAMBLE
# hooks are below (/HOOKS)


HOOKS = ('set', 'get', 'remove', 'sort', 'begin_operation', 'end_operation', 'revert')
HOOK_PERMS = tuple(
    it.chain.from_iterable(it.combinations(HOOKS, x) for x in range(len(HOOKS) + 1))
)


class Registry:
    """
    Helper mixin for callbacks to register there invocation
    """
    def __init__(self, *args, **kwargs):
        self.registry = []
        super().__init__(*args, **kwargs)

    def register(self, name, *args, **kwargs):
        """
        Register that callback `name` has been called with args `args`
        and kwarg `kwargs`
        """
        self.registry.append((name, list(args), kwargs))


def make_callback(name):
    """ 
    Build a callback for the hook `name`. The only non-required action
    this callback performs is to add an entry to the class's registry
    so we can see the callback has been called later.
    """
    def callback(self, hook, proxy, *args, **kwargs):
        self.register(name, hook, list(proxy), *args, **kwargs)
        if name in ('set', 'get', 'sort','remove'):
            return args[1]

    return callback


def make_callback_attrs(hooks):
    """
    Makes a dictionary containing callbacks for all hooks in iterable `hooks`.
    `hooks` is also set as the `registered_callbacks` attr so we can inspect
    it later.
    """
    def wrapped_callback(hook):
        wrapper = getattr(pluggable_list, hook + '_callback')()
        return wrapper(make_callback(hook))

    hooks = set(hooks)

    attrs = {n + '_cb': wrapped_callback(n) for n in hooks}
    attrs['registered_callbacks'] = hooks

    return attrs


class Constructor:
    """
    A class that returns a generated class when called.
    """
    def __init__(self, bases, hooks):
        self._bases = bases
        self._hooks = hooks

    def __call__(self):
        return type(
            'CustomListClass',
            tuple(it.chain((Registry,), self._bases)), 
            make_callback_attrs(self._hooks)
        )

    def __repr__(self):
        return (
            "Constructor: bases: {}, callbacks: {}"
            .format(self._bases, self._hooks)
        )


def make_list_class(bases):
    def fixture_func(request):
        return Constructor(bases, request.param)

    return fixture_func


def callback_attrs_fixture(name):
    fixture_wrapper = pytest.fixture(name=name, params=HOOK_PERMS)
    return fixture_wrapper(lambda request: make_callback_attrs(request.param))


def callback_mixin_class_fixture(name):
    fixture_wrapper = pytest.fixture(name=name, params=HOOK_PERMS)
    return fixture_wrapper(make_list_class([CallbackMixin]))


def custom_list_class_fixture(name, bases):
    fixture_wrapper = pytest.fixture(name=name, params=HOOK_PERMS)
    return fixture_wrapper(make_list_class(bases))


def custom_baselist_class_fixture(name, mixins):
    bases = [BasePluggableList]
    bases.extend(mixins)
    return custom_list_class_fixture(name, bases)


class FunctionTestRig:
    """
    In addition in may be stipulated that invoking the method on the real
    list may cause an exception by passing an iterable of exception types as
    the `allowed_exceptions` argument. Then if invoking the method on the real
    list raises and exception in `allowed_exceptions` then invoking the method
    on the built list must raise the same exception (not just an exception in
    `allowed_exceptions, but the same exception as the on raised by the real
    list).
    """

    def __init__(self, cls, elements, *, allowed_exceptions=None):
        self._cls = cls
        self._elements = list(elements)
        self.obj = cls(self._elements)
        self.real_list = list(self._elements)

        if allowed_exceptions is None:
            self._allowed_exceptions = tuple()
        else:
            self._allowed_exceptions = tuple(allowed_exceptions)

    def assert_equiv(self, func_name, *args, **kwargs):
        try:
            r1 = getattr(self.real_list, func_name)(*args, **kwargs)
        except Exception as exp:
            if isinstance(exp, self._allowed_exceptions):
                with pytest.raises(
                        exp.__class__,
                        message=(
                            'invoking func on real list caused a '
                            '`{}` but the same operation on the '
                            'built list did not.'
                            .format(exp)
                        )
                ):
                    getattr(self.obj, func_name)(*args, **kwargs)
            else:
                raise
        else:
            r2 = getattr(self.obj, func_name)(*args, **kwargs)
            assert r1 == r2, (
                "Return value from actual list and built list did no match"
            )

        assert list(self.obj) == self.real_list, (
            "Actual list and built list have different entries after "
            "calling `{}` (either different order or different values)."
            .format(func_name)
        )


class CallbackTestRig:
    def __init__(self, list_cls, elements):
        self._elements = list(elements)
        self._list_cls = list_cls
        self.obj = list_cls(self._elements)

    def invoke(self, func_name, op_type, *args, **kwargs):
        with self._check_begin_op_callback(op_type):
            getattr(self.obj, func_name)(*args, **kwargs)

        self._check_end_op_callback()

    @contextmanager
    def _check_callbacks(self, expected_callbacks):
        start_count = len(self.obj.registry)

        yield

        new_callback_count = len(self.obj.registry) - start_count

        expected_and_possible_callbacks = [
            cb for cb in expected_callbacks
            if cb[0] in self.obj.registered_callbacks
        ]

        if new_callback_count == 0:
            assert len(expected_and_possible_callbacks) == 0
        else:
            new_callbacks = [
                cb for cb in
                self.obj.registry[-new_callback_count:]
                if cb[0] not in ('begin_operation', 'end_operation')
            ]

            assert expected_and_possible_callbacks == new_callbacks

    @contextmanager
    def _check_begin_op_callback(self, op_type):
        if  'begin_operation' in self.obj.registered_callbacks:
            start_count = len(self.obj.registry)
            data_copy = getattr(self.obj, DATA_ATTR).copy()
            yield
            assert self.obj.registry[start_count] == begin_op_cb(data_copy, op_type)
        else:
            yield

    def _check_end_op_callback(self):
        if 'end_operation' in self.obj.registered_callbacks:
            assert self.obj.registry[-1] == end_op_cb(getattr(self.obj, DATA_ATTR).copy())
    
    @contextmanager
    def assert_op_callbacks(self, op_type, expected_callbacks):
        with self._check_callbacks(expected_callbacks):
            with self._check_begin_op_callback(op_type):
                yield

        self._check_end_op_callback()

    @contextmanager
    def assert_callbacks(self, expected_callbacks):
        with self._check_callbacks(expected_callbacks):
            yield self.invoke

                

def get_cb(proxy, idx, value):
    """
    Build the expected registry entry for a get callback.
    """
    return ('get', [GET_HOOK, list(proxy), idx, value], {})


def set_cb(proxy, idx, value):
    """
    Build the expected registry entry for a set callback.
    """
    return ('set', [SET_HOOK, list(proxy), idx, value], {})


def remove_cb(proxy, idx, value):
    """
    Build the expected registry entry for a remove callback.
    """
    return ('remove', [REMOVE_HOOK, list(proxy), idx, value], {})


def sort_cb(proxy, value):
    """
    Build the expected registry entry for a sort callback.
    """
    return ('sort', [SORT_HOOK, list(proxy), value], {})


def begin_op_cb(proxy, op_type):
    kwargs = {k: k in op_type for k in ('modify', 'fetch')}
    return ('begin_operation', [BEGIN_OPERATION_HOOK, list(proxy)], kwargs)


def end_op_cb(proxy):
    return ('end_operation', [END_OPERATION_HOOK, list(proxy)], {})


def revert_cb(proxy):
    return ('revert', [REVERT_HOOK, list(proxy)], {})


CB_CONSTRUCTOR = {
    'get': get_cb,
    'remove': remove_cb,
    'set': set_cb,
    'sort': sort_cb,
    'begin_operation': begin_op_cb,
    'end_operation': end_op_cb,
    'revert': revert_cb,
}


def cb_seq(*callbacks):
    return [
        CB_CONSTRUCTOR[cb](x)
        for cb, xs in callbacks
        for x in xs
    ]


class Namespace:
    pass


def lr(a, b=None):
    """
    *l*etter *r*ange. Create a list container the first `a` letters if `b` is
    None or a sequence of the `a`th to be `b-1`th letters if b is not none.
    Letters are English, lowercase letters are in standard order.
    """
    if b is None:
        return [string.ascii_lowercase[n] for n in range(a)]
    else:
        return [string.ascii_lowercase[n] for n in range(a, b)]


def set_element_feed():
    for c in string.ascii_uppercase:
        yield c


def test_sequences(n, decr=False, safe=False):
    if decr:
        return [(range(n - 1, -1, -1), lr(n))]
    elif safe:
        return [(range(n), lr(n))]
    else:
        return [(range(-1, n + 2), lr(n))]

    return it.chain.from_iterable(
        it.product(range(n), repeat=x) for x in range(n)
    )


def index_sequences(n, decr=False):
    if decr:
        return [range(n - 1, -1, -1)]
    else:
        return [range(n)]


def value_sequences(n):
    return [
        tuple(string.ascii_lowercase[x] for x in range(n)),
    ]


def access_seq_iter(access_seq, shifting=False):
    if shifting:
        removed = set()
        for access_idx in access_seq:
            yield access_idx - sum(1 for x in removed if x < access_idx)
            removed.add(access_idx)
    else:
        for access_idx in access_seq:
            yield access_idx


def build_remove_cb_seq(value_seq, access_seq, shifting=False):
    callbacks = []
    pointer = value_seq

    for target in access_seq_iter(access_seq, shifting=shifting):
        proxy = pointer.copy()
        pointer = proxy
        callbacks.append(remove_cb(proxy, target, proxy[target]))
        del proxy[target]
    
    return callbacks


def build_set_cb_seq(value_seq, access_seq, set_seq):
    callbacks = []
    pointer = value_seq

    for access_ele, set_ele in zip(access_seq, set_seq):
        proxy = pointer.copy()
        pointer = proxy
        callbacks.append(set_cb(proxy, access_ele, set_ele))
        proxy.insert(access_ele, set_ele)
    
    return callbacks


# HOOKS


def pytest_namespace():
    ns = Namespace()
    
    ns.callback_attrs_fixture = callback_attrs_fixture
    ns.custom_list_class_fixture = custom_list_class_fixture
    ns.callback_mixin_class_fixture = callback_mixin_class_fixture
    ns.custom_baselist_class_fixture = custom_baselist_class_fixture
    ns.lr = lr
    ns.test_sequences = test_sequences
    ns.value_sequences = value_sequences
    ns.index_sequences = index_sequences
    ns.get_cb = get_cb
    ns.set_cb = set_cb
    ns.remove_cb = remove_cb
    ns.sort_cb = sort_cb
    ns.cb_seq = cb_seq
    ns.callback_test_rig = CallbackTestRig
    ns.function_test_rig = FunctionTestRig
    ns.build_remove_cb_seq = build_remove_cb_seq
    ns.build_set_cb_seq = build_set_cb_seq
    ns.set_element_feed = set_element_feed

    return {
        'pluggable_list': ns
    }
