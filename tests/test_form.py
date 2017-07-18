from django.conf import settings
from django.test import TestCase

from localized_fields.forms import LocalizedFieldForm


class LocalizedFieldFormTestCase(TestCase):
    """Tests the workings of the :see:LocalizedFieldForm class."""

    @staticmethod
    def test_init():
        """Tests whether the constructor correctly
        creates a field for every language."""
        # case required for specific language
        form = LocalizedFieldForm(required=[settings.LANGUAGE_CODE])

        for (lang_code, _), field in zip(settings.LANGUAGES, form.fields):
            assert field.label == lang_code

            if lang_code == settings.LANGUAGE_CODE:
                assert field.required
            else:
                assert not field.required

        # case required for all languages
        form = LocalizedFieldForm(required=True)
        assert form.required
        for field in form.fields:
            assert field.required

        # case optional filling
        form = LocalizedFieldForm(required=False)
        assert not form.required
        for field in form.fields:
            assert not field.required

        # case required for any language
        form = LocalizedFieldForm(required=[])
        assert form.required
        for field in form.fields:
            assert not field.required


    @staticmethod
    def test_compress():
        """Tests whether the :see:compress function
        is working properly."""

        input_value = [lang_name for _, lang_name in settings.LANGUAGES]
        output_value = LocalizedFieldForm().compress(input_value)

        for lang_code, lang_name in settings.LANGUAGES:
            assert output_value.get(lang_code) == lang_name
