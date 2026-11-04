import html

from django.conf import settings

from .field import LocalizedField


class LocalizedBleachField(LocalizedField):
    """Custom version of :see:BleachField that is actually a
    :see:LocalizedField."""

    DEFAULT_SHOULD_ESCAPE = True

    def __init__(self, *args, escape=True, **kwargs):
        """Initializes a new instance of :see:LocalizedBleachField."""

        self.escape = escape

        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()

        if self.escape != self.DEFAULT_SHOULD_ESCAPE:
            kwargs["escape"] = self.escape

        return name, path, args, kwargs

    def pre_save(self, instance, add: bool):
        """Ran just before the model is saved, allows us to built the slug.

        Arguments:
            instance:
                The model that is being saved.

            add:
                Indicates whether this is a new entry
                to the database or an update.
        """

        try:
            import bleach

            from django_bleach.utils import get_bleach_default_options
        except ImportError:
            raise UserWarning(
                "LocalizedBleachField requires django-bleach, install it with `pip install django-bleach`."
            )

        localized_value = getattr(instance, self.attname)
        if not localized_value:
            return None

        for lang_code, _ in settings.LANGUAGES:
            value = localized_value.get(lang_code)
            if not value:
                continue

            cleaned_value = bleach.clean(
                value if self.escape else html.unescape(value),
                **get_bleach_default_options()
            )

            localized_value.set(
                lang_code,
                cleaned_value if self.escape else html.unescape(cleaned_value),
            )

        return localized_value
