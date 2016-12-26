from django import forms
from django.conf import settings
from django.test import TestCase
from django.utils.text import slugify

from localized_fields.fields import LocalizedAutoSlugField

from .fake_model import get_fake_model


class LocalizedAutoSlugFieldTestCase(TestCase):
    """Tests the :see:LocalizedAutoSlugField class."""

    TestModel = None

    @classmethod
    def setUpClass(cls):
        """Creates the test model in the database."""

        super(LocalizedAutoSlugFieldTestCase, cls).setUpClass()

        cls.TestModel = get_fake_model()

    def test_populate(self):
        """Tests whether the :see:LocalizedAutoSlugField's
        populating feature works correctly."""

        obj = self.TestModel()
        obj.title.en = 'this is my title'
        obj.save()

        assert obj.slug.get('en') == slugify(obj.title.en)

    def test_populate_multiple_languages(self):
        """Tests whether the :see:LocalizedAutoSlugField's
        populating feature correctly works for all languages."""

        obj = self.TestModel()

        for lang_code, lang_name in settings.LANGUAGES:
            obj.title.set(lang_code, 'title %s' % lang_name)

        obj.save()

        for lang_code, lang_name in settings.LANGUAGES:
            assert obj.slug.get(lang_code) == 'title-%s' % lang_name.lower()

    def test_unique_slug(self):
        """Tests whether the :see:LocalizedAutoSlugField
        correctly generates unique slugs."""

        obj = self.TestModel()
        obj.title.en = 'title'
        obj.save()

        another_obj = self.TestModel()
        another_obj.title.en = 'title'
        another_obj.save()

        assert another_obj.slug.en == 'title-1'

    @staticmethod
    def test_deconstruct():
        """Tests whether the :see:deconstruct
        function properly retains options
        specified in the constructor."""

        field = LocalizedAutoSlugField(populate_from='title')
        _, _, _, kwargs = field.deconstruct()

        assert 'populate_from' in kwargs
        assert kwargs['populate_from'] == field.populate_from

    @staticmethod
    def test_formfield():
        """Tests whether the :see:formfield method
        returns a valid form field that is hidden."""

        field = LocalizedAutoSlugField(populate_from='title')
        form_field = field.formfield()

        assert isinstance(form_field, forms.CharField)
        assert isinstance(form_field.widget, forms.HiddenInput)
