import pytest
from pluggable_list.constants import REGISTER_ATTR, SET_HOOK
from pluggable_list.bases import BasePluggableList
from pluggable_list.exceptions import UnknownHook, HookAlreadyRegistered


def test_unknown_hook_registation():
    def func(self):
        pass

    setattr(func, REGISTER_ATTR, {'PIRATE_TEST_HOOK'})

    attrs = {
        'test': func
    }
    try:
        type('testcls', (BasePluggableList,), attrs)
    except Exception as exp:
        assert exp.__class__ == UnknownHook
        assert exp.hook == 'PIRATE_TEST_HOOK'


def test_hook_already_registered():
    def func1(self):
        pass

    def func2(self):
        pass

    setattr(func1, REGISTER_ATTR, {SET_HOOK})
    setattr(func2, REGISTER_ATTR, {SET_HOOK})

    attrs = {
        'test1': func1,
        'test2': func2,
    }
    try:
        type('testcls', (BasePluggableList,), attrs)
    except Exception as exp:
        assert exp.__class__ == HookAlreadyRegistered
        assert exp.hook == SET_HOOK
