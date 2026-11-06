import html

import bleach

from django.conf import settings
from django.test import TestCase, override_settings
from django_bleach.utils import get_bleach_default_options

from localized_fields.fields import LocalizedBleachField
from localized_fields.value import LocalizedValue

strip_tags = override_settings(
    BLEACH_STRIP_TAGS=True,
    BLEACH_STRIP_COMMENTS=True,
    BLEACH_ALLOWED_TAGS=["p", "b", "i", "u", "em", "strong", "ul", "li", "ol"],
)

IMG_PAYLOAD = "<img src=x onerror=alert(1)>"


def escape_times(value, times):
    for _ in range(times):
        value = html.escape(value)

    return value


class ModelTest:
    """Used to declare a bleach-able field on."""

    def __init__(self, value):
        """Initializes a new instance of :see:ModelTest.

        Arguments:
            The value to initialize with.
        """

        self.value = value


class LocalizedBleachFieldTestCase(TestCase):
    """Tests the :see:LocalizedBleachField class."""

    def test_pre_save(self):
        """Tests whether the :see:pre_save function bleaches all values in a
        :see:LocalizedValue."""

        value = self._get_test_value()
        model, field = self._get_test_model(value)

        bleached_value = field.pre_save(model, False)
        self._validate(value, bleached_value)

    def test_pre_save_none(self):
        """Tests whether the :see:pre_save function works properly when
        specifying :see:None."""

        model, field = self._get_test_model(None)

        bleached_value = field.pre_save(model, False)
        assert not bleached_value

    def test_pre_save_none_values(self):
        """Tests whether the :see:pre_save function works properly when one of
        the languages has no text and is None."""

        value = self._get_test_value()
        value.set(settings.LANGUAGE_CODE, None)

        model, field = self._get_test_model(value)

        bleached_value = field.pre_save(model, False)
        self._validate(value, bleached_value)

    def test_pre_save_do_not_escape(self):
        """Tests whether the :see:pre_save function works properly when field
        escape argument is set to False."""

        value = self._get_test_value()
        model, field = self._get_test_model(value, escape=False)

        bleached_value = field.pre_save(model, False)
        self._validate(value, bleached_value, False)

    def test_max_clean_passes_validation(self):
        """Tests whether only None and positive integers are accepted for
        max_clean_passes."""

        for max_clean_passes in (0, -1, True, "5", 1.5):
            with self.subTest(max_clean_passes=max_clean_passes):
                with self.assertRaises(ValueError):
                    LocalizedBleachField(max_clean_passes=max_clean_passes)

        for max_clean_passes in (None, 1, 10):
            with self.subTest(max_clean_passes=max_clean_passes):
                field = LocalizedBleachField(max_clean_passes=max_clean_passes)
                assert field.max_clean_passes == max_clean_passes

    def test_max_clean_passes_deconstruct(self):
        """Tests whether max_clean_passes is only included in migrations when
        set, and survives a round trip."""

        _, _, _, kwargs = LocalizedBleachField().deconstruct()
        assert "max_clean_passes" not in kwargs

        _, _, args, kwargs = LocalizedBleachField(
            escape=False, max_clean_passes=5
        ).deconstruct()
        assert kwargs["max_clean_passes"] == 5

        field = LocalizedBleachField(*args, **kwargs)
        assert field.max_clean_passes == 5
        assert field.escape is False

    @strip_tags
    def test_pre_save_single_pass_revives_markup(self):
        """Tests that without max_clean_passes, escape=False keeps today's
        single pass, which can leave markup in the stored value."""

        assert (
            self._pre_save(
                "Nice <<span>img src=x onerror=alert(1)>", escape=False
            )
            == "Nice <img src=x onerror=alert(1)>"
        )

    @strip_tags
    def test_pre_save_max_clean_passes_payloads(self):
        """Tests whether max_clean_passes removes markup that was escaped any
        number of times, and the result is stable."""

        payloads = ["Nice <<span>img src=x onerror=alert(1)>"] + [
            escape_times(IMG_PAYLOAD, layers) for layers in range(1, 16)
        ]

        for escape in (True, False):
            for payload in payloads:
                with self.subTest(escape=escape, payload=payload):
                    value = LocalizedValue({settings.LANGUAGE_CODE: payload})
                    model, field = self._get_test_model(
                        value, escape=escape, max_clean_passes=10
                    )

                    stored = field.pre_save(model, False).get(
                        settings.LANGUAGE_CODE
                    )
                    assert "<" not in stored
                    assert "onerror" not in html.unescape(stored)

                    assert (
                        field.pre_save(model, False).get(settings.LANGUAGE_CODE)
                        == stored
                    )

    @strip_tags
    def test_pre_save_max_clean_passes_text(self):
        """Tests whether max_clean_passes keeps ordinary text and allowed
        tags."""

        cases = [
            ("Tom &amp; Jerry", True, "Tom &amp; Jerry"),
            ("Tom &amp; Jerry", False, "Tom & Jerry"),
            ("a <b>bold</b> < b", True, "a <b>bold</b> &lt; b"),
            ("a <b>bold</b> < b", False, "a <b>bold</b> < b"),
            (
                "Use &amp;lt;b&amp;gt;bold&amp;lt;/b&amp;gt;",
                True,
                "Use <b>bold</b>",
            ),
            ("Nice <<span>img src=x onerror=alert(1)>", True, "Nice "),
            ("Nice <<span>img src=x onerror=alert(1)>", False, "Nice "),
        ]

        for text, escape, expected in cases:
            with self.subTest(text=text, escape=escape):
                assert self._pre_save(
                    text, escape=escape, max_clean_passes=5
                ) == (expected)

    @strip_tags
    def test_pre_save_max_clean_passes_limit(self):
        """Tests whether a value that is still changing after max_clean_passes
        passes is stored as an empty string."""

        # Escaped 10 times needs exactly 5 changing passes, 11 times needs 6.
        for escape in (True, False):
            with self.subTest(escape=escape):
                assert self._pre_save(
                    escape_times("Tom & Jerry", 10),
                    escape=escape,
                    max_clean_passes=5,
                ) == ("Tom &amp; Jerry" if escape else "Tom & Jerry")

                assert (
                    self._pre_save(
                        escape_times("Tom & Jerry", 11),
                        escape=escape,
                        max_clean_passes=5,
                    )
                    == ""
                )

    @strip_tags
    def test_pre_save_max_clean_passes_per_language(self):
        """Tests whether only the language that is still changing after
        max_clean_passes passes is emptied."""

        value = LocalizedValue()
        for lang_code, lang_name in settings.LANGUAGES:
            value.set(lang_code, lang_name)

        other_lang_code = settings.LANGUAGES[1][0]
        value.set(other_lang_code, escape_times("Tom & Jerry", 12))

        model, field = self._get_test_model(
            value, escape=False, max_clean_passes=2
        )
        bleached_value = field.pre_save(model, False)

        for lang_code, lang_name in settings.LANGUAGES:
            expected = "" if lang_code == other_lang_code else lang_name
            assert bleached_value.get(lang_code) == expected

    def _pre_save(self, text, **field_kwargs):
        """Runs :see:pre_save on a value with the text in the default language
        and returns the stored text."""

        value = LocalizedValue({settings.LANGUAGE_CODE: text})
        model, field = self._get_test_model(value, **field_kwargs)

        return field.pre_save(model, False).get(settings.LANGUAGE_CODE)

    @staticmethod
    def _get_test_model(value, escape=True, max_clean_passes=None):
        """Gets a test model and an artificially constructed
        :see:LocalizedBleachField instance to test with."""

        model = ModelTest(value)

        field = LocalizedBleachField(
            escape=escape, max_clean_passes=max_clean_passes
        )
        field.attname = "value"
        return model, field

    @staticmethod
    def _get_test_value():
        """Gets a :see:LocalizedValue instance for testing."""

        value = LocalizedValue()

        for lang_code, lang_name in settings.LANGUAGES:
            value.set(lang_code, "<script>%s</script>" % lang_name)

        return value

    @staticmethod
    def _validate(non_bleached_value, bleached_value, escaped_value=True):
        """Validates whether the specified non-bleached value ended up being
        correctly bleached.

        Arguments:
            non_bleached_value:
                The value before bleaching.

            bleached_value:
                The value after bleaching.
        """
        for lang_code, _ in settings.LANGUAGES:
            if not non_bleached_value.get(lang_code):
                assert not bleached_value.get(lang_code)
                continue

            cleaned_value = bleach.clean(
                non_bleached_value.get(lang_code)
                if escaped_value
                else html.unescape(non_bleached_value.get(lang_code)),
                **get_bleach_default_options(),
            )

            expected_value = (
                cleaned_value if escaped_value else html.unescape(cleaned_value)
            )

            assert bleached_value.get(lang_code) == expected_value
