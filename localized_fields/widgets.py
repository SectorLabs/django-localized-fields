import copy

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
            copy.copy(self.widget)
            for _ in settings.LANGUAGES
        ]

        super().__init__(initial_widgets, *args, **kwargs)

        for ((lang_code, lang_name), widget) in zip(settings.LANGUAGES, self.widgets):
            widget.attrs['lang'] = lang_code
            widget.lang_code = lang_code
            widget.lang_name = lang_name

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

    def get_context(self, name, value, attrs):
        context = super(forms.MultiWidget, self).get_context(name, value, attrs)
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)

        final_attrs = context['widget']['attrs']
        input_type = final_attrs.pop('type', None)
        id_ = final_attrs.get('id')
        subwidgets = []
        for i, widget in enumerate(self.widgets):
            if input_type is not None:
                widget.input_type = input_type
            widget_name = '%s_%s' % (name, i)
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            if id_:
                widget_attrs = final_attrs.copy()
                widget_attrs['id'] = '%s_%s' % (id_, i)
            else:
                widget_attrs = final_attrs
            widget_attrs = self.build_widget_attrs(widget, widget_value, widget_attrs)
            widget_context = widget.get_context(widget_name, widget_value, widget_attrs)['widget']
            widget_context.update(dict(
                lang_code=widget.lang_code,
                lang_name=widget.lang_name
            ))
            subwidgets.append(widget_context)
        context['widget']['subwidgets'] = subwidgets
        return context

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


class AdminLocalizedIntegerFieldWidget(AdminLocalizedFieldWidget):
    widget = widgets.AdminIntegerFieldWidget
