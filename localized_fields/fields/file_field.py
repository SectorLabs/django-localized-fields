import json
import datetime
import posixpath

from django.core.files import File
from django.db.models.fields.files import FieldFile
from django.utils import six
from django.core.files.storage import default_storage
from django.utils.encoding import force_str, force_text

from localized_fields.fields import LocalizedField
from localized_fields.fields.field import LocalizedValueDescriptor
from localized_fields.value import LocalizedValue

from ..value import LocalizedFileValue
from ..forms import LocalizedFileFieldForm


class LocalizedFieldFile(FieldFile):

    def __init__(self, instance, field, name, lang):
        super().__init__(instance, field, name)
        self.lang = lang

    def save(self, name, content, save=True):
        name = self.field.generate_filename(self.instance, name, self.lang)
        self.name = self.storage.save(name, content,
                                      max_length=self.field.max_length)
        self._committed = True

        if save:
            self.instance.save()

    save.alters_data = True

    def delete(self, save=True):
        if not self:
            return

        if hasattr(self, '_file'):
            self.close()
            del self.file

        self.storage.delete(self.name)

        self.name = None
        self._committed = False

        if save:
            self.instance.save()

    delete.alters_data = True


class LocalizedFileValueDescriptor(LocalizedValueDescriptor):
    def __get__(self, instance, cls=None):
        value = super().__get__(instance, cls)
        for lang, file in value.__dict__.items():
            if isinstance(file, six.string_types) or file is None:
                file = self.field.value_class(instance, self.field, file, lang)
                value.set(lang, file)

            elif isinstance(file, File) and \
                    not isinstance(file, LocalizedFieldFile):
                file_copy = self.field.value_class(instance, self.field,
                                                   file.name, lang)
                file_copy.file = file
                file_copy._committed = False
                value.set(lang, file_copy)

            elif isinstance(file, LocalizedFieldFile) and \
                    not hasattr(file, 'field'):
                file.instance = instance
                file.field = self.field
                file.storage = self.field.storage
                file.lang = lang

            # Make sure that the instance is correct.
            elif isinstance(file, LocalizedFieldFile) \
                    and instance is not file.instance:
                file.instance = instance
                file.lang = lang
        return value


class LocalizedFileField(LocalizedField):
    descriptor_class = LocalizedFileValueDescriptor
    attr_class = LocalizedFileValue
    value_class = LocalizedFieldFile

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None,
                 **kwargs):

        self.storage = storage or default_storage
        self.upload_to = upload_to

        super().__init__(verbose_name, name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['upload_to'] = self.upload_to
        if self.storage is not default_storage:
            kwargs['storage'] = self.storage
        return name, path, args, kwargs

    def get_prep_value(self, value):
        """Returns field's value prepared for saving into a database."""

        if isinstance(value, LocalizedValue):
            prep_value = LocalizedValue()
            for k, v in value.__dict__.items():
                if v is None:
                    prep_value.set(k, '')
                else:
                    # Need to convert File objects provided via a form to
                    # unicode for database insertion
                    prep_value.set(k, six.text_type(v))
            return super().get_prep_value(prep_value)
        return super().get_prep_value(value)

    def pre_save(self, model_instance, add):
        """Returns field's value just before saving."""
        value = super().pre_save(model_instance, add)
        if isinstance(value, LocalizedValue):
            for file in value.__dict__.values():
                if file and not file._committed:
                    file.save(file.name, file, save=False)
        return value

    def generate_filename(self, instance, filename, lang):
        if callable(self.upload_to):
            filename = self.upload_to(instance, filename, lang)
        else:
            now = datetime.datetime.now()
            dirname = force_text(now.strftime(force_str(self.upload_to)))
            dirname = dirname.format(lang=lang)
            filename = posixpath.join(dirname, filename)
        return self.storage.generate_filename(filename)

    def save_form_data(self, instance, data):
        if isinstance(data, LocalizedValue):
            for k, v in data.__dict__.items():
                if v is not None and not v:
                    data.set(k, '')
            setattr(instance, self.name, data)

    def formfield(self, **kwargs):
        defaults = {'form_class': LocalizedFileFieldForm}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        if isinstance(value, LocalizedFileValue):
            return json.dumps({k: v.name for k, v
                               in value.__dict__.items()})
        else:
            return super().value_to_string(obj)
