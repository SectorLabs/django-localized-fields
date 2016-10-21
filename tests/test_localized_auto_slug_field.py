from django.conf import settings
from django.contrib.postgres.operations import HStoreExtension
from django.db import connection, migrations, models
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase
from django.utils.text import slugify

from localized_fields.fields import (LocalizedAutoSlugField, LocalizedField,
                                     LocalizedValue)


class LocalizedAutoSlugFieldTestCase(TestCase):
    """Tests the :see:LocalizedAutoSlugField class."""

    TestModel = None

    @classmethod
    def setUpClass(cls):
        """Creates the test model in the database."""

        super(LocalizedAutoSlugFieldTestCase, cls).setUpClass()

        class TestModel(models.Model):
            """Model used for testing the :see:LocalizedAutoSlugField."""

            app_label = 'localized_fields'

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.title = self.title or LocalizedValue()
                self.slug = self.slug or LocalizedValue()

            title = LocalizedField()
            slug = LocalizedAutoSlugField(populate_from='title')

        class TestProject:

            def clone(self, *args, **kwargs):
                return self

        class TestMigration(migrations.Migration):
            operations = [
                HStoreExtension()
            ]

        with connection.schema_editor() as schema_editor:
            migration_executor = MigrationExecutor(schema_editor.connection)
            migration_executor.apply_migration(
                TestProject(),
                TestMigration('eh', 'localized_fields')
            )
            schema_editor.create_model(TestModel)

        cls.TestModel = TestModel

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
