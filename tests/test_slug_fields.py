import copy

import pytest

from django import forms
from django.conf import settings
from django.db import models
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils.text import slugify

from localized_fields.fields import LocalizedField, LocalizedUniqueSlugField

from .fake_model import get_fake_model


class LocalizedSlugFieldTestCase(TestCase):
    """Tests the localized slug classes."""

    AutoSlugModel = None
    Model = None

    @classmethod
    def setUpClass(cls):
        """Creates the test models in the database."""

        super(LocalizedSlugFieldTestCase, cls).setUpClass()

        cls.Model = get_fake_model(
            {
                "title": LocalizedField(),
                "name": models.CharField(max_length=255),
                "slug": LocalizedUniqueSlugField(populate_from="title"),
            }
        )

    @staticmethod
    def test_unique_slug_with_time():
        """Tests whether the primary key is included in the slug when the
        'use_pk' option is enabled."""

        title = "myuniquetitle"

        PkModel = get_fake_model(
            {
                "title": LocalizedField(),
                "slug": LocalizedUniqueSlugField(
                    populate_from="title", include_time=True
                ),
            }
        )

        obj = PkModel()
        obj.title.en = title
        obj.save()

        assert obj.slug.en.startswith("%s-" % title)

    @classmethod
    def test_uniue_slug_no_change(cls):
        """Tests whether slugs are not re-generated if not needed."""

        NoChangeSlugModel = get_fake_model(
            {
                "title": LocalizedField(),
                "slug": LocalizedUniqueSlugField(
                    populate_from="title", include_time=True
                ),
            }
        )

        title = "myuniquetitle"

        obj = NoChangeSlugModel()
        obj.title.en = title
        obj.title.nl = title
        obj.save()

        old_slug_en = copy.deepcopy(obj.slug.en)
        old_slug_nl = copy.deepcopy(obj.slug.nl)
        obj.title.nl += "beer"
        obj.save()

        assert old_slug_en == obj.slug.en
        assert old_slug_nl != obj.slug.nl

    @classmethod
    def test_unique_slug_update(cls):
        obj = cls.Model.objects.create(
            title={settings.LANGUAGE_CODE: "mytitle"}
        )
        assert obj.slug.get() == "mytitle"
        obj.title.set(settings.LANGUAGE_CODE, "othertitle")
        obj.save()
        assert obj.slug.get() == "othertitle"

    @classmethod
    def test_unique_slug_unique_max_retries(cls):
        """Tests whether the unique slug implementation doesn't try to find a
        slug forever and gives up after a while."""

        title = "myuniquetitle"

        obj = cls.Model()
        obj.title.en = title
        obj.save()

        with cls.assertRaises(cls, IntegrityError):
            for _ in range(0, settings.LOCALIZED_FIELDS_MAX_RETRIES + 1):
                another_obj = cls.Model()
                another_obj.title.en = title
                another_obj.save()

    @classmethod
    def test_populate(cls):
        """Tests whether the populating feature works correctly."""

        obj = cls.Model()
        obj.title.en = "this is my title"
        obj.save()

        assert obj.slug.get("en") == slugify(obj.title)

    @classmethod
    def test_populate_callable(cls):
        """Tests whether the populating feature works correctly when you
        specify a callable."""

        def generate_slug(instance):
            return instance.title

        get_fake_model(
            {
                "title": LocalizedField(),
                "slug": LocalizedUniqueSlugField(populate_from=generate_slug),
            }
        )

        obj = cls.Model()
        for lang_code, lang_name in settings.LANGUAGES:
            obj.title.set(lang_code, "title %s" % lang_name)

        obj.save()

        for lang_code, lang_name in settings.LANGUAGES:
            assert obj.slug.get(lang_code) == "title-%s" % lang_name.lower()

    @staticmethod
    def test_populate_multiple_from_fields():
        """Tests whether populating the slug from multiple fields works
        correctly."""

        model = get_fake_model(
            {
                "title": LocalizedField(),
                "name": models.CharField(max_length=255),
                "slug": LocalizedUniqueSlugField(
                    populate_from=("title", "name")
                ),
            }
        )

        obj = model()
        for lang_code, lang_name in settings.LANGUAGES:
            obj.name = "swen"
            obj.title.set(lang_code, "title %s" % lang_name)

        obj.save()

        for lang_code, lang_name in settings.LANGUAGES:
            assert (
                obj.slug.get(lang_code) == "title-%s-swen" % lang_name.lower()
            )

    @staticmethod
    def test_populate_multiple_from_fields_fk():
        """Tests whether populating the slug from multiple fields works
        correctly."""

        model_fk = get_fake_model({"name": LocalizedField()})

        model = get_fake_model(
            {
                "title": LocalizedField(),
                "other": models.ForeignKey(model_fk, on_delete=models.CASCADE),
                "slug": LocalizedUniqueSlugField(
                    populate_from=("title", "other.name")
                ),
            }
        )

        other = model_fk.objects.create(name={settings.LANGUAGE_CODE: "swen"})

        obj = model()
        for lang_code, lang_name in settings.LANGUAGES:
            obj.other_id = other.id
            obj.title.set(lang_code, "title %s" % lang_name)

        obj.save()

        for lang_code, lang_name in settings.LANGUAGES:
            assert (
                obj.slug.get(lang_code) == "title-%s-swen" % lang_name.lower()
            )

    @classmethod
    def test_populate_multiple_languages(cls):
        """Tests whether the populating feature correctly works for all
        languages."""

        obj = cls.Model()
        for lang_code, lang_name in settings.LANGUAGES:
            obj.title.set(lang_code, "title %s" % lang_name)

        obj.save()

        for lang_code, lang_name in settings.LANGUAGES:
            assert obj.slug.get(lang_code) == "title-%s" % lang_name.lower()

    @classmethod
    def test_disable(cls):
        """Tests whether disabling auto-slugging works."""

        Model = get_fake_model(
            {
                "title": LocalizedField(),
                "slug": LocalizedUniqueSlugField(
                    populate_from="title", enabled=False
                ),
            }
        )

        obj = Model()
        obj.title = "test"

        # should raise IntegrityError because auto-slugging
        # is disabled and the slug field is NULL
        with pytest.raises(IntegrityError):
            obj.save()

    @classmethod
    def test_allows_override_when_immutable(cls):
        """Tests whether setting a value manually works and does not get
        overriden."""

        Model = get_fake_model(
            {
                "title": LocalizedField(),
                "name": models.CharField(max_length=255),
                "slug": LocalizedUniqueSlugField(
                    populate_from="title", immutable=True
                ),
            }
        )

        obj = Model()

        for lang_code, lang_name in settings.LANGUAGES:
            obj.slug.set(lang_code, "my value %s" % lang_code)
            obj.title.set(lang_code, "my title %s" % lang_code)

        obj.save()

        for lang_code, lang_name in settings.LANGUAGES:
            assert obj.slug.get(lang_code) == "my value %s" % lang_code

    @classmethod
    def test_unique_slug(cls):
        """Tests whether unique slugs are properly generated."""

        title = "myuniquetitle"

        obj = cls.Model()
        obj.title.en = title
        obj.save()

        for i in range(1, settings.LOCALIZED_FIELDS_MAX_RETRIES - 1):
            another_obj = cls.Model()
            another_obj.title.en = title
            another_obj.save()

            assert another_obj.slug.en == "%s-%d" % (title, i)

    @classmethod
    def test_unique_slug_utf(cls):
        """Tests whether generating a slug works when the value consists
        completely out of non-ASCII characters."""

        obj = cls.Model()
        obj.title.en = "مكاتب للايجار بشارع بورسعيد"
        obj.save()

        assert obj.slug.en == "مكاتب-للايجار-بشارع-بورسعيد"

    @staticmethod
    def test_deconstruct():
        """Tests whether the :see:deconstruct function properly retains options
        specified in the constructor."""

        field = LocalizedUniqueSlugField(
            enabled=False, immutable=True, populate_from="title"
        )
        _, _, _, kwargs = field.deconstruct()

        assert not kwargs["enabled"]
        assert kwargs["immutable"]
        assert kwargs["populate_from"] == field.populate_from

    @staticmethod
    def test_formfield():
        """Tests whether the :see:formfield method returns a valid form field
        that is hidden."""

        form_field = LocalizedUniqueSlugField(populate_from="title").formfield()

        assert isinstance(form_field, forms.CharField)
        assert isinstance(form_field.widget, forms.HiddenInput)
