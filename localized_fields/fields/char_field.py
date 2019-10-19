from ..forms import LocalizedCharFieldForm
from ..value import LocalizedStringValue
from .field import LocalizedField


class LocalizedCharField(LocalizedField):
    attr_class = LocalizedStringValue

    def formfield(self, **kwargs):
        """Gets the form field associated with this field."""
        defaults = {"form_class": LocalizedCharFieldForm}

        defaults.update(kwargs)
        return super().formfield(**defaults)
