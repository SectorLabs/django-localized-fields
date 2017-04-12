from django.conf import settings
from django.utils import translation


class LocalizedValue(dict):
    """Represents the value of a :see:LocalizedField."""
    default_value = None

    def __init__(self, keys: dict=None):
        """Initializes a new instance of :see:LocalizedValue.

        Arguments:
            keys:
                The keys to initialize this value with. Every
                key contains the value of this field in a
                different language.
        """

        # NOTE(seroy): First fill all the keys with default value,
        # in order to attributes will be for each language
        for lang_code, _ in settings.LANGUAGES:
            value = keys.get(lang_code) if isinstance(keys, dict) else \
                self.default_value
            self.set(lang_code, value)

        if isinstance(keys, str):
            setattr(self, settings.LANGUAGE_CODE, keys)

    def get(self, language: str=None) -> str:
        """Gets the underlying value in the specified or
        primary language.

        Arguments:
            language:
                The language to get the value in.

        Returns:
            The value in the current language, or
            the primary language in case no language
            was specified.
        """

        language = language or settings.LANGUAGE_CODE
        return super().get(language, None)

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

        path = 'localized_fields.localized_value.%s' % self.__class__.__name__
        return path, [self.__dict__], {}

    def __str__(self) -> str:
        """Gets the value in the current language, or falls
        back to the primary language if there's no value
        in the current language."""

        value = self.get(translation.get_language())

        if not value:
            value = self.get(settings.LANGUAGE_CODE)

        return value or ''

    def __eq__(self, other):
        """Compares :paramref:self to :paramref:other for
        equality.

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
        """Compares :paramref:self to :paramerf:other for
        in-equality.

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

        return '%s<%s> 0x%s' % (self.__class__.__name__,
                                self.__dict__, id(self))


class LocalizedStingValue(LocalizedValue):
    default_value = ''


class LocalizedFileValue(LocalizedValue):

    def __getattr__(self, name):
        value = self.get(translation.get_language())
        if hasattr(value, name):
            return getattr(value, name)
        raise AttributeError("'{}' object has no attribute '{}'".
                             format(self.__class__.__name__, name))

    def __str__(self):
        return str(super().__str__())

    def localized(self):
        return self.get(translation.get_language())
