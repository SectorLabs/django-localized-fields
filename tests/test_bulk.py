from django.db import models
from django.test import TestCase

from localized_fields.fields import LocalizedField, LocalizedUniqueSlugField

from .fake_model import get_fake_model


class LocalizedBulkTestCase(TestCase):
    """Tests bulk operations with data structures provided by the django-
    localized-fields library."""

    @staticmethod
    def test_localized_bulk_insert():
        """Tests whether bulk inserts work properly when using a
        :see:LocalizedUniqueSlugField in the model."""

        model = get_fake_model(
            {
                "name": LocalizedField(),
                "slug": LocalizedUniqueSlugField(
                    populate_from="name", include_time=True
                ),
                "score": models.IntegerField(),
            }
        )

        to_create = [
            model(
                name={"en": "english name 1", "ro": "romanian name 1"}, score=1
            ),
            model(
                name={"en": "english name 2", "ro": "romanian name 2"}, score=2
            ),
            model(
                name={"en": "english name 3", "ro": "romanian name 3"}, score=3
            ),
        ]

        model.objects.bulk_create(to_create)
        assert model.objects.all().count() == 3

        for obj in to_create:
            obj_db = model.objects.filter(
                name__en=obj.name.en, name__ro=obj.name.ro, score=obj.score
            ).first()

            assert obj_db
            assert len(obj_db.slug.en) >= len(obj_db.name.en)
            assert len(obj_db.slug.ro) >= len(obj_db.name.ro)
