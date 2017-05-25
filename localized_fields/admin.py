from django.contrib.admin import ModelAdmin

from . import widgets
from .fields import LocalizedField


FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS = {
    LocalizedField: {'widget': widgets.AdminLocalizedFieldWidget},
}


class LocalizedFieldsAdminMixin(ModelAdmin):
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
        super(LocalizedFieldsAdminMixin, self).__init__(*args, **kwargs)
        overrides = FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS.copy()
        overrides.update(self.formfield_overrides)
        self.formfield_overrides = overrides
