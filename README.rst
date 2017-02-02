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
