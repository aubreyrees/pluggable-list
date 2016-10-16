"""
This file is part of the Python module "pluggable_list" and defines
constants for this module.


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


DATA_ATTR = '_pluggable_list_data'
CONTROL_ATTR = '_pluggable_list_control'
REGISTER_ATTR = '_pluggable_list_register'
GET_HOOK = 0
SET_HOOK = 1
REMOVE_HOOK = 2
SORT_HOOK = 3
BEGIN_OPERATION_HOOK = 4
END_OPERATION_HOOK = 5
REVERT_HOOK = 6

HOOKS = {
    GET_HOOK, SET_HOOK, REMOVE_HOOK, SORT_HOOK, BEGIN_OPERATION_HOOK,
    END_OPERATION_HOOK, REVERT_HOOK
}
