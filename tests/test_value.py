from django.db.models import F
from django.conf import settings
from django.utils import translation
from django.test import TestCase, override_settings

from localized_fields.value import LocalizedValue

from .data import get_init_values


class LocalizedValueTestCase(TestCase):
    """Tests the :see:LocalizedValue class."""

    @staticmethod
    def tearDown():
        """Assures that the current language
        is set back to the default."""

        translation.activate(settings.LANGUAGE_CODE)

    @staticmethod
    def test_init():
        """Tests whether the __init__ function
        of the :see:LocalizedValue class works
        as expected."""

        keys = get_init_values()
        value = LocalizedValue(keys)

        for lang_code, _ in settings.LANGUAGES:
            assert getattr(value, lang_code, None) == keys[lang_code]

    @staticmethod
    def test_init_default_values():
        """Tests whether the __init__ function
        of the :see:LocalizedValue accepts the
        default value or an empty dict properly."""

        value = LocalizedValue()

        for lang_code, _ in settings.LANGUAGES:
            assert getattr(value, lang_code) is None

    @staticmethod
    def test_init_array():
        """Tests whether the __init__ function
        of :see:LocalizedValue properly handles an
        array.

        Arrays can be passed to LocalizedValue as
        a result of a ArrayAgg operation."""

        value = LocalizedValue(['my value'])
        assert value.get(settings.LANGUAGE_CODE) == 'my value'

    @staticmethod
    def test_get_explicit():
        """Tests whether the the :see:LocalizedValue
        class's :see:get function works properly
        when specifying an explicit value."""

        keys = get_init_values()
        localized_value = LocalizedValue(keys)

        for language, value in keys.items():
            assert localized_value.get(language) == value

    @staticmethod
    def test_get_default_language():
        """Tests whether the :see:LocalizedValue
        class's see:get function properly
        gets the value in the default language."""

        keys = get_init_values()
        localized_value = LocalizedValue(keys)

        for language, _ in keys.items():
            translation.activate(language)
            assert localized_value.get() == keys[settings.LANGUAGE_CODE]

    @staticmethod
    def test_set():
        """Tests whether the :see:LocalizedValue
        class's see:set function works properly."""

        localized_value = LocalizedValue()

        for language, value in get_init_values():
            localized_value.set(language, value)
            assert localized_value.get(language) == value
            assert getattr(localized_value, language) == value

    @staticmethod
    def test_eq():
        """Tests whether the __eq__ operator
        of :see:LocalizedValue works properly."""

        a = LocalizedValue({'en': 'a', 'ar': 'b'})
        b = LocalizedValue({'en': 'a', 'ar': 'b'})

        assert a == b

        b.en = 'b'
        assert a != b

    @staticmethod
    def test_translate():
        """Tests whether the :see:LocalizedValue
        class's __str__ works properly."""

        keys = get_init_values()
        localized_value = LocalizedValue(keys)

        for language, value in keys.items():
            translation.activate(language)
            assert localized_value.translate() == value

    @staticmethod
    def test_translate_fallback():
        """Tests whether the :see:LocalizedValue
        class's translate()'s fallback functionality
        works properly."""

        test_value = 'myvalue'

        localized_value = LocalizedValue({
            settings.LANGUAGE_CODE: test_value
        })

        other_language = settings.LANGUAGES[-1][0]

        # make sure that, by default it returns
        # the value in the default language
        assert localized_value.translate() == test_value

        # make sure that it falls back to the
        # primary language when there's no value
        # available in the current language
        translation.activate(other_language)
        assert localized_value.translate() == test_value

        # make sure that it's just __str__ falling
        # back and that for the other language
        # there's no actual value
        assert localized_value.get(other_language) != test_value

    @staticmethod
    def test_translate_none():
        """Tests whether the :see:LocalizedValue
        class's translate() method properly returns
        None when there is no value."""

        # with no value, we always expect it to return None
        localized_value = LocalizedValue()
        assert localized_value.translate() is None
        assert str(localized_value) == ''

        # with no value for the default language, the default
        # behavior is to return None, unless a custom fallback
        # chain is configured, which there is not for this test
        other_language = settings.LANGUAGES[-1][0]
        localized_value = LocalizedValue({
            other_language: 'hey'
        })

        translation.activate(settings.LANGUAGE_CODE)
        assert localized_value.translate() is None
        assert str(localized_value) == ''

    @staticmethod
    def test_translate_fallback_custom_fallback():
        """Tests whether the :see:LocalizedValue class's
        translate()'s fallback functionality properly respects
        the LOCALIZED_FIELDS_FALLBACKS setting."""

        fallbacks = {
            'nl': ['ro']
        }

        localized_value = LocalizedValue({
            settings.LANGUAGE_CODE: settings.LANGUAGE_CODE,
            'ro': 'ro'
        })

        with override_settings(LOCALIZED_FIELDS_FALLBACKS=fallbacks):
            with translation.override('nl'):
                assert localized_value.translate() == 'ro'

    @staticmethod
    def test_deconstruct():
        """Tests whether the :see:LocalizedValue
        class's :see:deconstruct function works properly."""

        keys = get_init_values()
        value = LocalizedValue(keys)

        path, args, kwargs = value.deconstruct()

        assert args[0] == keys

    @staticmethod
    def test_construct_string():
        """Tests whether the :see:LocalizedValue's constructor
        assumes the primary language when passing a single string."""

        value = LocalizedValue('beer')
        assert value.get(settings.LANGUAGE_CODE) == 'beer'

    @staticmethod
    def test_construct_expression():
        """Tests whether passing expressions as values
        works properly and are not converted to string."""

        value = LocalizedValue(dict(en=F('other')))
        assert isinstance(value.en, F)
