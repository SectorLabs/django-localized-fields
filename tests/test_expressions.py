from django.test import TestCase
from django.db import models
from django.utils import translation
from django.conf import settings

from localized_fields.fields import LocalizedField
from localized_fields.value import LocalizedValue
from localized_fields.expressions import LocalizedRef

from .fake_model import get_fake_model


class LocalizedExpressionsTestCase(TestCase):
    """Tests whether expressions properly work with :see:LocalizedField."""

    TestModel1 = None
    TestModel2 = None

    @classmethod
    def setUpClass(cls):
        """Creates the test model in the database."""

        super(LocalizedExpressionsTestCase, cls).setUpClass()

        cls.TestModel1 = get_fake_model(
            'LocalizedExpressionsTestCase2',
            {
                'name': models.CharField(null=False, blank=False, max_length=255),
            }
        )

        cls.TestModel2 = get_fake_model(
            'LocalizedExpressionsTestCase1',
            {
                'text': LocalizedField(),
                'other': models.ForeignKey(cls.TestModel1, related_name='features')
            }
        )

    @classmethod
    def test_localized_ref(cls):
        """Tests whether the :see:LocalizedRef expression properly works."""

        obj = cls.TestModel1.objects.create(name='bla bla')
        for i in range(0, 10):
            cls.TestModel2.objects.create(
                text=LocalizedValue(dict(en='text_%d_en' % i, ro='text_%d_ro' % i, nl='text_%d_nl' % i)),
                other=obj
            )

        for lang_code, _ in settings.LANGUAGES:
            translation.activate(lang_code)

            queryset = (
                cls.TestModel1.objects
                .annotate(
                    mytexts=LocalizedRef('features__text')
                )
                .values_list(
                    'mytexts', flat=True
                )
            )

            for index, value in enumerate(queryset):
                assert str(index) in value
