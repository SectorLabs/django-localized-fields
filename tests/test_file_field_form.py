from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms.widgets import FILE_INPUT_CONTRADICTION
from django.test import TestCase

from localized_fields.forms import LocalizedFileFieldForm


class LocalizedFileFieldFormTestCase(TestCase):
    """Tests the workings of the :see:LocalizedFileFieldForm class."""

    def test_clean(self):
        """Tests whether the :see:clean function is working properly."""

        formfield = LocalizedFileFieldForm(required=True)
        with self.assertRaises(ValidationError):
            formfield.clean([])
        with self.assertRaises(ValidationError):
            formfield.clean([], {'en': None})
        with self.assertRaises(ValidationError):
            formfield.clean("badvalue")
        with self.assertRaises(ValidationError):
            value = [FILE_INPUT_CONTRADICTION] * len(settings.LANGUAGES)
            formfield.clean(value)

        formfield = LocalizedFileFieldForm(required=False)
        formfield.clean([''] * len(settings.LANGUAGES))
        formfield.clean(['', ''], ['', ''])

    def test_bound_data(self):
        """Tests whether the :see:bound_data function is returns correctly
        value"""

        formfield = LocalizedFileFieldForm()
        assert formfield.bound_data([''], None) == ['']

        initial = dict([(lang, '') for lang, _ in settings.LANGUAGES])
        value = [None] * len(settings.LANGUAGES)
        expected_value = [''] * len(settings.LANGUAGES)
        assert formfield.bound_data(value, initial) == expected_value
