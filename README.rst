django-localized-fields
=======================

.. image:: https://circleci.com/gh/SectorLabs/django-localized-fields.svg?style=svg
    :target: https://circleci.com/gh/SectorLabs/django-localized-fields

.. image:: https://img.shields.io/github/license/SectorLabs/django-localized-fields.svg
    :target: https://github.com/SectorLabs/django-localized-fields/blob/master/LICENSE.md

.. image:: https://badge.fury.io/py/django-localized-fields.svg
    :target: https://pypi.python.org/pypi/django-localized-fields

``django-localized-fields`` is an implementation of a field class for Django models that allows the field's value to be set in multiple languages. It does this by utilizing the ``hstore`` type (PostgreSQL specific), which is available as ``models.HStoreField`` since Django 1.10.

This package requires Python 3.5 or newer, Django 1.11 or newer and PostgreSQL 9.6 or newer.

Contributors
------------

* `seroy <https://github.com/seroy/>`_
* `unaizalakain <https://github.com/unaizalakain/>`_

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
            'localized_fields.apps.LocalizedFieldsConfig'
        ]

3. Set the database engine to ``psqlextra.backend``:

    .. code-block:: python

        DATABASES = {
            'default': {
                ...
                'ENGINE': 'psqlextra.backend'
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
Declare fields on your model as ``LocalizedField``:

.. code-block:: python

     from localized_fields.fields import LocalizedField


     class MyModel(models.Model):
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
     print(new.title.get('ar', 'haha')) # prints 'haha' if there is no value in arabic

You can also explicitly set a value in a certain language:

.. code-block:: python

     new.title.set('en', 'other english title')
     new.title.set('nl', 'other dutch title')

     new.title.ro = 'other romanian title'

Constraints
^^^^^^^^^^^

**Required/Optional**

Constraints are enforced on a database level.

* Optional filling

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(blank=True, null=True, required=False)

* Make translation required for any language

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(blank=False, null=False, required=False)

* Make translation required for specific languages

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(blank=False, null=False, required=['en', 'ro'])

* Make translation required for all languages

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(blank=False, null=False, required=True)

* By default the primary language **required** and the others optional:

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField()

**Uniqueness**

By default the values stored in a ``LocalizedField`` are *not unique*. You can enforce uniqueness for certain languages. This uniqueness constraint is enforced on a database level using a ``UNIQUE INDEX``.

* Enforce uniqueness for one or more languages:

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(uniqueness=['en', 'ro'])

* Enforce uniqueness for **all** languages:

    .. code-block:: python

        from localized_fields.util import get_language_codes

        class MyModel(models.Model):
            title = LocalizedField(uniqueness=get_language_codes())

* Enforce uniqueness for one ore more languages **together** (similar to Django's ``unique_together``):

    .. code-block:: python

        class MyModel(models.Model):
            title = LocalizedField(uniqueness=[('en', 'ro')])

* Enforce uniqueness for **all** languages **together**:

    .. code-block:: python

        from localized_fields.util import get_language_codes

        class MyModel(models.Model):
            title = LocalizedField(uniqueness=[(*get_language_codes())])


Other fields
^^^^^^^^^^^^
Besides ``LocalizedField``, there's also:

* ``LocalizedUniqueSlugField``
    Successor of ``LocalizedAutoSlugField`` that fixes concurrency issues and enforces
    uniqueness of slugs on a database level. Usage is the exact same:

          .. code-block:: python

              from localized_fields.models import LocalizedModel
              from localized_fields.fields import LocalizedField, LocalizedUniqueSlugField

              class MyModel(LocalizedModel):
                   title = LocalizedField()
                   slug = LocalizedUniqueSlugField(populate_from='title')

    ``populate_from`` can be:

        - The name of a field.

           .. code-block:: python

               slug = LocalizedUniqueSlugField(populate_from='name', include_time=True)

        - A callable.

           .. code-block:: python

               def generate_slug(instance):
                   return instance.title

               slug = LocalizedUniqueSlugField(populate_from=generate_slug, include_time=True)

        - A tuple of names of fields.

           .. code-block:: python

               slug = LocalizedUniqueSlugField(populate_from=('name', 'beer') include_time=True)

    By setting the option ``include_time=True``

          .. code-block:: python

               slug = LocalizedUniqueSlugField(populate_from='title', include_time=True)

    You can instruct the field to include a part of the current time into
    the resulting slug. This is useful if you're running into a lot of collisions.

* ``LocalizedBleachField``
     Automatically bleaches the content of the field.

          * django-bleach

     Example usage:

           .. code-block:: python

              from localized_fields.fields import LocalizedField, LocalizedBleachField

              class MyModel(models.Model):
                   title = LocalizedField()
                   description = LocalizedBleachField()

* ``LocalizedIntegerField``
    This is an experimental field type introduced in version 5.0 and is subject to change. It also has
    some pretty major downsides due to the fact that values are stored as strings and are converted
    back and forth.

    Allows storing integers in multiple languages. This works exactly like ``LocalizedField`` except that
    all values must be integers. Do note that values are stored as strings in your database because
    the backing field type is ``hstore``, which only allows storing integers. The ``LocalizedIntegerField``
    takes care of ensuring that all values are integers and converts the stored strings back to integers
    when retrieving them from the database. Do not expect to be able to do queries such as:

        .. code-block:: python

            MyModel.objects.filter(score__en__gt=1)


* ``LocalizedCharField`` and ``LocalizedTextField``
    These fields following the Django convention for string-based fields use the empty string as value for “no data”, not NULL.
    ``LocalizedCharField`` uses ``TextInput`` (``<input type="text">``) widget for render.

    Example usage:

           .. code-block:: python

              from localized_fields.fields import LocalizedCharField, LocalizedTextField

              class MyModel(models.Model):
                   title = LocalizedCharField()
                   description = LocalizedTextField()

* ``LocalizedFileField``
    A file-upload field

    Parameter ``upload_to`` supports ``lang`` parameter for string formatting or as function argument (in case if ``upload_to`` is callable).

    Example usage:

           .. code-block:: python

              from localized_fields.fields import LocalizedFileField

              def my_directory_path(instance, filename, lang):
                # file will be uploaded to MEDIA_ROOT/<lang>/<id>_<filename>
                return '{0}/{0}_{1}'.format(lang, instance.id, filename)

              class MyModel(models.Model):
                   file1 = LocalizedFileField(upload_to='uploads/{lang}/')
                   file2 = LocalizedFileField(upload_to=my_directory_path)

    In template you can access to file attributes:

            .. code-block:: django

              {# For current active language: #}

              {{ model.file.url }}  {# output file url #}
              {{ model.file.name }} {# output file name #}

              {# Or get it in a specific language: #}

              {{ model.file.ro.url }}  {# output file url for romanian language #}
              {{ model.file.ro.name }} {# output file name for romanian language #}

    To get access to file instance for current active language use ``localized`` method:

            .. code-block:: python

              model.file.localized()

Experimental feature
^^^^^^^^^^^^^^^^^^^^
Enables the following experimental features:
    * ``LocalizedField`` will return ``None`` instead of an empty ``LocalizedValue`` if there is no database value.

.. code-block:: python

     LOCALIZED_FIELDS_EXPERIMENTAL = True


Django Admin Integration
^^^^^^^^^^^^^^^^^^^^^^^^
To enable widgets in the admin, you need to inherit from ``LocalizedFieldsAdminMixin``:

.. code-block:: python

    from django.contrib import admin
    from myapp.models import MyLocalizedModel

    from localized_fields.admin import LocalizedFieldsAdminMixin

    class MyLocalizedModelAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        """Any admin options you need go here"""

    admin.site.register(MyLocalizedModel, MyLocalizedModelAdmin)


Frequently asked questions (FAQ)
--------------------------------

1. Does this package work with Python 2?

    No. Only Python 3.5 or newer is supported. We're using type hints. These do not work well under older versions of Python.

2. With what Django versions does this package work?

    Only Django 1.11 or newer is supported, this includes Django 2.X. This is because we rely on Django's ``HStoreField`` and template-based widget rendering.

3. Does this package come with support for Django Admin?

    Yes. Our custom fields come with a special form that will automatically be used in Django Admin if the field is of ``LocalizedField``.

4. Why should I pick this over any of the other translation packages out there?

    You should pick whatever you feel comfortable with. This package stores translations in your database without having to have translation tables. It however only works on PostgreSQL.

5. I am using PostgreSQL <9.6, can I use this?

    No. The ``hstore`` data type was introduced in PostgreSQL 9.6.

6. I am using this package. Can I give you some beer?

    Yes! If you're ever in the area of Cluj-Napoca, Romania, swing by :)
