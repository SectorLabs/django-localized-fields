Querying localized content
==========================

.. note::

    All examples below assume a model declared like this:

    .. code-block:: python

        from localized_fields.models import LocalizedModel
        from localized_fields.fields import LocalizedField


        class MyModel(LocalizedModel):
            title = LocalizedField()


Active language
---------------

Only need a value in a specific language? Use the ``LocalizedRef`` expression to query a value in the currently active language:

.. code-block:: python

    from localized_fields.expressions import LocalizedRef

    MyModel.objects.create(title=dict(en="Hello", nl="Hallo"))

    translation.activate("nl")
    english_title = (
        MyModel
        .objects
        .annotate(title=LocalizedRef("title"))
        .values_list("title", flat=True)
        .first()
    )

    print(english_title) # prints "Hallo"


Specific language
-----------------

.. code-block:: python

    from localized_fields.expressions import LocalizedRef

    result = (
        MyModel
        .objects
        .values(
            'title__en',
            'title__nl',
        )
        .first()
    )

    print(result['title__en'])
    print(result['title__nl'])
