from typing import List, Union

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms.widgets import FILE_INPUT_CONTRADICTION

from .value import LocalizedValue, LocalizedStringValue, \
    LocalizedFileValue, LocalizedIntegerValue
from .widgets import LocalizedFieldWidget, LocalizedCharFieldWidget, \
    LocalizedFileWidget, AdminLocalizedIntegerFieldWidget


class LocalizedFieldForm(forms.MultiValueField):
    """Form for a localized field, allows editing
    the field in multiple languages."""

    widget = LocalizedFieldWidget
    field_class = forms.fields.CharField
    value_class = LocalizedValue

    def __init__(self, *args, required: Union[bool, List[str]]=False, **kwargs):
        """Initializes a new instance of :see:LocalizedFieldForm."""

        fields = []

        for lang_code, _ in settings.LANGUAGES:
            field_options = dict(
                required=required if type(required) is bool else (lang_code in
                                                                  required),
                label=lang_code
            )
            fields.append(self.field_class(**field_options))

        super(LocalizedFieldForm, self).__init__(
            fields,
            required=required if type(required) is bool else True,
            require_all_fields=False,
            *args, **kwargs
        )

        # set 'required' attribute for each widget separately
        for field, widget in zip(self.fields, self.widget.widgets):
            widget.is_required = field.required

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
    """Form for a localized char field, allows editing
    the field in multiple languages."""

    widget = LocalizedCharFieldWidget
    value_class = LocalizedStringValue


class LocalizedTextFieldForm(LocalizedFieldForm):
    """Form for a localized text field, allows editing
    the field in multiple languages."""

    value_class = LocalizedStringValue


class LocalizedIntegerFieldForm(LocalizedFieldForm):
    """Form for a localized integer field, allows editing
    the field in multiple languages."""

    widget = AdminLocalizedIntegerFieldWidget
    value_class = LocalizedIntegerValue


class LocalizedFileFieldForm(LocalizedFieldForm, forms.FileField):
    """Form for a localized file field, allows editing
    the field in multiple languages."""

    widget = LocalizedFileWidget
    field_class = forms.fields.FileField
    value_class = LocalizedFileValue

    def clean(self, value, initial=None):
        """
        Most part of this method is a copy of
        django.forms.MultiValueField.clean, with the exception of initial
        value handling (this need for correct processing FileField's).
        All original comments saved.
        """
        if initial is None:
            initial = [None for x in range(0, len(value))]
        else:
            if not isinstance(initial, list):
                initial = self.widget.decompress(initial)

        clean_data = []
        errors = []
        if not value or isinstance(value, (list, tuple)):
            if (not value or not [v for v in value if
                                  v not in self.empty_values]) \
                    and (not initial or not [v for v in initial if
                                             v not in self.empty_values]):
                if self.required:
                    raise ValidationError(self.error_messages['required'],
                                          code='required')
        else:
            raise ValidationError(self.error_messages['invalid'],
                                  code='invalid')
        for i, field in enumerate(self.fields):
            try:
                field_value = value[i]
            except IndexError:
                field_value = None
            try:
                field_initial = initial[i]
            except IndexError:
                field_initial = None

            if field_value in self.empty_values and \
                    field_initial in self.empty_values:
                if self.require_all_fields:
                    # Raise a 'required' error if the MultiValueField is
                    # required and any field is empty.
                    if self.required:
                        raise ValidationError(self.error_messages['required'],
                                              code='required')
                elif field.required:
                    # Otherwise, add an 'incomplete' error to the list of
                    # collected errors and skip field cleaning, if a required
                    # field is empty.
                    if field.error_messages['incomplete'] not in errors:
                        errors.append(field.error_messages['incomplete'])
                    continue
            try:
                clean_data.append(field.clean(field_value, field_initial))
            except ValidationError as e:
                # Collect all validation errors in a single list, which we'll
                # raise at the end of clean(), rather than raising a single
                # exception for the first error we encounter. Skip duplicates.
                errors.extend(m for m in e.error_list if m not in errors)
        if errors:
            raise ValidationError(errors)

        out = self.compress(clean_data)
        self.validate(out)
        self.run_validators(out)
        return out

    def bound_data(self, data, initial):
        bound_data = []
        if initial is None:
            initial = [None for x in range(0, len(data))]
        else:
            if not isinstance(initial, list):
                initial = self.widget.decompress(initial)
        for d, i in zip(data, initial):
            if d in (None, FILE_INPUT_CONTRADICTION):
                bound_data.append(i)
            else:
                bound_data.append(d)
        return bound_data
