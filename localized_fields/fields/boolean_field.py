from typing import Dict, Optional, Union

from django.conf import settings
from django.db.utils import IntegrityError

from ..forms import LocalizedBooleanFieldForm
from ..value import LocalizedBooleanValue, LocalizedValue
from .field import LocalizedField


class LocalizedBooleanField(LocalizedField):
    """Stores booleans as a localized value."""

    attr_class = LocalizedBooleanValue

    @classmethod
    def from_db_value(cls, value, *_) -> Optional[LocalizedBooleanValue]:
        db_value = super().from_db_value(value)

        if db_value is None:
            return db_value

        if isinstance(db_value, str):
            if db_value.lower() == "true":
                return True
            return False

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
            print(type(local_value))

            if local_value is not None and local_value.lower() not in (
                "false",
                "true",
            ):
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
                if local_value.lower() == "false":
                    local_value = False
                elif local_value.lower() == "true":
                    local_value = True
                else:
                    raise ValueError(
                        f"Could not convert value {local_value} to boolean."
                    )

                integer_values[lang_code] = local_value
            elif local_value is not None:
                raise TypeError(
                    f"Expected value of type str instead of {type(local_value)}."
                )

        return LocalizedBooleanValue(integer_values)
