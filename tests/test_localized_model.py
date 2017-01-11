from django.test import TestCase
from django.utils import translation

from localized_fields.fields import LocalizedValue

from .fake_model import get_fake_model
from .test_localized_field import get_init_values


class LocalizedModelTestCase(TestCase):
    """Tests whether the :see:LocalizedValueDescriptor class."""

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

    @classmethod
    def test_set(cls):
        """Tests whether the :see:LocalizedValueDescriptor
        class's see:set function works properly."""

        obj = cls.TestModel()

        for language, value in get_init_values():
            translation.activate(language)
            obj.title = value
            assert obj.title.get(language) == value
            assert getattr(obj.title, language) == value
