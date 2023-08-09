import re

from typing import Dict, Optional, Union

from django.conf import settings
from django.db.utils import IntegrityError

from ..forms import LocalizedBooleanFieldForm
from ..value import LocalizedBooleanValue, LocalizedValue
from .field import LocalizedField


class LocalizedBooleanField(LocalizedField):
    """Stores booleans as a localized value."""

    attr_class = LocalizedBooleanValue

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def from_db_value(cls, value, *_) -> Optional[LocalizedBooleanValue]:
        db_value = super().from_db_value(value)

        if db_value is None:
            return db_value

        if isinstance(db_value, str):
            if db_value == "true":
                return True
            return False

        # if we were used in an expression somehow then it might be
        # that we're returning an individual value or an array, so
        # we should not convert that into an :see:LocalizedBooleanValue
        if not isinstance(db_value, LocalizedValue):
            return db_value

        return cls._convert_localized_value(db_value)

    def to_python(
        self, value: Union[Dict[str, str], str, None]
    ) -> LocalizedBooleanValue:
        """Converts the value from a database value into a Python value."""

        db_value = super().to_python(value)
        return self._convert_localized_value(db_value)

    def get_prep_value(self, value: LocalizedBooleanValue) -> dict:
        """Gets the value in a format to store into the database."""

        # apply default values
        default_values = LocalizedBooleanValue(self.default)
        if isinstance(value, LocalizedBooleanValue):
            for lang_code, _ in settings.LANGUAGES:
                local_value = value.get(lang_code)
                if local_value is None:
                    value.set(lang_code, default_values.get(lang_code, None))

        prepped_value = super().get_prep_value(value)
        if prepped_value is None:
            return None

        # make sure all values are proper values to be converted to bool
        for lang_code, _ in settings.LANGUAGES:
            local_value = prepped_value[lang_code]

            if local_value is not None and local_value not in ("False", "True"):
                raise IntegrityError(
                    'non-boolean value in column "%s.%s" violates '
                    "boolean constraint" % (self.name, lang_code)
                )

            # convert to a string before saving because the underlying
            # type is hstore, which only accept strings
            prepped_value[lang_code] = (
                str(local_value) if local_value is not None else None
            )

        return prepped_value

    def formfield(self, **kwargs):
        """Gets the form field associated with this field."""
        defaults = {"form_class": LocalizedBooleanFieldForm}

        defaults.update(kwargs)
        return super().formfield(**defaults)

    @staticmethod
    def _convert_localized_value(
        value: LocalizedValue,
    ) -> LocalizedBooleanValue:
        """Converts from :see:LocalizedValue to :see:LocalizedBooleanValue."""

        integer_values = {}
        for lang_code, _ in settings.LANGUAGES:
            local_value = value.get(lang_code, None)

            if isinstance(local_value, str):
                if re.match("False", local_value, re.IGNORECASE):
                    local_value = False
                elif re.match("True", local_value, re.IGNORECASE):
                    local_value = True
                else:
                    local_value = None

                integer_values[lang_code] = local_value

        return LocalizedBooleanValue(integer_values)
