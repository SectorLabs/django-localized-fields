from django.test import TestCase

from localized_fields.value import LocalizedFileValue
from localized_fields.widgets import LocalizedFileWidget


class LocalizedFileWidgetTestCase(TestCase):
    """Tests the workings of the :see:LocalizedFiledWidget class."""

    @staticmethod
    def test_get_context():
        """Tests whether the :see:get_context correctly
        handles 'required' attribute, separately for each subwidget."""

        widget = LocalizedFileWidget()
        widget.widgets[0].is_required = True
        widget.widgets[1].is_required = True
        widget.widgets[2].is_required = False
        context = widget.get_context(name='test',
                                     value=LocalizedFileValue(dict(en='test')),
                                     attrs=dict(required=True))
        assert 'required' not in context['widget']['subwidgets'][0]['attrs']
        assert context['widget']['subwidgets'][1]['attrs']['required']
        assert 'required' not in context['widget']['subwidgets'][2]['attrs']
