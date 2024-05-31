import django
import pytest

from django.test import TestCase

from localized_fields.fields import LocalizedField
from localized_fields.value import LocalizedValue

from .fake_model import get_fake_model


class LocalizedIsNullLookupsTestCase(TestCase):
    """Tests whether ref lookups properly work with."""

    TestModel1 = None

    @classmethod
    def setUpClass(cls):
        """Creates the test model in the database."""
        super(LocalizedIsNullLookupsTestCase, cls).setUpClass()
        cls.TestModel = get_fake_model(
            {"text": LocalizedField(null=True, required=[])}
        )
        cls.TestModel.objects.create(
            text=LocalizedValue(dict(en="text_en", ro="text_ro", nl="text_nl"))
        )
        cls.TestModel.objects.create(
            text=None,
        )

    def test_isnull_lookup_valid_values(self):
        """Test whether isnull properly works with valid values."""
        assert self.TestModel.objects.filter(text__isnull=True).exists()
        assert self.TestModel.objects.filter(text__isnull=False).exists()

    def test_isnull_lookup_null(self):
        """Test whether isnull crashes with None as value."""

        with pytest.raises(ValueError):
            assert self.TestModel.objects.filter(text__isnull=None).exists()

    def test_isnull_lookup_string(self):
        """Test whether isnull properly works with string values on the
        corresponding Django version."""
        if django.VERSION < (4, 0):
            assert self.TestModel.objects.filter(text__isnull="True").exists()
        else:
            with pytest.raises(ValueError):
                assert self.TestModel.objects.filter(
                    text__isnull="True"
                ).exists()
