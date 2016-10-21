django-localized-fields
=======================

`django-localized-fields` is an implementation of a field class for Django models that allows the field's value to be set in multiple languages. It does this by utilizing the `hstore` type (PostgreSQL specific), which is available as `models.HStoreField` in Django 1.10.

How does it work?
-----------------
By declaring fields on your model as `LocalizedField`:

.. code-block:: python

     from django.db import models
     from localized_fields.fields import LocalizedField


     class MyModel(models.Model):
         title = LocalizedField()


During migration, the field type will be changed to `hstore`. From now on you can store multi-language content in this field:

.. code-block:: python

     new = MyModel()
     new.title.en = 'english title'
     new.title.nl = 'dutch title'
     new.title.ro = 'romanian title'
     new.save()

`django-localized-fields` integrates with Django's i18n system, in order for certain languages to be available you have to correctly configure the `LANGUAGES` and `LANGUAGE_CODE` settings:

.. code-block:: python

     LANGUAGE_CODE = 'en' # default language
     LANGUAGEs = (
          ('en', 'English'),
          ('nl', 'Dutch'),
          ('ro', 'Romanian')
     )

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
     print(new.title.get()) # whatever language is the currently active one

You can also explicitly set a value in a certain language:

.. code-block:: python

     new.title.set('en', 'other english title')
     new.title.set('nl', 'other dutch title')

     new.title.ro = 'other romanian title'


Installation
------------
1. Install the package from PyPi:

    .. code-block:: bash

        $ pip install django-localized-fields

2. Add `localized_fields` to your `INSTALLED_APPS`:

     .. code-block:: bash

        INSTALLED_APPS = [
            ....

            'localized_fields'
        ]

You're good to go! Happy hacking!
