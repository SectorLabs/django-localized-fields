from django.conf import settings


def get_init_values() -> dict:
    """Gets a test dictionary containing a key for every language."""

    keys = {}

    for lang_code, lang_name in settings.LANGUAGES:
        keys[lang_code] = "value in %s" % lang_name

    return keys
