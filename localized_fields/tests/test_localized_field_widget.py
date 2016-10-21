from django.conf import settings
from django.test import TestCase

from ..fields import LocalizedValue
from ..forms import LocalizedFieldWidget


class LocalizedFieldWidgetTestCase(TestCase):
    """Tests the workings of the :see:LocalizedFieldWidget class."""

    @staticmethod
    def test_widget_creation():
        """Tests whether a widget is created for every
        language correctly."""

        widget = LocalizedFieldWidget()
        assert len(widget.widgets) == len(settings.LANGUAGES)

    @staticmethod
    def test_decompress():
        """Tests whether a :see:LocalizedValue instance
        can correctly be "decompressed" over the available
        widgets."""

        localized_value = LocalizedValue()
        for lang_code, lang_name in settings.LANGUAGES:
            localized_value.set(lang_code, lang_name)

        widget = LocalizedFieldWidget()
        decompressed_values = widget.decompress(localized_value)

        for (lang_code, _), value in zip(settings.LANGUAGES, decompressed_values):
            assert localized_value.get(lang_code) == value
