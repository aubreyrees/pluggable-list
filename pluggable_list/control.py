"""
This file is part of the Python module "pl_obj" and implements
callback handling functionallity and some utility functions.


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

import contextlib
from .constants import (
    DATA_ATTR, GET_HOOK, SET_HOOK, REMOVE_HOOK, SORT_HOOK,
    BEGIN_OPERATION_HOOK, END_OPERATION_HOOK, REVERT_HOOK
)
from .exceptions import CallbackDoesNotExist


class ListProxy:
    def __init__(self, real_list):
        self._real_list = real_list

    def __getitem__(self, spec):
        return self._real_list[spec]

    def __iter__(self):
        return iter(self._real_list)


class Control:
    """
    A instance of the Control class encapsulates callback state and
    functionallity for a PluggableList class as well as providing some
    utility methods
    """
    def __init__(self, list_cls, callbacks):
        self._list_cls = list_cls
        self._callbacks = callbacks

    def get_callback(self, hook):
        """
        Return the callback for hook `hook`.
        """
        try:
            return self._callbacks[hook]
        except KeyError:
            raise CallbackDoesNotExist(hook)

    def has_callback(self, hook):
        """
        Return true if this Control object's pluggable list has a callback for
        hook `hook`.
        """
        return self._callbacks.get(hook) is not None

    def invoke_callback(self, hook, pl_obj, *args, **kwargs):
        try:
            callback_func = self._callbacks[hook]
        except KeyError:
            raise CallbackDoesNotExist(hook)
        else:
            proxy = ListProxy(getattr(pl_obj, DATA_ATTR))
            return callback_func(pl_obj, hook, proxy, *args, **kwargs)

    def invoke_callback_safe(self, default):
        def invoke(hook, pl_obj, *args, **kwargs):
            try:
                callback_func = self._callbacks[hook]
            except KeyError:
                return default
            else:
                proxy = ListProxy(getattr(pl_obj, DATA_ATTR))
                return callback_func(pl_obj, hook, proxy, *args, **kwargs)

        return invoke

    def _revert(self, pl_obj):
        self.invoke_callback_safe(None)(REVERT_HOOK, pl_obj)

    @contextlib.contextmanager
    def op(self, pl_obj, *, modify=False, fetch=False, safe=False):
        """
        Context manager that runs a code that interacts with the internal data
        structure in a safe context. before the code is run any
        begin_operation callback is run, then the code is run. If an excepion
        is raised and the operation has declared it is modifying the data
        structure, any changes are reverted. Finally the end_operation
        callback is if one exists.
        """
        if modify:
            save_point = getattr(pl_obj, DATA_ATTR).copy()

        invoked_callbacks = []

        def invoke(hook, *args, **kwargs):
            result = self.invoke_callback(hook, pl_obj, *args, **kwargs)
            invoked_callbacks.append((hook, args, kwargs))
            return result

        def invoke_safe(default):
            def func(hook, *args, **kwargs):
                try:
                    return invoke(hook, *args, **kwargs)
                except CallbackDoesNotExist:
                    return default
            return func

        self.invoke_callback_safe(None)(
            BEGIN_OPERATION_HOOK, pl_obj, modify=modify, fetch=fetch
        )

        if safe:
            func = invoke_safe
        else:
            func = invoke

        try:
            yield func
        except:
            if modify:
                self._revert(pl_obj)
                setattr(pl_obj, DATA_ATTR, save_point)
            raise
        finally:
            self.invoke_callback_safe(None)(END_OPERATION_HOOK, pl_obj)
