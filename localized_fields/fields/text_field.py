from ..forms import LocalizedTextFieldForm
from .char_field import LocalizedCharField


class LocalizedTextField(LocalizedCharField):
    def formfield(self, **kwargs):
        """Gets the form field associated with this field."""

        defaults = {
            'form_class': LocalizedTextFieldForm
        }

        defaults.update(kwargs)
        return super().formfield(**defaults)
