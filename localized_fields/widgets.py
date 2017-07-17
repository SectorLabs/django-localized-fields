from typing import List

from django.conf import settings
from django import forms
from django.contrib.admin import widgets

from .value import LocalizedValue


class LocalizedFieldWidget(forms.MultiWidget):
    """Widget that has an input box for every language."""
    template_name = 'localized_fields/multiwidget.html'
    widget = forms.Textarea

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of :see:LocalizedFieldWidget."""

        initial_widgets = [
            self.widget
            for _ in settings.LANGUAGES
        ]

        super().__init__(initial_widgets, *args, **kwargs)

        for ((lang_code, lang_name), widget) in zip(settings.LANGUAGES, self.widgets):
            widget.attrs['lang_code'] = lang_code
            widget.attrs['lang_name'] = lang_name

    def decompress(self, value: LocalizedValue) -> List[str]:
        """Decompresses the specified value so
        it can be spread over the internal widgets.

        Arguments:
            value:
                The :see:LocalizedValue to display in this
                widget.

        Returns:
            All values to display in the inner widgets.
        """

        result = []
        for lang_code, _ in settings.LANGUAGES:
            if value:
                result.append(value.get(lang_code))
            else:
                result.append(None)

        return result

    @staticmethod
    def build_widget_attrs(widget, value, attrs):
        attrs = dict(attrs)  # Copy attrs to avoid modifying the argument.

        if (not widget.use_required_attribute(value) or not widget.is_required) \
                and 'required' in attrs:
            del attrs['required']

        return attrs


class LocalizedCharFieldWidget(LocalizedFieldWidget):
    """Widget that has an input box for every language."""
    widget = forms.TextInput


class LocalizedFileWidget(LocalizedFieldWidget):
    """Widget that has an file input box for every language."""
    widget = forms.ClearableFileInput


class AdminLocalizedFieldWidget(LocalizedFieldWidget):
    template_name = 'localized_fields/admin/widget.html'
    widget = widgets.AdminTextareaWidget


class AdminLocalizedCharFieldWidget(AdminLocalizedFieldWidget):
    widget = widgets.AdminTextInputWidget


class AdminLocalizedFileFieldWidget(AdminLocalizedFieldWidget):
    widget = widgets.AdminFileWidget
