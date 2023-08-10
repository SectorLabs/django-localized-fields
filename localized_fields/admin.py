from . import widgets
from .fields import (
    LocalizedBooleanField,
    LocalizedCharField,
    LocalizedField,
    LocalizedFileField,
    LocalizedTextField,
)

FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS = {
    LocalizedField: {"widget": widgets.AdminLocalizedFieldWidget},
    LocalizedCharField: {"widget": widgets.AdminLocalizedCharFieldWidget},
    LocalizedTextField: {"widget": widgets.AdminLocalizedFieldWidget},
    LocalizedFileField: {"widget": widgets.AdminLocalizedFileFieldWidget},
    LocalizedBooleanField: {"widget": widgets.AdminLocalizedBooleanFieldWidget},
}


class LocalizedFieldsAdminMixin:
    """Mixin for making the fancy widgets work in Django Admin."""

    class Media:
        css = {"all": ("localized_fields/localized-fields-admin.css",)}

        js = (
            "admin/js/jquery.init.js",
            "localized_fields/localized-fields-admin.js",
        )

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of :see:LocalizedFieldsAdminMixin."""

        super().__init__(*args, **kwargs)
        overrides = FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS.copy()
        overrides.update(self.formfield_overrides)
        self.formfield_overrides = overrides
