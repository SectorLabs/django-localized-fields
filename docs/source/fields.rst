.. _django.db.models.CharField: https://docs.djangoproject.com/en/2.2/ref/models/fields/#charfield
.. _django.db.models.TextField: https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.TextField
.. _django.db.models.IntegerField: https://docs.djangoproject.com/en/2.2/ref/models/fields/#integerfield
.. _django.db.models.FileField: https://docs.djangoproject.com/en/2.2/ref/models/fields/#filefield

.. _fields:

Localized fields
================

LocalizedField
--------------

Base localized fields. Stores content as strings of arbitrary lengths.

.. code-block:: python

    from localized_fields.fields import LocalizedField


LocalizedCharField
------------------

Localized version of `django.db.models.CharField`_.

Use this for single-line text content. Uses ``<input type="text" />`` when rendered as a widget.

.. code-block:: python

    from localized_fields.fields import LocalizedCharField

Follows the same convention as `django.db.models.CharField`_ to store empty strings for "no data" and not NULL.


LocalizedTextField
------------------

Localized version of `django.db.models.TextField`_.

Use this for multi-line text content.

.. code-block:: python

    from localized_fields.fields import LocalizedTextField

Follows the same convention as `django.db.models.TextField`_ to store empty strings for "no data" and not NULL.


LocalizedFileField
------------------

Localized version of `django.db.models.FileField`_.

.. code-block:: python

    from localized_fields.fields import LocalizedFileField

    def my_directory_path(instance, filename, lang):
      # file will be uploaded to MEDIA_ROOT/<lang>/<id>_<filename>
      return '{0}/{0}_{1}'.format(lang, instance.id, filename)

    class MyModel(models.Model):
         file1 = LocalizedFileField(upload_to='uploads/{lang}/')
         file2 = LocalizedFileField(upload_to=my_directory_path)


The ``upload_to`` supports the ``{lang}}`` placeholder for string formatting or as function argument (in case if upload_to is a callable).

In a template, you can access the files for different languages:

.. code-block:: html

    {# For current active language: #}

    {{ model.file.url }}  {# output file url #}
    {{ model.file.name }} {# output file name #}

    {# Or get it in a specific language: #}

    {{ model.file.ro.url }}  {# output file url for romanian language #}
    {{ model.file.ro.name }} {# output file name for romanian language #}

To get the file instance for the current language:

.. code-block:: python

    model.file.localized()


LocalizedIntegerField
---------------------

Localized version of `django.db.models.IntegerField`_.

.. code-block:: python

    from localized_fields.fields import LocalizedIntegerField

Although the underlying PostgreSQL data type for ``LocalizedField`` is hstore (which only stores strings). ``LocalizedIntegerField`` takes care of making sure that input values are integers and casts the values back to integers when querying them.
