from datetime import datetime

from django.conf import settings
from django import forms
from django.utils.text import slugify
from django.db import transaction
from django.db.utils import IntegrityError


from ..util import get_language_codes
from ..localized_value import LocalizedValue
from .localized_field import LocalizedField


class LocalizedUniqueSlugField(LocalizedField):
    """Automatically provides slugs for a localized field upon saving."

    An improved version of :see:LocalizedAutoSlugField,
    which adds:

        - Concurrency safety
        - Improved performance

    When in doubt, use this over :see:LocalizedAutoSlugField.
    """

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of :see:LocalizedUniqueSlugField."""

        kwargs['uniqueness'] = kwargs.pop('uniqueness', get_language_codes())

        self.populate_from = kwargs.pop('populate_from')
        self.include_time = kwargs.pop('include_time', False)

        super().__init__(*args, **kwargs)

    def deconstruct(self):
        """Deconstructs the field into something the database
        can store."""

        name, path, args, kwargs = super(
            LocalizedUniqueSlugField, self).deconstruct()

        kwargs['populate_from'] = self.populate_from
        kwargs['include_time'] = self.include_time
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        """Gets the form field associated with this field.

        Because this is a slug field which is automatically
        populated, it should be hidden from the form.
        """

        defaults = {
            'form_class': forms.CharField,
            'required': False
        }

        defaults.update(kwargs)

        form_field = super().formfield(**defaults)
        form_field.widget = forms.HiddenInput()

        return form_field

    def contribute_to_class(self, cls, name, *args, **kwargs):
        """Hook that allow us to operate with model class. We overwrite save()
        method to run retry logic.

        Arguments:
            cls:
                Model class.

            name:
                Name of field in model.
        """
        # apparently in inheritance cases, contribute_to_class is called more
        # than once, so we have to be careful not to overwrite the original
        # save method.
        if not hasattr(cls, '_orig_save'):
            cls._orig_save = cls.save
            max_retries = getattr(
                settings,
                'LOCALIZED_FIELDS_MAX_RETRIES',
                100
            )

            def _new_save(instance, *args_, **kwargs_):
                retries = 0
                while True:
                    with transaction.atomic():
                        try:
                            slugs = self.populate_slugs(instance, retries)
                            setattr(instance, name, slugs)
                            instance._orig_save(*args_, **kwargs_)
                            break
                        except IntegrityError as e:
                            if retries >= max_retries:
                                raise e
                            # check to be sure a slug fight caused
                            # the IntegrityError
                            s_e = str(e)
                            if name in s_e and 'unique' in s_e:
                                retries += 1
                            else:
                                raise e

            cls.save = _new_save
        super().contribute_to_class(cls, name, *args, **kwargs)

    def populate_slugs(self, instance, retries=0):
        """Built the slug from populate_from field.

        Arguments:
            instance:
                The model that is being saved.

            retries:
                The value of the current attempt.

        Returns:
            The localized slug that was generated.
        """
        slugs = LocalizedValue()
        populates_slugs = getattr(instance, self.populate_from, {})
        for lang_code, _ in settings.LANGUAGES:

            value = populates_slugs.get(lang_code)

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

            if retries > 0:
                # do not add another - if we already added time
                if not self.include_time:
                    slug += '-'
                slug += '%d' % retries

            slugs.set(lang_code, slug)
        return slugs
