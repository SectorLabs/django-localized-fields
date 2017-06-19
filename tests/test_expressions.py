from django.test import TestCase
from django.db import models
from django.utils import translation
from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg

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

        def create_queryset(ref):
            return (
                cls.TestModel1.objects
                .annotate(mytexts=ref)
                .values_list('mytexts', flat=True)
            )

        # assert that it properly selects the currently active language
        for lang_code, _ in settings.LANGUAGES:
            translation.activate(lang_code)
            queryset = create_queryset(LocalizedRef('features__text'))

            for index, value in enumerate(queryset):
                assert translation.get_language() in value
                assert str(index) in value

        # ensure that the default language is used in case no
        # language is active at all
        translation.deactivate_all()
        queryset = create_queryset(LocalizedRef('features__text'))
        for index, value in enumerate(queryset):
            assert settings.LANGUAGE_CODE in value
            assert str(index) in value

        # ensures that overriding the language works properly
        queryset = create_queryset(LocalizedRef('features__text', 'ro'))
        for index, value in enumerate(queryset):
            assert 'ro' in value
            assert str(index) in value

        # ensures that using this in combination with ArrayAgg works properly
        queryset = create_queryset(ArrayAgg(LocalizedRef('features__text', 'ro'))).first()
        assert isinstance(queryset, list)
        for value in queryset:
            assert 'ro' in value
