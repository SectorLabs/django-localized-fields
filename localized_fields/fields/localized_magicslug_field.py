from django.conf import settings
from django.utils.text import slugify

from ..localized_value import LocalizedValue
from .localized_autoslug_field import LocalizedAutoSlugField
from ..util import get_language_codes


class LocalizedMagicSlugField(LocalizedAutoSlugField):
    """Automatically provides slugs for a localized
    field upon saving."

    An improved version of :see:LocalizedAutoSlugField,
    which adds:

        - Concurrency safety
        - Improved performance

    When in doubt, use this over :see:LocalizedAutoSlugField.
    """

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of :see:LocalizedMagicSlugField."""

        self.populate_from = kwargs.pop('populate_from')
        kwargs['uniqueness'] = kwargs.pop('uniqueness', get_language_codes())

        super(LocalizedAutoSlugField, self).__init__(
            *args,
            **kwargs
        )

    def pre_save(self, instance, add: bool):
        """Ran just before the model is saved, allows us to built
        the slug.

        Arguments:
            instance:
                The model that is being saved.

            add:
                Indicates whether this is a new entry
                to the database or an update.

        Returns:
            The localized slug that was generated.
        """

        slugs = LocalizedValue()

        for lang_code, _ in settings.LANGUAGES:
            value = self._get_populate_from_value(
                instance,
                self.populate_from,
                lang_code
            )

            if not value:
                continue

            slug = slugify(value, allow_unicode=True)
            if instance.retries > 0:
                slug += '-%d' % instance.retries

            slugs.set(lang_code, slug)

        setattr(instance, self.name, slugs)
        return slugs
