==============
Pluggable List
==============

A module that attempts to make it easy to rapidly develop custom list classes.

**Contents**

* `About`_
* `Code Status`_
* `Installation`_
* `Authors`_
* `License`_

About
=====

This module focuses on easy of alteration (and possible blocking) of values
being fetched, set, removed and customizing value comparison during searching
as well notifications for changes of indices. It does not attempt to address 
custom lists that need to alter the index of elements internally.

Execution speed while considered is not the primary driving factor for this 
module; rather it focuses on increasing speed of development and assumes that
to be used to contexts where it will be fast enough.

It implements hooks for which callbacks can be registered so a callback can
be invoked:

* with the index and value of a element fetched from list. This callback
  can alter the value before it is passed to external code, or throw
  an exception to prevent the value being retrieved.
* with a value of about to added to list, and index at which the new value
  will be inserted. This callback can alter the value before it is added 
  to the list, or throw an exception to prevent the value being added.
* with the index and value of a element about to be removed. This callback
  can alter the value before it is passed to external code (this is used, 
  for example, with the pop function), or throw an exception to prevent
  the value being removed.

These 3 callbacks are intended to handle a single fetch, addition and removal
and are called multiple times for batch operations such as extend, accessing
the list using a slice, etc.

It addition to these callbacks can be invoked:

* before and after any operation that modifies or fetches any information from
  the list is run;
* to notify that an error has occurred part way through a batch operation, as
  well as callbacks to reflect reverts to the list to get it back to it's 
  state prior to operation.

There are also callbacks that can invoked when searching and sorting the list.

Finally methods are distributed across multiple mixins to allow for partial 
implementation of the list interface.
     

Code Status
===========

This module does not a stable release yet and is currently under development.
Interfaces are mostly stable but searching and sorting functionality, as well
as some comparison operations, need finishing and tests need finalising. 2.7
support is also underway and will be done for the first stable release.

Installation
============

Supported Python versions are: 3.4 and 3.5.

To install using pip:

::

    pip install git+https://github.com/aubreystarktoller/pluggable-list.git

You can obtain the source from:

::

    https://github.com/aubreystarktoller/pluggable-list


Authors
=======

Aubrey Stark-Toller <aubrey@deepearth.uk>

License
=======

pluggable-list is licensed under the GNU General Public License Version 3. See
LICENSE for the full license.
