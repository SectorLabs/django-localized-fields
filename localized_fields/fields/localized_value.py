from django.conf import settings
from django.utils import translation


class LocalizedValue:
    """Represents the value of a :see:LocalizedField."""

    def __init__(self, keys: dict=None):
        """Initializes a new instance of :see:LocalizedValue.

        Arguments:
            keys:
                The keys to initialize this value with. Every
                key contains the value of this field in a
                different language.
        """

        if isinstance(keys, str):
            setattr(self, settings.LANGUAGE_CODE, keys)
        else:
            for lang_code, _ in settings.LANGUAGES:
                value = keys.get(lang_code) if keys else None
                setattr(self, lang_code, value)

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
        return getattr(self, language, None)

    def set(self, language: str, value: str):
        """Sets the value in the specified language.

        Arguments:
            language:
                The language to set the value in.

            value:
                The value to set.
        """

        setattr(self, language, value)
        return self

    def deconstruct(self) -> dict:
        """Deconstructs this value into a primitive type.

        Returns:
            A dictionary with all the localized values
            contained in this instance.
        """

        path = 'localized_fields.fields.LocalizedValue'
        return path, [self.__dict__], {}

    def __str__(self) -> str:
        """Gets the value in the current language, or falls
        back to the primary language if there's no value
        in the current language."""

        value = self.get(translation.get_language())

        if not value:
            value = self.get(settings.LANGUAGE_CODE)

        return value or ''
    
    def __bool__(self) -> bool:
        """Get thruthiness of the value in the current 
        language."""

        value = self.get(translation.get_language())

        return bool(value)

    def __repr__(self):  # pragma: no cover
        """Gets a textual representation of this object."""

        return 'LocalizedValue<%s> 0x%s' % (self.__dict__, id(self))
