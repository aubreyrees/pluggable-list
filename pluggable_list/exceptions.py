"""
This file is part of the Python module "pluggable_list" and implements
exception classes for this module


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


class CallbackDoesNotExist(Exception):
    """
    Raised when a callback that is not defined is called.
    """
    pass


class UnknownHook(Exception):
    """
    Raised when an attempt is made to register a hook of an unknown type.
    """
    def __init__(self, hook, func):
        self.hook = hook
        self.func = func
        super().__init__()


class HookAlreadyRegistered(Exception):
    """
    Raised when an attempt is made to register a hook that has already been
    registered.
    """
    def __init__(self, hook):
        self.hook = hook
        super().__init__()


class ToFewValues(Exception):
    """
    Called when to few values are given for an operation.
    """
    def __init__(self, count):
        self.count = count
        super().__init__()


class ToManyValues(Exception):
    """
    Called when to many values are given for an operation.
    """
    def __init__(self, count):
        self.count = count
        super().__init__()
