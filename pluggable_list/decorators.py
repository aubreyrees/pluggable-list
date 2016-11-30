"""
This file is part of the Python module "pluggable_list" and implements
decorators for assigning meta data to methods.


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

from .constants import REGISTER_ATTR, Hook


def _register_hook(func, hook):
    try:
        register = getattr(func, REGISTER_ATTR)
    except AttributeError:
        register = set()
        setattr(func, REGISTER_ATTR, register)

    register.add(hook)

def get_callback():
    """
    Method decorator that marks the method as a get callback. Must return the
    value to be returned.
    """
    def wrapper(func):
        """
        Set a flag on the method `func` so that when the method's class is
        created the creater knows to register the method as a get callback.
        """
        _register_hook(func, Hook.get)
        return func
    return wrapper


def set_callback():
    """
    Method decorator that marks the method as a set callback. Must return the
    value that is be added to the list.
    """
    def wrapper(func):
        """
        Set a flag on the method `func` so that when the method's class is
        created the creater knows to register the method as a set callback.
        """
        _register_hook(func, Hook.set)
        return func
    return wrapper


def remove_callback():
    """
    Method decorator that marks the method as a del callback. No return value
    is expected.
    """
    def wrapper(func):
        """
        Set a flag on the method `func` so that when the method's class is
        created the creater knows to register the method as a del callback.
        """
        _register_hook(func, Hook.remove)
        return func
    return wrapper


def sort_callback():
    """
    Method decorator that marks the method as a sort callback. No return value
    is expected.
    """
    def wrapper(func):
        """
        Set a flag on the method `func` so that when the method's class is
        created the creater knows to register the method as a sort callback.
        """
        _register_hook(func, Hook.sort)
        return func
    return wrapper


def begin_operation_callback():
    """
    Method decorator that marks the method as a begin operation callback. No
    return value is expected.
    """
    def wrapper(func):
        """
        Set a flag on the method `func` so that when the method's class is
        created the creater knows to register the method as a begin operation
        callback.
        """
        _register_hook(func, Hook.begin_operation)
        return func
    return wrapper


def end_operation_callback():
    """
    Method decorator that marks the method as a end operation callback. No
    return value is expected.
    """
    def wrapper(func):
        """
        Set a flag on the method `func` so that when the method's class is
        created the creater knows to register the method as a end operation
        callback.
        """
        _register_hook(func, Hook.end_operation)
        return func
    return wrapper


def revert_callback():
    """
    Method decorator that marks the method as a revert callback. No return
    value is expected.
    """
    def wrapper(func):
        """
        Set a flag on the method `func` so that when the method's class is
        created the creater knows to register the method as a revert callback.
        """
        _register_hook(func, Hook.revert)
        return func
    return wrapper
