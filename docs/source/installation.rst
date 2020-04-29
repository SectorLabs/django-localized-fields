.. _installation:

Installation
============

1. Install the package from PyPi:

    .. code-block:: bash

        $ pip install django-localized-fields

2. Add ``django.contrib.postgres``, ``psqlextra`` and ``localized_fields`` to your ``INSTALLED_APPS``:

    .. code-block:: python

        INSTALLED_APPS = [
            ...
            "django.contrib.postgres",
            "psqlextra",
            "localized_fields",
        ]


3. Set the database engine to ``psqlextra.backend``:

    .. code-block:: python

        DATABASES = {
            "default": {
                ...
                "ENGINE": "psqlextra.backend",
            ],
        }

    .. note::

        Already using a custom back-end? Set ``POSTGRES_EXTRA_DB_BACKEND_BASE`` to your custom back-end. See django-postgres-extra's documentation for more details: `Using a custom database back-end <https://django-postgres-extra.readthedocs.io/en/latest/db-engine/#using-a-custom-database-back-end>`_.

4. Set ``LANGUAGES`` and ``LANGUAGE_CODE``:

    .. code-block:: python

        LANGUAGE_CODE = "en" # default language
        LANGUAGES = (
            ("en", "English"), # default language
            ("ar", "Arabic"),
            ("ro", "Romanian"),
        )


    .. warning::

        Make sure that the language specified in ``LANGUAGE_CODE`` is the first language in the ``LANGUAGES`` list. Django and many third party packages assume that the default language is the first one in the list.

5. Apply migrations to enable the HStore extension:

    .. code-block:: bash

        $ python manage.py migrate

    .. note::

        Migrations might fail to be applied if the PostgreSQL user applying the migration is not a super user. Enabling/creating extensions requires superuser permission. Not a superuser? Ask your database administrator to create the ``hstore`` extension on your PostgreSQL server manually using the following statement:

            .. code-block:: sql

                CREATE EXTENSION IF NOT EXISTS hstore;

        Then, fake apply the migration to tell Django that the migration was applied already:

            .. code-block:: bash

                python manage.py migrate localized_fields --fake
