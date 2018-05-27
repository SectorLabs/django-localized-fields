from django.test import TestCase
from django.conf import settings
from localized_fields.fields import LocalizedIntegerField

from .data import get_init_integer_values
from .fake_model import get_fake_model

class LocalizedIntegerFieldTestCase(TestCase):

    @staticmethod
    def test_from_db_value():
        """Tests whether the :see:from_db_value function
        produces the expected :see:LocalizedValue."""

        input_data = get_init_integer_values()
        localized_value = LocalizedIntegerField().from_db_value(input_data)

        for lang_code, _ in settings.LANGUAGES:
            assert getattr(localized_value, lang_code) == input_data[lang_code]
            assert isinstance((getattr(localized_value, lang_code)), int) is True
            assert localized_value.get(lang_code) == input_data[lang_code]
            assert isinstance(localized_value.get(lang_code), int) is True

    @staticmethod
    def test_default_value():
        """Tests whether default language value is returned correctly"""

        input_data = get_init_integer_values()
        Model = get_fake_model(dict(
            score=LocalizedIntegerField(required=True)
        ))

        inst = Model()
        inst.score = dict(en=0, ro=1, nl = 2)
        inst.score = LocalizedIntegerField
        inst.save()

        inst = Model.objects.get(pk=inst.pk)
        
        settings.LANGUAGE_CODE = 'ro'
        assert int(inst.score) == input_data['ro']
        settings.LANGUAGE_CODE = 'en'
