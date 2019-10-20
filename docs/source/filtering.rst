Filtering localized content
===========================

.. note::

    All examples below assume a model declared like this:

    .. code-block:: python

        from localized_fields.models import LocalizedModel
        from localized_fields.fields import LocalizedField


        class MyModel(LocalizedModel):
            title = LocalizedField()


Active language
----------------

.. code-block:: python

    from django.utils import translation

    # filter in english
    translation.activate("en")
    MyModel.objects.filter(title="test")

    # filter in dutch
    translation.activate("nl")
    MyModel.objects.filter(title="test")


Specific language
-----------------

.. code-block:: python

    MyModel.objects.filter(title__en="test")
    MyModel.objects.filter(title__nl="test")

    # do it dynamically, where the language code is a var
    lang_code = "nl"
    MyModel.objects.filter(**{"title_%s" % lang_code: "test"})
