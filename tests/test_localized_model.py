from django.test import TestCase

from localized_fields import LocalizedValue

from .fake_model import get_fake_model


class LocalizedModelTestCase(TestCase):
    """Tests whether the :see:LocalizedModel class."""

    TestModel = None

    @classmethod
    def setUpClass(cls):
        """Creates the test model in the database."""

        super(LocalizedModelTestCase, cls).setUpClass()

        cls.TestModel = get_fake_model()

    @classmethod
    def test_defaults(cls):
        """Tests whether all :see:LocalizedField
        fields are assigned an empty :see:LocalizedValue
        instance when the model is instanitiated."""

        obj = cls.TestModel()

        assert isinstance(obj.title, LocalizedValue)
