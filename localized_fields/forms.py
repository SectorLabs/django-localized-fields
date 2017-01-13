from typing import List

from django import forms
from django.conf import settings

from .widgets import LocalizedFieldWidget, LocalizedCharFieldWidget
from .fields.localized_value import LocalizedValue, LocalizedStingValue


class LocalizedFieldForm(forms.MultiValueField):
    """Form for a localized field, allows editing
    the field in multiple languages."""

    widget = LocalizedFieldWidget
    value_class = LocalizedValue

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of :see:LocalizedFieldForm."""

        fields = []

        for lang_code, _ in settings.LANGUAGES:
            field_options = {'required': False}

            if lang_code == settings.LANGUAGE_CODE:
                field_options['required'] = True

            field_options['label'] = lang_code
            fields.append(forms.fields.CharField(**field_options))

        super(LocalizedFieldForm, self).__init__(
            fields,
            require_all_fields=False,
            *args, **kwargs
        )

    def compress(self, value: List[str]) -> value_class:
        """Compresses the values from individual fields
        into a single :see:LocalizedValue instance.

        Arguments:
            value:
                The values from all the widgets.

        Returns:
            A :see:LocalizedValue containing all
            the value in several languages.
        """

        localized_value = self.value_class()

        for (lang_code, _), value in zip(settings.LANGUAGES, value):
            localized_value.set(lang_code, value)

        return localized_value


class LocalizedCharFieldForm(LocalizedFieldForm):

    widget = LocalizedCharFieldWidget
    value_class = LocalizedStingValue


class LocalizedTextFieldForm(LocalizedFieldForm):

    value_class = LocalizedStingValue
