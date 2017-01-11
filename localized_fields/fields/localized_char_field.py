from ..forms import LocalizedCharFieldForm
from .localized_field import LocalizedField
from .localized_value import LocalizedStingValue


class LocalizedCharField(LocalizedField):
    attr_class = LocalizedStingValue

    def formfield(self, **kwargs):
        """Gets the form field associated with this field."""
        defaults = {
            'form_class': LocalizedCharFieldForm
        }

        defaults.update(kwargs)
        return super().formfield(**defaults)
