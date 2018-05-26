from django.test import TestCase
from django.conf import settings
from localized_fields.fields import LocalizedField

from .data import get_init_integer_values

class LocalizedIntegerFieldTestCase(TestCase):

    @staticmethod
    def test_from_db_value():
        """Tests whether the :see:from_db_value function
        produces the expected :see:LocalizedValue."""

        input_data = get_init_integer_values()
        localized_value = LocalizedField().from_db_value(input_data)

        for lang_code, _ in settings.LANGUAGES:
            assert getattr(localized_value, lang_code) == input_data[lang_code]
            assert isinstance((getattr(localized_value, lang_code)), int) is True
