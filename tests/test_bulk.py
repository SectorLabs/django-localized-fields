import json

from django.db import models
from django.conf import settings
from django.test import TestCase

from localized_fields.fields import LocalizedField

from .data import get_init_values
from .fake_model import get_fake_model


class LocalizedBulkTestCase(TestCase):
    """Tests bulk operations with data structures provided
    by the django-localized-fields library."""

    @staticmethod
    def test_localized_bulk_insert():
        model = get_fake_model(
            'BulkInsertModel',
            {
                'name': LocalizedField(),
                'score': models.IntegerField()
            }
        )

        objects = model.objects.bulk_create([
            model(name={'en': 'english name 1', 'ro': 'romanian name 1'}, score=1),
            model(name={'en': 'english name 2', 'ro': 'romanian name 2'}, score=2),
            model(name={'en': 'english name 3', 'ro': 'romanian name 3'}, score=3)
        ])

        assert model.objects.all().count() == 3
