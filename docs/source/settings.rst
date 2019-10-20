.. _LANGUAGES: https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-LANGUAGE_CODE
.. _LANGUAGE_CODE: https://docs.djangoproject.com/en/2.2/ref/settings/#languages

Settings
========

.. LOCALIZED_FIELDS_EXPERIMENTAL:

* ``LOCALIZED_FIELDS_EXPERIMENTAL``

    .. note::

        Disabled in v5.x and earlier. Enabled by default since v6.0.

    When enabled:

    * ``LocalizedField`` will return ``None`` instead of an empty ``LocalizedValue`` if there is no database value.
    * ``LocalizedField`` lookups will by the currently active language instead of an exact match by dict.


.. _LOCALIZED_FIELDS_FALLBACKS:

* ``LOCALIZED_FIELDS_FALLBACKS``

    List of language codes which define the order in which fallbacks should happen. If a value is not available in a specific language, we'll try to pick the value in the next language in the list.

    .. warning::

        If this setting is not configured, the default behaviour is to fall back to the value in the **default language**. It is recommended to configure this setting to get predictible fallback behaviour that suits your use case.

        Use the same language codes as you used for configuring the `LANGUAGES`_ and `LANGUAGE_CODE`_ setting.

    .. code-block:: python

        LOCALIZED_FIELDS_FALLBACKS = {
            "en": ["nl", "ar"], # if trying to get EN, but not available, try NL and then AR
            "nl": ["en", "ar"], # if trying to get NL, but not available, try EN and then AR
            "ar": ["en", "nl"], # if trying to get AR, but not available, try EN and then NL
        }
