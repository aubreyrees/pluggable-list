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


import enum


DATA_ATTR = '_pluggable_list_data'
CONTROL_ATTR = '_pluggable_list_control'
REGISTER_ATTR = '_pluggable_list_register'


class Hook(enum.IntEnum):
    get = 0
    set = 1
    remove = 2
    sort = 3
    begin_operation = 4
    end_operation = 5
    revert = 6
