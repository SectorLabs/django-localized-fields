|  |  |  |
|--------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| :white_check_mark: | **Tests** | [![CircleCI](https://circleci.com/gh/SectorLabs/django-localized-fields/tree/master.svg?style=svg)](https://circleci.com/gh/SectorLabs/django-localized-fields/tree/master) |
| :memo: | **License** | [![License](https://img.shields.io/:license-mit-blue.svg)](http://doge.mit-license.org) |
| :package: | **PyPi** | [![PyPi](https://badge.fury.io/py/django-localized-fields.svg)](https://pypi.python.org/pypi/django-localized-fields) |
| <img src="https://icon-library.net/images/django-icon/django-icon-0.jpg" width="22px" height="22px" align="center" /> | **Django Versions** | 2.0, 2.1, 2.2, 3.0, 3.1 |
| <img src="http://www.iconarchive.com/download/i73027/cornmanthe3rd/plex/Other-python.ico" width="22px" height="22px" align="center" /> | **Python Versions** | 3.6, 3.7, 3.8, 3.9 |
| :book: | **Documentation** | [Read The Docs](https://django-localized-fields.readthedocs.io) |
| :warning: | **Upgrade** | [Upgrade fom v5.x](https://django-localized-fields.readthedocs.io/en/latest/releases.html#v6-0)
| :checkered_flag: | **Installation** | [Installation Guide](https://django-localized-fields.readthedocs.io/en/latest/installation.html) |

`django-localized-fields` is an implementation of a field class for Django models that allows the field's value to be set in multiple languages. It does this by utilizing the ``hstore`` type (PostgreSQL specific), which is available as `models.HStoreField` since Django 1.10.

---

:warning: **This README is for v6. See the `v5.x` branch for v5.x.**

---

## Working with the code
### Prerequisites

* PostgreSQL 10 or newer.
* Django 2.0 or newer.
* Python 3.6 or newer.

### Getting started

1. Clone the repository:

       λ git clone https://github.com/SectorLabs/django-localized-fields.git

2. Create a virtual environment:

       λ cd django-localized-fields
       λ virtualenv env
       λ source env/bin/activate

3. Create a postgres user for use in tests (skip if your default user is a postgres superuser):

       λ createuser --superuser psqlextra --pwprompt
       λ export DATABASE_URL=postgres://localized_fields:<password>@localhost/localized_fields

   Hint: if you're using virtualenvwrapper, you might find it beneficial to put
   the ``export`` line in ``$VIRTUAL_ENV/bin/postactivate`` so that it's always
   available when using this virtualenv.

4. Install the development/test dependencies:

       λ pip install ".[test]" ".[analysis]"

5. Run the tests:

       λ tox

7. Auto-format code, sort imports and auto-fix linting errors:

       λ python setup.py fix
