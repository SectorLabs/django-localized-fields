django-localized-fields
=======================

.. image:: https://scrutinizer-ci.com/g/SectorLabs/django-localized-fields/badges/quality-score.png
    :target: https://scrutinizer-ci.com/g/SectorLabs/django-localized-fields/

.. image:: https://scrutinizer-ci.com/g/SectorLabs/django-localized-fields/badges/coverage.png
    :target: https://scrutinizer-ci.com/g/SectorLabs/django-localized-fields/

.. image:: https://travis-ci.com/SectorLabs/django-localized-fields.svg?token=sFgxhDFpypxkMcvhRoSz&branch=master
    :target: https://travis-ci.com/SectorLabs/django-localized-fields

.. image:: https://badge.fury.io/py/django-localized-fields.svg
    :target: https://pypi.python.org/pypi/django-localized-fields

.. image:: https://img.shields.io/github/license/SectorLabs/django-localized-fields.svg

``django-localized-fields`` is an implementation of a field class for Django models that allows the field's value to be set in multiple languages. It does this by utilizing the ``hstore`` type (PostgreSQL specific), which is available as ``models.HStoreField`` in Django 1.10.

This package requires Python 3.5 or newer and Django 1.10 or newer.

In the pipeline
---------------
We're working on making this easier to setup and use. Any feedback is apreciated. Here's a short list of things we're working to improve:

* Make it unnecesarry to add anything to your `INSTALLED_APPS`.
* Move generic PostgreSQL code to a separate package.

Installation
------------
1. Install the package from PyPi:

    .. code-block:: bash

        $ pip install django-localized-fields

2. Add ``localized_fields`` and ``django.contrib.postgres`` to your ``INSTALLED_APPS``:

     .. code-block:: bash

        INSTALLED_APPS = [
            ....

            'django.contrib.postgres',
            'localized_fields'
        ]

3. Set the database engine to ``localized_fields.db_backend``:

    .. code-block:: python

        DATABASES = {
            'default': {
                ...
                'ENGINE': 'localized_fields.db_backend'
            }
        }

3. Set ``LANGUAGES` and `LANGUAGE_CODE`` in your settings:

     .. code-block:: python

         LANGUAGE_CODE = 'en' # default language
         LANGUAGES = (
             ('en', 'English'),
             ('nl', 'Dutch'),
             ('ro', 'Romanian')
         )

Usage
-----

Preparation
^^^^^^^^^^^
Inherit your model from ``LocalizedModel`` and declare fields on your model as ``LocalizedField``:

.. code-block:: python

     from localized_fields.models import LocalizedModel
     from localized_fields.fields import LocalizedField


     class MyModel(LocalizedModel):
         title = LocalizedField()

``django-localized-fields`` integrates with Django's i18n system, in order for certain languages to be available you have to correctly configure the ``LANGUAGES`` and ``LANGUAGE_CODE`` settings:

.. code-block:: python

     LANGUAGE_CODE = 'en' # default language
     LANGUAGES = (
          ('en', 'English'),
          ('nl', 'Dutch'),
          ('ro', 'Romanian')
     )

All the ``LocalizedField`` you define now will be available in the configured languages.

Basic usage
^^^^^^^^^^^
.. code-block:: python

     new = MyModel()
     new.title.en = 'english title'
     new.title.nl = 'dutch title'
     new.title.ro = 'romanian title'
     new.save()

By changing the active language you can control which language is presented:

.. code-block:: python

     from django.utils import translation

     translation.activate('nl')
     print(new.title) # prints 'dutch title'

     translation.activate('en')
     print(new.title) # prints 'english title'

Or get it in a specific language:

.. code-block:: python

     print(new.title.get('en')) # prints 'english title'
     print(new.title.get('ro')) # prints 'romanian title'
     print(new.title.get()) # whatever language is the primary one

You can also explicitly set a value in a certain language:

.. code-block:: python

     new.title.set('en', 'other english title')
     new.title.set('nl', 'other dutch title')

     new.title.ro = 'other romanian title'

Constraints
^^^^^^^^^^^

**Required/Optional**

At the moment, it is not possible to select two languages to be marked as required. The constraint is **not** enforced on a database level.

