from django.conf import settings
from django.test import TestCase

from localized_fields.value import LocalizedValue
from localized_fields.widgets import LocalizedFieldWidget


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

    @staticmethod
    def test_decompress_none():
        """Tests whether the :see:LocalizedFieldWidget correctly
        handles :see:None."""

        widget = LocalizedFieldWidget()
        decompressed_values = widget.decompress(None)

        for _, value in zip(settings.LANGUAGES, decompressed_values):
            assert not value

    @staticmethod
    def test_get_context():
        """Tests whether the :see:get_context correctly
        handles 'required' attribute, separately for each subwidget."""

        widget = LocalizedFieldWidget()
        widget.widgets[0].is_required = True
        widget.widgets[1].is_required = False
        context = widget.get_context(name='test', value=LocalizedValue(),
                                     attrs=dict(required=True))
        assert context['widget']['subwidgets'][0]['attrs']['required']
        assert 'required' not in context['widget']['subwidgets'][1]['attrs']
