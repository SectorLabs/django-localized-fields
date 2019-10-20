Working with localized values
=============================

.. note::

    All examples below assume a model declared like this:

    .. code-block:: python

        from localized_fields.models import LocalizedModel
        from localized_fields.fields import LocalizedField


        class MyModel(LocalizedModel):
            title = LocalizedField()

Localized content is represented by ``localized_fields.value.LocalizedValue``. Which is essentially a dictionary where the key is the language and the value the content in the respective language.

.. code-block:: python

    from localized_fields.value import LocalizedValue

    obj = MyModel.objects.first()
    assert isistance(obj.title, LocalizedValue) # True


With fallback
-------------

.. seealso::

    Configure :ref:`LOCALIZED_FIELDS_FALLBACKS <LOCALIZED_FIELDS_FALLBACKS>` to control the fallback behaviour.


Active language
***************

.. code-block:: python

    # gets content in Arabic, falls back to next language
    # if not availble
    translation.activate('ar')
    obj.title.translate()

    # alternative: cast to string
    title_ar = str(obj.title)


Specific language
*****************

.. code-block:: python

    # gets content in Arabic, falls back to next language
    # if not availble
    obj.title.translate('ar')


Without fallback
----------------

Specific language
*****************

.. code-block:: python

    # gets content in Dutch, None if not available
    # no fallback to secondary languages here!
    obj.title.nl


Specific language dynamically
*****************************

.. code-block:: python

    # gets content in Dutch, None if not available
    # no fallback to secondary languages here!
    obj.title.get('nl')
