from django.conf import settings

from .field import LocalizedField

class LocalizedIntegerField(LocalizedField):

    @classmethod
    def from_db_value(cls, value, *_):

        if isinstance(value, dict):
            values = LocalizedField.from_db_value(value, *_)
            converted_values = {}

            for lang_code, _ in settings.LANGUAGES:
                value = values.get(lang_code)
                converted_values[lang_code] = int(value) if value is not None else None
            
            return cls.attr_class(converted_values)

        if not isinstance(value, dict):
            return int(value)
