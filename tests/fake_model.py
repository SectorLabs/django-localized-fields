from django.contrib.postgres.operations import HStoreExtension
from django.db import connection, migrations
from django.db.migrations.executor import MigrationExecutor

from localized_fields import (LocalizedAutoSlugField, LocalizedField,
                              LocalizedModel)

MODEL = None


def get_fake_model():
    """Creates a fake model to use during unit tests."""

    global MODEL

    if MODEL:
        return MODEL

    class TestModel(LocalizedModel):
        """Model used for testing the :see:LocalizedAutoSlugField."""

        app_label = 'localized_fields'

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

    MODEL = TestModel
    return MODEL
