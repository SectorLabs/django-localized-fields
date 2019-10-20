Saving localized content
========================

.. note::

    All examples below assume a model declared like this:

    .. code-block:: python

        from localized_fields.models import LocalizedModel
        from localized_fields.fields import LocalizedField


        class MyModel(LocalizedModel):
            title = LocalizedField()


Individual assignment
*********************

.. code-block:: python

    obj = MyModel()
    obj.title.en = 'Hello'
    obj.title.nl = 'Hallo'
    obj.save()


Individual dynamic assignment
*****************************

.. code-block:: python

    obj = MyModel()
    obj.title.set('en', 'Hello')
    obj.title.set('nl', 'Hallo')
    obj.save()


Multiple assignment
*******************

.. code-block:: python

    obj = MyModel()
    obj.title = dict(en='Hello', nl='Hallo')
    obj.save()

    obj = MyModel(title=dict(en='Hello', nl='Hallo'))
    obj.save()

    obj = MyModel.objects.create(title=dict(en='Hello', nl='Hallo'))


Default language assignment
***************************

.. code-block:: python

    obj = MyModel()
    obj.title = 'Hello' # assumes value is in default language
    obj.save()

    obj = MyModel(title='Hello') # assumes value is in default language
    obj.save()

    obj = MyModel.objects.create(title='title') # assumes value is in default language


Array assignment
****************

.. code-block:: python

    obj = MyModel()
    obj.title = ['Hello', 'Hallo'] # order according to LANGUAGES
    obj.save()

    obj = MyModel(title=['Hello', 'Hallo']) # order according to LANGUAGES
    obj.save()

    obj = MyModel.objects.create(title=['Hello', 'Hallo']) # order according to LANGUAGES
