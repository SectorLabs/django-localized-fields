.. _unique_together: https://docs.djangoproject.com/en/2.2/ref/models/options/#unique-together

Constraints
===========

All constraints are enforced by PostgreSQL. Constraints can be applied to all fields documented in :ref:`Fields <fields>`.

.. warning::

    Don't forget to run ``python manage.py makemigrations`` after modifying constraints.

Required/optional
-----------------


* Default language required and all other languages optional:


    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField()


* All languages are optional and the field itself can be ``None``:

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(blank=True, null=True, required=False)

* All languages are optional but the field itself cannot be ``None``:

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(blank=False, null=False, required=False)


* Make specific languages required:

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(blank=False, null=False, required=['en', 'ro'])


* Make all languages required:


    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(blank=False, null=False, required=True)


Uniqueness
----------

.. note::

    Uniqueness is enforced by PostgreSQL by creating unique indexes on hstore keys. Keep this in mind when setting up unique constraints. If you already have a unique constraint in place, you do not have to add an additional index as uniqueness is enforced by creating an index.


* Enforce uniqueness for one or more languages:

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(uniqueness=['en', 'ro'])


* Enforce uniqueness for all languages:

    .. code-block:: python

        from localized_fields.util import get_language_codes

        class MyModel(models.Model):
            title = LocalizedField(uniqueness=get_language_codes())


* Enforce uniqueness for one or more languages together:

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(uniqueness=[('en', 'ro')])

    This is similar to Django's `unique_together`_.


* Enforce uniqueness for all languages together:

    .. code-block:: python

        from localized_fields.util import get_language_codes

        class MyModel(models.Model):
            title = LocalizedField(uniqueness=[(*get_language_codes())])
