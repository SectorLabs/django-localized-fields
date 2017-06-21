import os
import shutil
import tempfile as sys_tempfile
import pickle

from django import forms
from django.test import TestCase, override_settings
from django.core.files.base import File, ContentFile
from django.core.files import temp as tempfile
from localized_fields.fields import LocalizedFileField
from localized_fields.value import LocalizedValue
from localized_fields.fields.file_field import LocalizedFieldFile
from localized_fields.forms import LocalizedFileFieldForm
from localized_fields.value import LocalizedFileValue
from localized_fields.widgets import LocalizedFileWidget
from .fake_model import get_fake_model


MEDIA_ROOT = sys_tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class LocalizedFileFieldTestCase(TestCase):
    """Tests the localized slug classes."""

    @classmethod
    def setUpClass(cls):
        """Creates the test models in the database."""

        super().setUpClass()

        cls.FileFieldModel = get_fake_model(
            'LocalizedFileFieldTestModel',
            {
                'file': LocalizedFileField(),
            }
        )
        if not os.path.isdir(MEDIA_ROOT):
            os.makedirs(MEDIA_ROOT)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT)

    @classmethod
    def test_assign(cls):
        """Tests whether the :see:LocalizedFileValueDescriptor works properly"""

        temp_file = tempfile.NamedTemporaryFile(dir=MEDIA_ROOT)
        instance = cls.FileFieldModel()
        instance.file = {'en': temp_file.name}
        assert isinstance(instance.file.en, LocalizedFieldFile)
        assert instance.file.en.name == temp_file.name

        field_dump = pickle.dumps(instance.file)
        instance = cls.FileFieldModel()
        instance.file = pickle.loads(field_dump)
        assert instance.file.en.field == instance._meta.get_field('file')
        assert instance.file.en.instance == instance
        assert isinstance(instance.file.en, LocalizedFieldFile)

        instance = cls.FileFieldModel()
        instance.file = {'en': ContentFile("test", "testfilename")}
        assert isinstance(instance.file.en, LocalizedFieldFile)
        assert instance.file.en.name == "testfilename"

        another_instance = cls.FileFieldModel()
        another_instance.file = {'ro': instance.file.en}
        assert another_instance == another_instance.file.ro.instance
        assert another_instance.file.ro.lang == 'ro'

    @classmethod
    def test_save_form_data(cls):
        """Tests whether the :see:save_form_data function correctly set 
        a valid value."""

        instance = cls.FileFieldModel()
        data = LocalizedFileValue({'en': False})
        instance._meta.get_field('file').save_form_data(instance, data)
        assert instance.file.en == ''

    @classmethod
    def test_pre_save(cls):
        """Tests whether the :see:pre_save function works properly."""

        instance = cls.FileFieldModel()
        instance.file = {'en': ContentFile("test", "testfilename")}
        instance._meta.get_field('file').pre_save(instance, False)
        assert instance.file.en._committed == True

    @classmethod
    def test_file_methods(cls):
        """Tests whether the :see:LocalizedFieldFile.delete method works
        correctly."""

        temp_file = File(tempfile.NamedTemporaryFile())
        instance = cls.FileFieldModel()
        # Calling delete on an unset FileField should not call the file deletion
        # process, but fail silently
        instance.file.en.delete()
        instance.file.en.save('testfilename', temp_file)
        assert instance.file.en.name == 'testfilename'
        instance.file.en.delete()
        assert instance.file.en.name is None

    @classmethod
    def test_generate_filename(cls):
        """Tests whether the :see:LocalizedFieldFile.generate_filename method
        works correctly."""

        instance = cls.FileFieldModel()
        field = instance._meta.get_field('file')
        field.upload_to = '{lang}/'
        filename = field.generate_filename(instance, 'test', 'en')
        assert filename == 'en/test'
        field.upload_to = lambda instance, filename, lang: \
            '%s_%s' % (lang, filename)
        filename = field.generate_filename(instance, 'test', 'en')
        assert filename == 'en_test'

    @staticmethod
    def test_get_prep_value():
        """Tests whether the :see:get_prep_value function returns correctly 
        value."""

        value = LocalizedValue({'en': None})
        assert LocalizedFileField().get_prep_value(None) == None
        assert isinstance(LocalizedFileField().get_prep_value(value), dict)
        assert LocalizedFileField().get_prep_value(value)['en'] == ''

    @staticmethod
    def test_formfield():
        """Tests whether the :see:formfield function correctly returns 
        a valid form."""

        form_field = LocalizedFileField().formfield()
        assert isinstance(form_field, LocalizedFileFieldForm)
        assert isinstance(form_field, forms.FileField)
        assert isinstance(form_field.widget, LocalizedFileWidget)

    @staticmethod
    def test_deconstruct():
        """Tests whether the :see:LocalizedFileField
        class's :see:deconstruct function works properly."""

        name, path, args, kwargs = LocalizedFileField().deconstruct()
        assert 'upload_to' in kwargs
        assert 'storage' not in kwargs
        name, path, \
        args, kwargs = LocalizedFileField(storage='test').deconstruct()
        assert 'storage' in kwargs
