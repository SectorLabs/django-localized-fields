import json

from django.conf import settings
from django.db import models
from django.db.utils import IntegrityError
from django.test import TestCase

from localized_fields.fields import LocalizedField
from localized_fields.forms import LocalizedFieldForm
from localized_fields.value import LocalizedValue

from .data import get_init_values
from .fake_model import get_fake_model


class LocalizedFieldTestCase(TestCase):
    """Tests the :see:LocalizedField class."""

    @staticmethod
    def test_init():
        """Tests whether the :see:__init__ function
        correctly handles parameters"""

        field = LocalizedField(blank=True)
        assert field.required == []

        field = LocalizedField(blank=False)
        assert field.required == [settings.LANGUAGE_CODE]

        field = LocalizedField(required=True)
        assert field.required == [lang_code for lang_code, _ in
                                  settings.LANGUAGES]

        field = LocalizedField(required=False)
        assert field.required == []

    @staticmethod
    def test_from_db_value():
        """Tests whether the :see:from_db_value function
        produces the expected :see:LocalizedValue."""

        input_data = get_init_values()
        localized_value = LocalizedField().from_db_value(input_data)

        for lang_code, _ in settings.LANGUAGES:
            assert getattr(localized_value, lang_code) == input_data[lang_code]

    @staticmethod
    def test_from_db_value_none():
        """Tests whether the :see:from_db_value function
        correctly handles None values."""

        localized_value = LocalizedField().from_db_value(None)

        for lang_code, _ in settings.LANGUAGES:
            assert localized_value.get(lang_code) is None

    def test_from_db_value_none_return_none(self):
        """Tests whether the :see:from_db_value function
        correctly handles None values when LOCALIZED_FIELDS_EXPERIMENTAL
        is set to True."""

        with self.settings(LOCALIZED_FIELDS_EXPERIMENTAL=True):
            localized_value = LocalizedField.from_db_value(None)

        assert localized_value is None

    @staticmethod
    def test_to_python():
        """Tests whether the :see:to_python function
        produces the expected :see:LocalizedValue."""

        input_data = get_init_values()
        localized_value = LocalizedField().to_python(input_data)

        for language, value in input_data.items():
            assert localized_value.get(language) == value

    @staticmethod
    def test_to_python_non_json():
        """Tests whether the :see:to_python function
        properly handles a string that is not JSON."""

        localized_value = LocalizedField().to_python('my value')
        assert localized_value.get() == 'my value'

    @staticmethod
    def test_to_python_none():
        """Tests whether the :see:to_python function
        produces the expected :see:LocalizedValue
        instance when it is passes None."""

        localized_value = LocalizedField().to_python(None)
        assert localized_value

        for lang_code, _ in settings.LANGUAGES:
            assert localized_value.get(lang_code) is None

    @staticmethod
    def test_to_python_non_dict():
        """Tests whether the :see:to_python function produces
        the expected :see:LocalizedValue when it is
        passed a non-dictionary value."""

        localized_value = LocalizedField().to_python(list())
        assert localized_value

        for lang_code, _ in settings.LANGUAGES:
            assert localized_value.get(lang_code) is None

    @staticmethod
    def test_to_python_str():
        """Tests whether the :see:to_python function produces
        the expected :see:LocalizedValue when it is
        passed serialized string value."""

        serialized_str = json.dumps(get_init_values())
        localized_value = LocalizedField().to_python(serialized_str)
        assert isinstance(localized_value, LocalizedValue)

        for language, value in get_init_values().items():
            assert localized_value.get(language) == value
            assert getattr(localized_value, language) == value

    @staticmethod
    def test_get_prep_value():
        """"Tests whether the :see:get_prep_value function
        produces the expected dictionary."""

        input_data = get_init_values()
        localized_value = LocalizedValue(input_data)

        output_data = LocalizedField().get_prep_value(localized_value)

        for language, value in input_data.items():
            assert language in output_data
            assert output_data.get(language) == value

    @staticmethod
    def test_get_prep_value_none():
        """Tests whether the :see:get_prep_value function
        produces the expected output when it is passed None."""

        output_data = LocalizedField().get_prep_value(None)
        assert not output_data

    @staticmethod
    def test_get_prep_value_no_localized_value():
        """Tests whether the :see:get_prep_value function
        produces the expected output when it is passed a
        non-LocalizedValue value."""

        output_data = LocalizedField().get_prep_value(['huh'])
        assert not output_data

    def test_get_prep_value_clean(self):
        """Tests whether the :see:get_prep_value produces
        None as the output when it is passed an empty, but
        valid LocalizedValue value but, only when null=True."""

        localized_value = LocalizedValue()

        with self.assertRaises(IntegrityError):
            LocalizedField(null=False).get_prep_value(localized_value)

        assert not LocalizedField(null=True).get_prep_value(localized_value)
        assert not LocalizedField().clean(None)
        assert not LocalizedField().clean(['huh'])

    @staticmethod
    def test_formfield():
        """Tests whether the :see:formfield function
        correctly returns a valid form."""

        assert isinstance(
            LocalizedField().formfield(),
            LocalizedFieldForm
        )

        # case optional filling
        field = LocalizedField(blank=True, required=[])
        assert not field.formfield().required
        for field in field.formfield().fields:
            assert not field.required

        # case required for any language
        field = LocalizedField(blank=False, required=[])
        assert field.formfield().required
        for field in field.formfield().fields:
            assert not field.required

        # case required for specific languages
        required_langs = ['ro', 'nl']
        field = LocalizedField(blank=False, required=required_langs)
        assert field.formfield().required
        for field in field.formfield().fields:
            if field.label in required_langs:
                assert field.required
            else:
                assert not field.required

        # case required for all languages
        field = LocalizedField(blank=False, required=True)
        assert field.formfield().required
        for field in field.formfield().fields:
            assert field.required

    def test_descriptor_user_defined_primary_key(self):
        """Tests that descriptor works even when primary key is user defined."""
        model = get_fake_model(dict(
            slug=models.SlugField(primary_key=True),
            title=LocalizedField()
        ))

        obj = model.objects.create(slug='test', title='test')
        assert obj.title == 'test'

    def test_required_all(self):
        """Tests whether passing required=True properly validates
        that all languages are filled in."""

        model = get_fake_model(dict(
            title=LocalizedField(required=True)
        ))

        with self.assertRaises(IntegrityError):
            model.objects.create(title=dict(ro='romanian', nl='dutch'))

        with self.assertRaises(IntegrityError):
            model.objects.create(title=dict(nl='dutch'))

        with self.assertRaises(IntegrityError):
            model.objects.create(title=dict(random='random'))

        with self.assertRaises(IntegrityError):
            model.objects.create(title=dict())

        with self.assertRaises(IntegrityError):
            model.objects.create(title=None)

        with self.assertRaises(IntegrityError):
            model.objects.create(title='')

        with self.assertRaises(IntegrityError):
            model.objects.create(title='         ')

    def test_required_some(self):
        """Tests whether passing an array to required,
        properly validates whether the specified languages
        are marked as required."""

        model = get_fake_model(dict(
            title=LocalizedField(required=['nl', 'ro'])
        ))

        with self.assertRaises(IntegrityError):
            model.objects.create(title=dict(ro='romanian', nl='dutch'))

        with self.assertRaises(IntegrityError):
            model.objects.create(title=dict(nl='dutch'))

        with self.assertRaises(IntegrityError):
            model.objects.create(title=dict(random='random'))

        with self.assertRaises(IntegrityError):
            model.objects.create(title=dict())

        with self.assertRaises(IntegrityError):
            model.objects.create(title=None)

        with self.assertRaises(IntegrityError):
            model.objects.create(title='')

        with self.assertRaises(IntegrityError):
            model.objects.create(title='         ')
