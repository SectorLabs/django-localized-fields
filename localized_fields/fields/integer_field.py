from typing import Dict, Optional, Union

from django.conf import settings
from django.contrib.postgres.fields.hstore import KeyTransform
from django.db.utils import IntegrityError

from ..forms import LocalizedIntegerFieldForm
from ..value import LocalizedIntegerValue, LocalizedValue
from .field import LocalizedField


class LocalizedIntegerFieldKeyTransform(KeyTransform):
    """Transform that selects a single key from a hstore value and casts it to
    an integer."""

    def as_sql(self, compiler, connection):
        sql, params = super().as_sql(compiler, connection)
        return f"{sql}::integer", params


class LocalizedIntegerField(LocalizedField):
    """Stores integers as a localized value."""

    attr_class = LocalizedIntegerValue

    def get_transform(self, name):
        """Gets the transformation to apply when selecting this value.

        This is where the SQL expression to grab a single is added and
        the cast to integer so that sorting by a hstore value works as
        expected.
        """

        def _transform(*args, **kwargs):
            return LocalizedIntegerFieldKeyTransform(name, *args, **kwargs)

        return _transform

    @classmethod
    def from_db_value(cls, value, *_) -> Optional[LocalizedIntegerValue]:
        db_value = super().from_db_value(value)
        if db_value is None:
            return db_value

        if isinstance(db_value, str):
            return int(db_value)

        # if we were used in an expression somehow then it might be
        # that we're returning an individual value or an array, so
        # we should not convert that into an :see:LocalizedIntegerValue
        if not isinstance(db_value, LocalizedValue):
            return db_value

        return cls._convert_localized_value(db_value)

    def to_python(
        self, value: Union[Dict[str, int], int, None]
    ) -> LocalizedIntegerValue:
        """Converts the value from a database value into a Python value."""

        db_value = super().to_python(value)
        return self._convert_localized_value(db_value)

    def get_prep_value(self, value: LocalizedIntegerValue) -> dict:
        """Gets the value in a format to store into the database."""

        # apply default values
        default_values = LocalizedIntegerValue(self.default)
        if isinstance(value, LocalizedIntegerValue):
            for lang_code, _ in settings.LANGUAGES:
                local_value = value.get(lang_code)
                if local_value is None:
                    value.set(lang_code, default_values.get(lang_code, None))

        prepped_value = super().get_prep_value(value)
        if prepped_value is None:
            return None

        # make sure all values are proper integers
        for lang_code, _ in settings.LANGUAGES:
            local_value = prepped_value[lang_code]
            try:
                if local_value is not None:
                    int(local_value)
            except (TypeError, ValueError):
                raise IntegrityError(
                    'non-integer value in column "%s.%s" violates '
                    "integer constraint" % (self.name, lang_code)
                )

            # convert to a string before saving because the underlying
            # type is hstore, which only accept strings
            prepped_value[lang_code] = (
                str(local_value) if local_value is not None else None
            )

        return prepped_value

    def formfield(self, **kwargs):
        """Gets the form field associated with this field."""
        defaults = {"form_class": LocalizedIntegerFieldForm}

        defaults.update(kwargs)
        return super().formfield(**defaults)

    @staticmethod
    def _convert_localized_value(
        value: LocalizedValue
    ) -> LocalizedIntegerValue:
        """Converts from :see:LocalizedValue to :see:LocalizedIntegerValue."""

        integer_values = {}
        for lang_code, _ in settings.LANGUAGES:
            local_value = value.get(lang_code, None)
            if local_value is None or local_value.strip() == "":
                local_value = None

            try:
                integer_values[lang_code] = int(local_value)
            except (ValueError, TypeError):
                integer_values[lang_code] = None

        return LocalizedIntegerValue(integer_values)
