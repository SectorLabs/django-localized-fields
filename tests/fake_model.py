from django.db import connection, migrations
from localized_fields import LocalizedModel
from django.db.migrations.executor import MigrationExecutor
from django.contrib.postgres.operations import HStoreExtension


def get_fake_model(name='TestModel', fields={}):
    """Creates a fake model to use during unit tests."""

    attributes = {
        'app_label': 'localized_fields',
        '__module__': __name__,
        '__name__': name
    }

    attributes.update(fields)
    TestModel = type(name, (LocalizedModel,), attributes)

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

    return TestModel
