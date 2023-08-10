from collections.abc import Iterable
from typing import Optional

import deprecation

from django.conf import settings
from django.utils import translation


class LocalizedValue(dict):
    """Represents the value of a :see:LocalizedField."""

    default_value = None

    def __init__(self, keys: dict = None):
        """Initializes a new instance of :see:LocalizedValue.

        Arguments:
            keys:
                The keys to initialize this value with. Every
                key contains the value of this field in a
                different language.
        """

        super().__init__({})
        self._interpret_value(keys)

    def get(self, language: str = None, default: str = None) -> str:
        """Gets the underlying value in the specified or primary language.

        Arguments:
            language:
                The language to get the value in.

        Returns:
            The value in the current language, or
            the primary language in case no language
            was specified.
        """

        language = language or settings.LANGUAGE_CODE
        value = super().get(language, default)
        return value if value is not None else default

    def set(self, language: str, value: str):
        """Sets the value in the specified language.

        Arguments:
            language:
                The language to set the value in.

            value:
                The value to set.
        """

        self[language] = value
        self.__dict__.update(self)
        return self

    def deconstruct(self) -> dict:
        """Deconstructs this value into a primitive type.

        Returns:
            A dictionary with all the localized values
            contained in this instance.
        """

        path = "localized_fields.value.%s" % self.__class__.__name__
        return path, [self.__dict__], {}

    def _interpret_value(self, value):
        """Interprets a value passed in the constructor as a
        :see:LocalizedValue.

        If string:
            Assumes it's the default language.

        If dict:
            Each key is a language and the value a string
            in that language.

        If list:
            Recurse into to apply rules above.

        Arguments:
            value:
                The value to interpret.
        """

        for lang_code, _ in settings.LANGUAGES:
            self.set(lang_code, self.default_value)

        if callable(value):
            value = value()

        if isinstance(value, str):
            self.set(settings.LANGUAGE_CODE, value)

        elif isinstance(value, dict):
            for lang_code, _ in settings.LANGUAGES:
                lang_value = value.get(lang_code, self.default_value)
                self.set(lang_code, lang_value)

        elif isinstance(value, Iterable):
            for val in value:
                self._interpret_value(val)

    def translate(self, language: Optional[str] = None) -> Optional[str]:
        """Gets the value in the specified language (or active language).

        Arguments:
            language:
                The language to get the value in. If not specified,
                the currently active language is used.

        Returns:
            The value in the specified (or active) language. If no value
            is available in the specified language, the value is returned
            in one of the fallback languages.
        """

        target_language = (
            language or translation.get_language() or settings.LANGUAGE_CODE
        )

        fallback_config = getattr(settings, "LOCALIZED_FIELDS_FALLBACKS", {})

        target_languages = fallback_config.get(
            target_language, [settings.LANGUAGE_CODE]
        )

        for lang_code in [target_language] + target_languages:
            value = self.get(lang_code)
            if value:
                return value or None

        return None

    def is_empty(self) -> bool:
        """Gets whether all the languages contain the default value."""

        for lang_code, _ in settings.LANGUAGES:
            if self.get(lang_code) != self.default_value:
                return False

        return True

    def __str__(self) -> str:
        """Gets the value in the current language or falls back to the next
        language if there's no value in the current language."""

        return self.translate() or ""

    def __eq__(self, other):
        """Compares :paramref:self to :paramref:other for equality.

        Returns:
            True when :paramref:self is equal to :paramref:other.
            And False when they are not.
        """

        if not isinstance(other, type(self)):
            if isinstance(other, str):
                return self.__str__() == other
            return False

        for lang_code, _ in settings.LANGUAGES:
            if self.get(lang_code) != other.get(lang_code):
                return False

        return True

    def __ne__(self, other):
        """Compares :paramref:self to :paramerf:other for in-equality.

        Returns:
            True when :paramref:self is not equal to :paramref:other.
            And False when they are.
        """

        return not self.__eq__(other)

    def __setattr__(self, language: str, value: str):
        """Sets the value for a language with the specified name.

        Arguments:
            language:
                The language to set the value in.

            value:
                The value to set.
        """

        self.set(language, value)

    def __repr__(self):  # pragma: no cover
        """Gets a textual representation of this object."""

        return "%s<%s> 0x%s" % (
            self.__class__.__name__,
            self.__dict__,
            id(self),
        )


class LocalizedStringValue(LocalizedValue):
    default_value = ""


class LocalizedFileValue(LocalizedValue):
    def __getattr__(self, name: str):
        """Proxies access to attributes to attributes of LocalizedFile."""

        value = self.get(translation.get_language())
        if hasattr(value, name):
            return getattr(value, name)
        raise AttributeError(
            "'{}' object has no attribute '{}'".format(
                self.__class__.__name__, name
            )
        )

    def __str__(self) -> str:
        """Returns string representation of value."""

        return str(super().__str__())

    @deprecation.deprecated(
        deprecated_in="4.6",
        removed_in="5.0",
        current_version="4.6",
        details="Use the translate() function instead.",
    )
    def localized(self):
        """Returns value for current language."""

        return self.get(translation.get_language())


class LocalizedBooleanValue(LocalizedValue):
    def translate(self):
        """Gets the value in the current language, or in the configured fallbck
        language."""

        value = super().translate()
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None

        if isinstance(value, bool):
            return value

        if value.lower() == "true":
            return True
        return False

    def __bool__(self):
        """Gets the value in the current language as a boolean."""
        value = self.translate()

        return value

    def __str__(self):
        """Returns string representation of value."""

        value = self.translate()
        return str(value) if value is not None else ""


class LocalizedNumericValue(LocalizedValue):
    def __int__(self):
        """Gets the value in the current language as an integer."""
        value = self.translate()
        if value is None:
            return self.default_value

        return int(value)

    def __str__(self) -> str:
        """Returns string representation of value."""

        value = self.translate()
        return str(value) if value is not None else ""

    def __float__(self):
        """Gets the value in the current language as a float."""
        value = self.translate()
        if value is None:
            return self.default_value

        return float(value)


class LocalizedIntegerValue(LocalizedNumericValue):
    """All values are integers."""

    default_value = None

    def translate(self):
        """Gets the value in the current language, or in the configured fallbck
        language."""

        value = super().translate()
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None

        return int(value)


class LocalizedFloatValue(LocalizedNumericValue):
    """All values are floats."""

    default_value = None

    def translate(self):
        """Gets the value in the current language, or in the configured
        fallback language."""
        value = super().translate()
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None

        return float(value)
