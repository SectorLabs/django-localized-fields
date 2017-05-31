from datetime import datetime

from django.utils.text import slugify
from django.core.exceptions import ImproperlyConfigured

from .autoslug_field import LocalizedAutoSlugField
from ..util import get_language_codes
from ..mixins import AtomicSlugRetryMixin
from ..value import LocalizedValue


class LocalizedUniqueSlugField(LocalizedAutoSlugField):
    """Automatically provides slugs for a localized
    field upon saving."

    An improved version of :see:LocalizedAutoSlugField,
    which adds:

        - Concurrency safety
        - Improved performance

    When in doubt, use this over :see:LocalizedAutoSlugField.
    Inherit from :see:AtomicSlugRetryMixin in your model to
    make this field work properly.
    """

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of :see:LocalizedUniqueSlugField."""

        kwargs['uniqueness'] = kwargs.pop('uniqueness', get_language_codes())

        super(LocalizedUniqueSlugField, self).__init__(
            *args,
            **kwargs
        )

        self.populate_from = kwargs.pop('populate_from')
        self.include_time = kwargs.pop('include_time', False)

    def deconstruct(self):
        """Deconstructs the field into something the database
        can store."""

        name, path, args, kwargs = super(
            LocalizedUniqueSlugField, self).deconstruct()

        kwargs['populate_from'] = self.populate_from
        kwargs['include_time'] = self.include_time
        return name, path, args, kwargs

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

        if not isinstance(instance, AtomicSlugRetryMixin):
            raise ImproperlyConfigured((
                'Model \'%s\' does not inherit from AtomicSlugRetryMixin. '
                'Without this, the LocalizedUniqueSlugField will not work.'
            ) % type(instance).__name__)

        slugs = LocalizedValue()

        for lang_code, value in self._get_populate_values(instance):
            if not value:
                continue

            slug = slugify(value, allow_unicode=True)

            # verify whether it's needed to re-generate a slug,
            # if not, re-use the same slug
            if instance.pk is not None:
                current_slug = getattr(instance, self.name).get(lang_code)
                if current_slug is not None:
                    stripped_slug = current_slug[0:current_slug.rfind('-')]
                    if slug == stripped_slug:
                        slugs.set(lang_code, current_slug)
                        continue

            if self.include_time:
                slug += '-%d' % datetime.now().microsecond

            retries = getattr(instance, 'retries', 0)
            if retries > 0:
                # do not add another - if we already added time
                if not self.include_time:
                    slug += '-'
                slug += '%d' % retries

            slugs.set(lang_code, slug)

        setattr(instance, self.name, slugs)
        return slugs