* Make the primary language **required** and the others optional (this is the **default**):

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(required=True)

* Make all languages optional:

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(null=True)

**Uniqueness**

By default the values stored in a ``LocalizedField`` are *not unique*. You can enforce uniqueness for certain languages. This uniqueness constraint is enforced on a database level using a ``UNIQUE INDEX``.

* Enforce uniqueness for one or more languages:

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(uniqueness=['en', 'ro'])

* Enforce uniqueness for **all** languages:

    .. code-block:: python

        from localized_fields import get_language_codes

        class MyModel(models.Model):
            title = LocalizedField(uniqueness=get_language_codes())

* Enforce uniqueness for one ore more languages **together** (similar to Django's ``unique_together``):

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(uniqueness=[('en', 'ro')])

* Enforce uniqueness for **all** languages **together**:

    .. code-block:: python

        from localized_fields import get_language_codes

        class MyModel(models.Model):
            title = LocalizedField(uniqueness=[(*get_language_codes())])


Other fields
^^^^^^^^^^^^
Besides ``LocalizedField``, there's also:

* ``LocalizedMagicSlugField``
    Successor of ``LocalizedAutoSlugField`` that fixes concurrency issues and enforces
    uniqueness of slugs on a database level. Usage is the exact same:

          .. code-block:: python

              from localized_fields.models import LocalizedModel
              from localized_fields.fields import (LocalizedField,
                                                   LocalizedMagicSlugField)

              class MyModel(LocalizedModel):
                   title = LocalizedField()
                   slug = LocalizedMagicSlugField(populate_from='title')

* ``LocalizedAutoSlugField``
     Automatically creates a slug for every language from the specified field.

     Currently only supports ``populate_from``. Example usage:

          .. code-block:: python

              from localized_fields.models import LocalizedModel
              from localized_fields.fields import (LocalizedField,
                                                   LocalizedAutoSlugField)

              class MyModel(LocalizedModel):
                   title = LocalizedField()
                   slug = LocalizedAutoSlugField(populate_from='title')

     This implementation is **NOT** concurrency safe, prefer ``LocalizedMagicSlugField``.

* ``LocalizedBleachField``
     Automatically bleaches the content of the field.
          * django-bleach

     Example usage:

           .. code-block:: python

              from localized_fields.models import LocalizedModel
              from localized_fields.fields import (LocalizedField,
                                                   LocalizedBleachField)

              class MyModel(LocalizedModel):
                   title = LocalizedField()
                   description = LocalizedBleachField()

Frequently asked questions (FAQ)
--------------------------------

1. Why do I need to change the database back-end/engine?

    We utilize PostgreSQL's `hstore` data type, which allows you to store key-value pairs in a column.  In order to create `UNIQUE` constraints on specific key, we need to create a special type of index. We could do this without a custom database back-end, but it would require everyone to manually write their migrations. By using a custom database back-end, we added support for this. When changing the `uniqueness` constraint on a `LocalizedField`, our custom database back-end takes care of creating, updating and deleting these constraints/indexes in the database.

2. I am already using a custom database back-end, can I still use yours?

    Yes. You can set the ``LOCALIZED_FIELDS_DB_BACKEND_BASE`` setting to your current back-end. This will instruct our custom database back-end to inherit from the database back-end you specified. **Warning**: this will only work if the base you specified indirectly inherits from the standard PostgreSQL database back-end.

3. Does this package work with Python 2?

    No. Only Python 3.5 or newer is supported. We're using type hints. These do not work well under older versions of Python.

4. Does this package work with Django 1.X?

    No. Only Django 1.10 or newer is supported. This is because we rely on Django's ``HStoreField``.

5. Does this package come with support for Django Admin?

    Yes. Our custom fields come with a special form that will automatically be used in Django Admin if the field is of ``LocalizedField``.

7. Why should I pick this over any of the other translation packages out there?

    You should pick whatever you feel comfortable with. This package stores translations in your database without having to have translation tables. It however only works on PostgreSQL.

8. I am using PostgreSQL <8.4, can I use this?

    No. The ``hstore`` data type was introduced in PostgreSQL 8.4.

9. I am using this package. Can I give you some beer?

    Yes! If you're ever in the area of Cluj-Napoca, Romania, swing by :)
