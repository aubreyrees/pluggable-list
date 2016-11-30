"""
This file is part of the Python module "pluggable_list" and implements
the builing blocks for pluggable list classes.


Copyright (C) 2016 Aubrey Stark-Toller <aubrey@deepearth.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


from .constants import  CONTROL_ATTR, DATA_ATTR, Hook
from .control import Control
from .utils.iter_tools import (
    insertions, attrs_with_a_register, del_indices, restricted_iter
)
from .exceptions import (
    UnknownHook, HookAlreadyRegistered, ToFewValues, ToManyValues,
    CallbackDoesNotExist
)


def get_list_attrs(pl_obj):
    """
    Return the control and data objects for a pluggable list object.
    """
    return getattr(pl_obj, CONTROL_ATTR), getattr(pl_obj, DATA_ATTR)


class PluggableListIter:
    def __init__(self, pluggable_list):
        self._pl_obj = pluggable_list
        self._idx = 0
        self._stop = False
        self._ctl, self._data = get_list_attrs(pluggable_list)

    def __iter__(self):
        return self

    def __next__(self):
        if self._stop:
            raise StopIteration()
        else:
            with self._ctl.op(self._pl_obj, fetch=True, safe=True) as invoke:
                try:
                    value = self._data[self._idx]
                except IndexError:
                    self._stop = True
                    raise StopIteration()
                else:
                    value = invoke(value)(Hook.get, self._idx, value)
                    self._idx += 1
                    return value


class PluggableListMeta(type):
    """
    Metaclass for pluggable list
    """
    def __new__(mcs, name, bases, attrs):
        callbacks = {}

        for _, attr, register in attrs_with_a_register(attrs):
            for hook in register:
                if hook in callbacks:
                    raise HookAlreadyRegistered(hook)
                elif hook in Hook:
                    callbacks[hook] = attr
                else:
                    raise UnknownHook(hook, attr)

        bases_iter = iter(bases)

        unseen_hooks = set(Hook).difference(callbacks)

        while unseen_hooks:
            try:
                base = next(bases_iter)
            except StopIteration:
                break

            try:
                ctl = getattr(base, CONTROL_ATTR)
            except AttributeError:
                pass
            else:
                found = set()
                for hook in unseen_hooks:
                    try:
                        callbacks[hook] = ctl.get_callback(hook)
                        found.add(hook)
                    except CallbackDoesNotExist:
                        pass

                unseen_hooks -= found

        new_cls = type.__new__(mcs, name, bases, attrs)
        ctl = Control(new_cls, callbacks)
        setattr(new_cls, CONTROL_ATTR, ctl)

        return new_cls


class CallbackMixin(metaclass=PluggableListMeta):
    pass


class BasePluggableList(CallbackMixin):
    """
    A base class for a class that implements a list like structure.
    Only the __getitem__, __iter__ and copy methods are implemented
    in this base class.
    """
    def __init__(self, iterable_obj=None):
        data = []
        setattr(self, DATA_ATTR, data)

        if iterable_obj is not None:
            with getattr(self, CONTROL_ATTR).op(
                self, modify=True, safe=True
            ) as invoke:
                for idx, value in enumerate(iterable_obj):
                    data.append(invoke(value)(Hook.set, idx, value))

    def copy(self):
        """
        Return a shallow copy of the pluggable list
        """
        return getattr(self, CONTROL_ATTR).create_copy(self)

    def __getitem__(self, spec):
        ctl, data = get_list_attrs(self)

        with ctl.op(self, fetch=True, safe=True) as invoke:
            def get(idx):
                value = data[idx]
                return invoke(value)(Hook.get, idx, value)

            if isinstance(spec, slice):
                return [get(idx) for idx in range(*spec.indices(len(data)))]
            else:
                return get(spec)

    def __iter__(self):
        return PluggableListIter(self)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            getattr(self, DATA_ATTR) == getattr(self, DATA_ATTR)
        )

    def __contains__(self, value):
        ctl, data = get_list_attrs(self)

        with ctl.op(self, fetch=True) as invoke:
            if ctl.has_callback(Hook.search):
                return any(invoke(Hook.search, v, value) for v in data)
            else:
                return any(v == value for v in data)


class SetItemMixin:
    """
    Mixin that provides the __setitem__ method.
    """
    def __setitem__(self, spec, value):
        ctl, data = get_list_attrs(self)

        with ctl.op(self, modify=True, safe=True) as invoke:
            if isinstance(spec, slice):
                try:
                    iter(value)
                except TypeError:
                    raise TypeError('can only assign an iterable')

                initial_len = len(data)
                indices = tuple(range(*spec.indices(initial_len)))

                strict_value_count = None

                if spec.step is not None:
                    strict_value_count = len(indices)

                    if strict_value_count == 0:
                        # this code is correct. we only enter the loop 
                        # if value is a non empty sequence, and a non 
                        # empty sequence is an error
                        for _ in value:
                            raise ValueError(
                                'attempt to assign a non-empty '
                                'sequence to extended slice of size 0'
                            )
                        else:
                            # value is an empty sequence, nothing more to do.
                            return None

                for idx in del_indices(indices):
                    invoke(None)(Hook.remove, idx, data[idx])
                    del data[idx]

                if spec.step is None or spec.step > 0:
                    if spec.start is None:
                        start = 0
                    elif spec.start < 0:
                        start = max(spec.start + initial_len, 0)
                    else:
                        start = min(spec.start, initial_len)

                    step = spec.step
                    if step is None:
                        step = 1
                else:
                    # step is not None and negative
                    start = indices[0] - len(indices) + 1
                    step = spec.step + 1

                pair_iter = restricted_iter(
                    strict_value_count,
                    strict_value_count,
                    insertions(len(data), start, step, value)
                )

                try:
                    for idx, value_to_set in pair_iter:
                        data.insert(
                            idx,
                            invoke(value_to_set)(Hook.set, idx, value_to_set)
                        )
                except (ToFewValues, ToManyValues) as exp:
                    raise ValueError(
                        'attempt to assign sequence of size {} to '
                        'extended slice of size {}'
                        .format(exp.count, strict_value_count)
                    )
            else:
                idx = len(data) + spec if spec < 0 else spec
                invoke(None)(Hook.remove, idx, data[idx])
                del data[idx]
                data.insert(idx, invoke(value)(Hook.set, idx, value))


class AppendMixin:
    """
    Mixin that provides append and extend methods
    """
    def append(self, value):
        """
        Add an item to the end of the list.
        """
        ctl, data = get_list_attrs(self)
        with ctl.op(self, modify=True, safe=True) as invoke:
            data.append(invoke(value)(Hook.set, len(data), value))


    def extend(self, iterable_obj):
        """
        Extend the list by appending all the values yield by `iterable_obj` to
        the list.
        """
        ctl, data = get_list_attrs(self)
        with ctl.op(self, safe=True, modify=True) as invoke:
            for idx, value in enumerate(iterable_obj, start=len(data)):
                data.append(invoke(value)(Hook.set, idx, value))


class InsertMixin(AppendMixin):
    """
    Mixin that provides insert, append and extend methods
    """
    def insert(self, idx, value):
        """
        Insert `value` at a given position. The first argument is the
        index of the element before which to insert. Calls `_insert` internally.
        """
        ctl, data = get_list_attrs(self)
        with ctl.op(self, modify=True, safe=True) as invoke:
            idx = max(idx + len(data), 0) if idx < 0 else min(idx, len(data))
            data.insert(idx, invoke(value)(Hook.set, idx, value))


class SetMixin(InsertMixin, SetItemMixin):
    """
    Mixin that provides all set methods
    """
    pass


class ClearMixin:
    """
    Implements the clear method.
    """
    def clear(self):
        ctl, data = get_list_attrs(self)
        with ctl.op(self, modify=True, safe=True) as invoke:
            while data:
                invoke(None)(Hook.remove, 0, data[0])
                del data[0]


class DelMixin(ClearMixin):
    """
    Mixin that implements puplic element removal methods that remove elements
    using indices (and not value searching).
    """
    def pop(self, idx=None):
        """
        Remove the operation at the given position in the list and return it.
        If no index is specified, pop removes and returns the last item in
        the list.
        """
        ctl, data = get_list_attrs(self)
        with ctl.op(self, modify=True, fetch=True, safe=True) as invoke:
            idx = len(data) if idx is None else idx
            value = data[idx]
            value = invoke(value)(Hook.remove, idx, value)
            del data[idx]

    def __delitem__(self, spec):
        ctl, data = get_list_attrs(self)

        with ctl.op(self, modify=True, safe=True) as invoke:
            if isinstance(spec, slice):
                indices = tuple(range(*spec.indices(len(data))))

                for idx in del_indices(indices):
                    invoke(None)(Hook.remove, idx, data[idx])
                    del data[idx]
            else:
                idx = len(data) + spec if spec < 0 else spec
                invoke(None)(Hook.remove, idx, data[idx])
                del data[idx]


class CountMixin:
    """
    Implements a count method.
    """
    def count(self, value):
        """
        Return the number of times x appears in the list.
        """
        ctl, data = get_list_attrs(self)

        with ctl.op(self, fetch=True) as invoke:
            if ctl.has_callback(Hook.search):
                return sum(1 for v in data if invoke(Hook.search, v, value))
            else:
                return sum(1 for v in data if v == value)


class IndexMixin:
    """
    Implements the index method.
    """
    def index(self, value):
        """
        Return the index in the list of the first item whose value is x. It is
        an error if there is no such item.
        """
        ctl, data = get_list_attrs(self)

        with ctl.op(self, fetch=True) as invoke:
            if ctl.has_callback(Hook.search):
                for idx, in_value in enumerate(data):
                    if invoke(Hook.search, in_value, value):
                        return idx
                else:
                    raise ValueError('pluggable_list.index(x): x not in list')
            else:
                for idx, in_value in enumerate(data):
                    if in_value == value:
                        return idx
                else:
                    raise ValueError('pluggable_list.index(x): x not in list')


class RemoveMixin:
    """
    Implements the remove method.
    """
    def remove(self, ex_value):
        """
        Remove the first item from the list whose value is x. It is an error
        if there is no such item.
        """
        ctl, data = get_list_attrs(self)

        with ctl.op(self, fetch=True) as invoke:
            if ctl.has_callback(Hook.search):
                for idx, in_value in enumerate(data):
                    if invoke(Hook.search, in_value, ex_value):
                        break
                else:
                    raise ValueError('pluggable_list.index(x): x not in list')
            else:
                for idx, in_value in enumerate(data):
                    if invoke(Hook.search, in_value, ex_value):
                        break
                else:
                    raise ValueError('pluggable_list.index(x): x not in list')

            try:
                invoke(Hook.remove, idx, in_value)
            except CallbackDoesNotExist:
                pass

            del data[idx]


class SearchMixin(RemoveMixin, IndexMixin, CountMixin):
    """
    Implements the remove, index and count methods
    """


class ReverseMixin:
    """
    Implements the reverse method.
    """
    def reverse(self):
        """
        Reverse the elements of the list in place.
        """
        getattr(self, DATA_ATTR).reverse()


class SortMixin(ReverseMixin):
    """
    Implements the sort and reverse methods.
    """
    def sort(self, key=None, reverse=False):
        """
        Sort the items of the list in place
        """
        def wrapper(func):
            def wrapped(value):
                value = getattr(self, CONTROL_ATTR).sort_value(self, value)
                return func(value)
            return wrapped

        if key:
            key = wrapper(key)
        else:
            key = lambda v: getattr(self, CONTROL_ATTR).sort_value(self, v)

        getattr(self, DATA_ATTR).sort(key=key, reverse=reverse)


class PluggableList(BasePluggableList, SetMixin, DelMixin, SearchMixin, SortMixin):
    """
    Implements the BasePluggableList and all mixins
    """
    pass
