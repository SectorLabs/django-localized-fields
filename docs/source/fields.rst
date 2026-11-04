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


LocalizedBleachField
--------------------

Localized field that sanitizes the value in every language with `bleach`_ before saving it. Requires `django-bleach`_, and uses the bleach options from its ``BLEACH_*`` settings.

.. code-block:: python

    from localized_fields.fields import LocalizedBleachField

    class MyModel(models.Model):
         description = LocalizedBleachField(escape=False, max_clean_passes=5)

``escape`` (default ``True``)
    When ``True``, the value is stored as bleach returns it. Allowed tags stay markup, and any other ``<``, ``>`` and ``&`` are escaped, for example ``&lt;`` instead of ``<``.
    When ``False``, the value is unescaped before cleaning and the cleaned value is unescaped again before it is stored, so those characters are stored unescaped.

``max_clean_passes`` (default ``None``)
    When ``None``, the value is cleaned once.

    When set to a number, the value is unescaped and cleaned repeatedly until it stops changing, at most that many times. Use this when values can contain markup that was escaped more than once, which a single pass only partially decodes and can leave as markup after a later unescape. If the value still changes after the last pass, the field stores an empty string for that language.

    This decodes escaped input with either ``escape`` value. ``escape`` then only decides how the cleaned result is stored. For example, with ``escape=True`` and ``b`` as an allowed tag, the input ``&lt;b&gt;bold&lt;/b&gt; & more`` is stored as ``&lt;b&gt;bold&lt;/b&gt; &amp; more`` without ``max_clean_passes``, but as ``<b>bold</b> &amp; more`` with it.

    Each pass removes up to two levels of escaping, so with ``5``, text escaped up to 10 times is still decoded. Ordinary text needs at most one pass that changes it.

    Repeated cleaning only removes markup when ``BLEACH_STRIP_TAGS = True``. With the default ``False``, bleach escapes disallowed tags instead of removing them, and with ``escape=False`` they are unescaped back into markup before the value is stored.

.. _bleach: https://bleach.readthedocs.io/
.. _django-bleach: https://django-bleach.readthedocs.io/


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
