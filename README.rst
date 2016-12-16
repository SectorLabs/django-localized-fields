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
* Make it unnecesarry to modify your migrations manually to enable the PostgreSQL HStore extension.

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


Create your migrations using ``python manage.py makemigrations``. Open the generated migration in your favorite editor and setup the HStore extension before the first ``CreateModel`` or ``AddField`` operation by adding a migration with the `HStoreExtension` operation. For example:

.. code-block:: python

    from django.contrib.postgres.operations import HStoreExtension

    class Migration(migrations.Migration):
        ...

        operations = [
            HStoreExtension(),
            ...
        ]

Then apply the migration using ``python manage.py migrate``.

``django-localized-fields`` integrates with Django's i18n system, in order for certain languages to be available you have to correctly configure the ``LANGUAGES`` and ``LANGUAGE_CODE`` settings:

.. code-block:: python

     LANGUAGE_CODE = 'en' # default language
     LANGUAGES = (
          ('en', 'English'),
          ('nl', 'Dutch'),
          ('ro', 'Romanian')
     )

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
By default, the following constraints apply to a ``LocalizedField``:

* Only the default language is ``required``. The other languages are optional and can be ``NULL``.
* If ``null=True`` is specified on the ``LocalizedField``, then none of the languages are required.

At the moment it is *not* possible to specifically instruct ``LocalizedField`` to mark certain languages as required or optional.

Other fields
^^^^^^^^^^^^
Besides ``LocalizedField``, there's also:

* ``LocalizedAutoSlugField``
     Automatically creates a slug for every language from the specified field. Depends upon:
          * django-autoslug

     Currently only supports `populate_from`. Example usage:

          .. code-block:: python

              from localized_fields.models import LocalizedModel
              from localized_fields.fields import (LocalizedField,
                                                   LocalizedAutoSlugField)

              class MyModel(LocalizedModel):
                   title = LocalizedField()
                   slug = LocalizedAutoSlugField(populate_from='title')

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
