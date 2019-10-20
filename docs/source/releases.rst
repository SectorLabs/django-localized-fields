Releases
========

v6.0
----

Breaking changes
****************

* Removes support for Python 3.6 and earlier.
* Removes support for PostgreSQL 9.6 and earlier.
* Sets ``LOCALIZED_FIELDS_EXPERIMENTAL`` to ``True`` by default.

Bug fixes
*********

* Fixes a bug where ``LocalizedIntegerField`` could not be used in ``order_by``.

Other
*****

* ``LocalizedValue.translate()`` can now takes an optional ``language`` parameter.
