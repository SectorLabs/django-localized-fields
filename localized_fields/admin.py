from django.contrib.admin import ModelAdmin

from . import widgets
from .fields import LocalizedField


FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS = {
    LocalizedField: {'widget': widgets.AdminLocalizedFieldWidget},
}


class LocalizedFieldsAdminMixin(ModelAdmin):
    """Mixin for making the fancy widgets work in Django Admin."""

    class Media:
        css = {
            'all': (
                'localized_fields/localized-fields-admin.css',
            )
        }

        js = (
            'localized_fields/localized-fields-admin.js',
        )

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of :see:LocalizedFieldsAdminMixin."""

        super(LocalizedFieldsAdminMixin, self).__init__(*args, **kwargs)
        overrides = FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS.copy()
        overrides.update(self.formfield_overrides)
        self.formfield_overrides = overrides
