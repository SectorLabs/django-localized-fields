import html

from django.conf import settings

from .field import LocalizedField


class LocalizedBleachField(LocalizedField):
    """Custom version of :see:BleachField that is actually a
    :see:LocalizedField."""

    DEFAULT_SHOULD_ESCAPE = True

    def __init__(self, *args, escape=True, max_clean_passes=None, **kwargs):
        """Initializes a new instance of :see:LocalizedBleachField.

        Arguments:
            escape:
                Whether to store the value as bleach returns it.
                When False, the value is unescaped before and after
                cleaning.

            max_clean_passes:
                When set, the value is unescaped and cleaned
                repeatedly until it stops changing, at most this
                many times. A value that is still changing after
                that is stored as an empty string. When None, the
                value is cleaned once.
        """

        if max_clean_passes is not None and (
            isinstance(max_clean_passes, bool)
            or not isinstance(max_clean_passes, int)
            or max_clean_passes < 1
        ):
            raise ValueError(
                "max_clean_passes must be None or a positive integer, got %r."
                % (max_clean_passes,)
            )

        self.escape = escape
        self.max_clean_passes = max_clean_passes

        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()

        if self.escape != self.DEFAULT_SHOULD_ESCAPE:
            kwargs["escape"] = self.escape

        if self.max_clean_passes is not None:
            kwargs["max_clean_passes"] = self.max_clean_passes

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

        bleach_options = get_bleach_default_options()

        for lang_code, _ in settings.LANGUAGES:
            value = localized_value.get(lang_code)
            if not value:
                continue

            if self.max_clean_passes is None:
                cleaned_value = bleach.clean(
                    value if self.escape else html.unescape(value),
                    **bleach_options
                )
                if not self.escape:
                    cleaned_value = html.unescape(cleaned_value)
            else:
                cleaned_value = self._clean_until_stable(
                    value, bleach, bleach_options
                )

            localized_value.set(lang_code, cleaned_value)

        return localized_value

    def _clean_until_stable(self, value, bleach, bleach_options):
        """Unescapes and cleans the value until it stops changing.

        Returns an empty string when the value is still changing after
        :see:max_clean_passes passes.
        """

        # The extra pass only checks that the last result is stable.
        for _ in range(self.max_clean_passes + 1):
            bleached_value = bleach.clean(
                html.unescape(value), **bleach_options
            )
            cleaned_value = html.unescape(bleached_value)
            if cleaned_value == value:
                break

            value = cleaned_value
        else:
            return ""

        return bleached_value if self.escape else value
