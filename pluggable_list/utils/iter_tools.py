"""
Functions to help with various iteration operations.

Copyright (C) 2016 Aubrey Stark-Tooller <aubrey@deepearth.uk>

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


import functools
from ..constants import REGISTER_ATTR
from ..exceptions import TooFewValues, TooManyValues


def insertions(list_len, start, step, iterable_obj):
    """
    Iterator that yields pairs where the second value of the pair is a value
    yielded from `iterable_obj` and first is the index in a target list at
    which the value should be inserted.

    `list_len` is the initial size of the target list, `start` is the position
    at which to start inserting elements in the target list and `step` is the
    number of elements between insert points.

    It is assumed that a once position and value have been yielded the caller
    will do the insert (and only this insert) and future indices yielded by
    this generator will reflect this expected alteration.

    The iterator will stop when `value_iter` has no more values to yield.
    If the position at which the next value would be inserted is beyond
    the target list then TooManyValues exception is raised.
    """
    idx = start
    list_len = list_len
    step = step
    iterator = iter(iterable_obj)
    count = 0

    while True:
        if idx < 0 or idx > list_len:
            remaining = sum(1 for _ in iterator)
            if remaining != 0:
                raise TooManyValues(count + remaining)
            else:
                raise StopIteration()
        else:
            current_idx = idx
            # it's fine if this raises StopIteration
            value = next(iterator)

            count += 1
            list_len += 1
            idx += step

            yield current_idx, value


def del_indices(indices):
    """
    Generator that yields indices from the strictly monotone sequence
    `indices` and adjusts them to compensates for deletions happening
    during iteration by making the assumption that the element at a
    yielded index is removed (and only this element is removed) before
    the element at the next yielded index is removed.
    """
    if len(indices) > 1 and indices[0] < indices[1]:
        for count, idx in enumerate(indices):
            yield idx - count
    else:
        for idx in indices:
            yield idx


def yield_from(iterable_obj):
    """
    Yield all values in `iterator`.
    """
    for value in iterable_obj:
        yield value


def _iter_func_with_max(max_len, iterator):
    """
    Generator that yields at most `max_len` values from `iterator`. If the
    iterator yields more values than `max_len` a `TooManyValues` exception is
    raised.
    """
    count = 0
    for value in iterator:
        count += 1
        if count <= max_len:
            yield value
        else:
            raise TooManyValues(count + sum(1 for _ in iterator))


def restricted_iter(min_len, max_len, iterable_obj):
    """
    Generator that yields values from `iterable_obj` and:
    * if `min_len` is not None, raises a `TooFewValues` exception if
      `iterable_obj` has yielded all values and the number of values
      is stricly less than `min_len`;
    * if `max_len` is not None, raises a `TooManyValues` exception if the
      number of values yield by `iterable_obj` is strictly greater than
      `max_len`.
    """
    if max_len is None:
        iter_func = yield_from
    else:
        iter_func = functools.partial(_iter_func_with_max, max_len)

    count = 1
    iterator = iter(iterable_obj)

    for count, value in enumerate(iter_func(iterator), start=1):
        yield value

    if min_len is not None and count < min_len:
        raise TooFewValues(count)


def attrs_with_a_register(attrs):
    """
    Generator that yields any attribute in the `attr` dict that
    is a callable and has a register attribute that is not None.
    """
    for name, attr in attrs.items():
        if callable(attr):
            register = getattr(attr, REGISTER_ATTR, None)
            if register is not None:
                yield name, attr, register
