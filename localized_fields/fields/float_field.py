from typing import Optional, Union, Dict

from django.conf import settings
from django.db.utils import IntegrityError

from .field import LocalizedField
from ..value import LocalizedValue, LocalizedFloatValue
from ..forms import LocalizedIntegerFieldForm


class LocalizedFloatField(LocalizedField):
    """Stores float as a localized value."""

    attr_class = LocalizedFloatValue

    @classmethod
    def from_db_value(cls, value, *_) -> Optional[LocalizedFloatValue]:
        db_value = super().from_db_value(value)
        if db_value is None:
            return db_value

        # if we were used in an expression somehow then it might be
        # that we're returning an individual value or an array, so
        # we should not convert that into an :see:LocalizedFloatValue
        if not isinstance(db_value, LocalizedValue):
            return db_value

        return cls._convert_localized_value(db_value)

    def to_python(self, value: Union[Dict[str, int], int, None]) -> LocalizedFloatValue:
        """Converts the value from a database value into a Python value."""

        db_value = super().to_python(value)
        return self._convert_localized_value(db_value)

    def get_prep_value(self, value: LocalizedFloatValue) -> dict:
        """Gets the value in a format to store into the database."""

        # apply default values
        default_values = LocalizedFloatValue(self.default)
        if isinstance(value, LocalizedFloatValue):
            for lang_code, _ in settings.LANGUAGES:
                local_value = value.get(lang_code)
                if local_value is None:
                    value.set(lang_code, default_values.get(lang_code, None))

        prepped_value = super().get_prep_value(value)
        if prepped_value is None:
            return None

        # make sure all values are proper floats
        for lang_code, _ in settings.LANGUAGES:
            local_value = prepped_value[lang_code]
            try:
                if local_value is not None:
                    float(local_value)
            except (TypeError, ValueError):
                raise IntegrityError('non-float value in column "%s.%s" violates '
                                     'float constraint' % (self.name, lang_code))

            # convert to a string before saving because the underlying
            # type is hstore, which only accept strings
            prepped_value[lang_code] = str(local_value) if local_value is not None else None

        return prepped_value

    def formfield(self, **kwargs):
        """Gets the form field associated with this field."""
        defaults = {
            'form_class': LocalizedIntegerFieldForm
        }

        defaults.update(kwargs)
        return super().formfield(**defaults)

    @staticmethod
    def _convert_localized_value(value: LocalizedValue) -> LocalizedFloatValue:
        """Converts from :see:LocalizedValue to :see:LocalizedFloatValue."""

        float_values = {}
        for lang_code, _ in settings.LANGUAGES:
            local_value = value.get(lang_code, None)
            if local_value is None or local_value.strip() == '':
                local_value = None

            try:
                float_values[lang_code] = float(local_value)
            except (ValueError, TypeError):
                float_values[lang_code] = None

        return LocalizedFloatValue(float_values)
