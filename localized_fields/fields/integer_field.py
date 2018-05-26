from .field import LocalizedField

from django.conf import settings

class LocalizedIntegerField(LocalizedField):

    @classmethod
    def from_db_value(cls, value, *_):

        values = LocalizedField.from_db_value(value, *_)
        converted_values = {}

        for lang_code, _ in settings.LANGUAGES:
            value = values.get(lang_code)
            converted_values[lang_code] = int(value) if value else None

        return cls.attr_class(converted_values)
