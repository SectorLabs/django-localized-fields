from typing import List

from django.conf import settings


def get_language_codes() -> List[str]:
    """Gets a list of all available language codes.

    This looks at your project's settings.LANGUAGES
    and returns a flat list of the configured
    language codes.

    Arguments:
        A flat list of all availble language codes
        in your project.
    """

    return [
        lang_code
        for lang_code, _ in settings.LANGUAGES
    ]


def resolve_object_property(obj, path: str):
    """Resolves the value of a property on an object.

    Is able to resolve nested properties. For example,
    a path can be specified:

        'other.beer.name'

    Raises:
        AttributeError:
            In case the property could not be resolved.

    Returns:
        The value of the specified property.
    """

    value = obj
    for path_part in path.split('.'):
        value = getattr(value, path_part)

    return value
