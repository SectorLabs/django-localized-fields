import inspect

from django.apps import AppConfig
from django.conf import settings

from . import lookups
from .fields import LocalizedField
from .lookups import LocalizedLookupMixin


class LocalizedFieldsConfig(AppConfig):
    name = "localized_fields"

    def ready(self):
        if getattr(settings, "LOCALIZED_FIELDS_EXPERIMENTAL", False):
            for _, clazz in inspect.getmembers(lookups):
                if not inspect.isclass(clazz) or clazz is LocalizedLookupMixin:
                    continue

                if issubclass(clazz, LocalizedLookupMixin):
                    LocalizedField.register_lookup(clazz)
