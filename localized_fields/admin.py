from django.contrib.admin import ModelAdmin

from .fields import LocalizedField
from . import widgets


FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS = {
    LocalizedField: {'widget': widgets.AdminLocalizedFieldWidget},
}


class LocalizedFieldsAdminMixin(ModelAdmin):
    class Media:
        css = {
            'all': (
                'localized_fields/jquery-ui.all.css',
            )
        }
        js = (
            'localized_fields/jquery-django.js',
            'localized_fields/jquery-ui.min.js',
            'localized_fields/localized-fields-admin.js'
        )

    def __init__(self, *args, **kwargs):
        super(LocalizedFieldsAdminMixin, self).__init__(*args, **kwargs)
        overrides = FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS.copy()
        overrides.update(self.formfield_overrides)
        self.formfield_overrides = overrides
