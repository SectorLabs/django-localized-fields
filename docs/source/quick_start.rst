.. _django.utils.translation.override: https://docs.djangoproject.com/en/2.2/ref/utils/#django.utils.translation.override
.. _django.db.models.TextField: https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.TextField
.. _LANGUAGES: https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-LANGUAGE_CODE
.. _LANGUAGE_CODE: https://docs.djangoproject.com/en/2.2/ref/settings/#languages

Quick start
===========

.. warning::

    This assumes you have followed the :ref:`Installation guide <installation>`.

``django-localized-fields`` provides various model field types to store content in multiple languages. The most basic of them all is ``LocalizedField`` which stores text of arbitrary length (like `django.db.models.TextField`_).

Declaring a model
-----------------

.. code-block:: python

    from localized_fields.models import LocalizedModel
    from localized_fields.fields import LocalizedField


    class MyModel(LocalizedModel):
        title = LocalizedField()


This creates a model with one localized field. Inside the ``LocalizedField``, strings can be stored in multiple languages. There are more fields like this for different data types (integers, images etc). ``LocalizedField`` is the most basic of them all.

Saving localized content
------------------------

You can now save text in ``MyModel.title`` in all languages you defined in the `LANGUAGES`_ setting. A short example:

.. code-block:: python

    newobj = MyModel()
    newobj.title.en = "Hello"
    newobj.title.ar = "مرحبا"
    newobj.title.nl = "Hallo"
    newobj.save()

There are various other ways of saving localized content. For example, all fields can be set at once by assigning a ``dict``:

.. code-block:: python

    newobj = MyModel()
    newobj.title = dict(en="Hello", ar="مرحبا", nl="Hallo")
    newobj.save()

This also works when using the ``create`` function:

.. code-block:: python

    newobj = MyModel.objects.create(title=dict(en="Hello", ar="مرحبا", nl="Hallo"))

Need to set the content dynamically? Use the ``set`` function:

.. code-block:: python

    newobj = MyModel()
    newobj.title.set("en", "Hello")

.. note::

    Localized field values (``localized_fields.value.LocalizedValue``) act like dictionaries. In fact, ``LocalizedValue`` extends ``dict``. Anything that works on a ``dict`` works on ``LocalizedValue``.

Retrieving localized content
----------------------------

When querying, the currently active language is taken into account. If there is no active language set, the default language is returned (set by the `LANGUAGE_CODE`_ setting).

.. code-block:: python

    from django.utils import translation

    obj = MyModel.objects.first()

    print(obj.title) # prints "Hello"

    translation.activate("ar")
    print(obj.title) # prints "مرحبا"
    str(obj.title) # same as printing, forces translation to active language

    translation.activate("nl")
    print(obj.title) # prints "Hallo"


.. note::

    Use `django.utils.translation.override`_ to change the language for just a block of code rather than setting the language globally:

    .. code-block:: python

        from django.utils import translation

        with translation.override("nl"):
            print(obj.title) # prints "Hallo"


Fallback
********

If there is no content for the currently active language, a fallback kicks in where the content will be returned in the next language. The fallback order is controlled by the order set in the `LANGUAGES`_ setting.

.. code-block:: python

    obj = MyModel.objects.create(dict(en="Hallo", ar="مرحبا"))

    translation.activate("nl")
    print(obj.title) # prints "مرحبا" because there"s no content in NL

.. seealso::

    Use the :ref:`LOCALIZED_FIELDS_FALLBACKS <LOCALIZED_FIELDS_FALLBACKS>` setting to control the fallback behaviour.


Cast to str
***********

Want to get the value in the currently active language without casting to ``str``? (For null-able fields for example). Use the ``.translate()`` function:

.. code-block:: python

    obj = MyModel.objects.create(dict(en="Hallo", ar="مرحبا"))

    str(obj.title) == obj.title.translate() # True

.. note::

    ``str(..)`` is guarenteed to return a string. If the value is ``None``, ``str(..)`` returns an empty string. ``translate()`` would return ``None``. This is because Python forces the ``__str__`` function to return a string.

    .. code-block:: python

        obj = MyModel.objects.create(dict(en="Hallo"))

        translation.activate('nl')

        str(obj.title) # ""
        obj.title.translate() # None
