from django.conf import settings
from django.db.utils import IntegrityError
from django.utils import six, translation

from psqlextra.fields import HStoreField

from ..forms import LocalizedFieldForm
from ..localized_value import LocalizedValue


class LocalizedValueDescriptor(object):
    """
    The descriptor for the localized value attribute on the model instance.
    Returns a :see:LocalizedValue when accessed so you can do stuff like::

        >>> from myapp.models import MyModel
        >>> instance = MyModel()
        >>> instance.value.en = 'English value'

    Assigns a strings to active language key in :see:LocalizedValue on
    assignment so you can do::

        >>> from django.utils import translation
        >>> from myapp.models import MyModel

        >>> translation.activate('nl')
        >>> instance = MyModel()
        >>> instance.title = 'dutch title'
        >>> print(instance.title.nl) # prints 'dutch title'
    """
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        # This is slightly complicated, so worth an explanation.
        # `instance.localizedvalue` needs to ultimately return some instance of
        # `LocalizedValue`, probably a subclass.

        # The instance dict contains whatever was originally assigned
        # in __set__.
        if self.field.name in instance.__dict__:
            value = instance.__dict__[self.field.name]
        elif instance.pk is not None:
            instance.refresh_from_db(fields=[self.field.name])
            value = getattr(instance, self.field.name)
        else:
            value = None

        if value is None:
            attr = self.field.attr_class()
            instance.__dict__[self.field.name] = attr

        if isinstance(value, dict):
            attr = self.field.attr_class(value)
            instance.__dict__[self.field.name] = attr

        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        if isinstance(value, six.string_types):
            self.__get__(instance).set(translation.get_language() or
                                       settings.LANGUAGE_CODE, value)
        else:
            instance.__dict__[self.field.name] = value


class LocalizedField(HStoreField):
    """A field that has the same value in multiple languages.

    Internally this is stored as a :see:HStoreField where there
    is a key for every language."""

    Meta = None

    # The class to wrap instance attributes in. Accessing to field attribute in
    # model instance will always return an instance of attr_class.
    attr_class = LocalizedValue

    # The descriptor to use for accessing the attribute off of the class.
    descriptor_class = LocalizedValueDescriptor

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of :see:LocalizedField."""

        super(LocalizedField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        super(LocalizedField, self).contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, self.descriptor_class(self))

    @classmethod
    def from_db_value(cls, value, *_):
        """Turns the specified database value into its Python
        equivalent.

        Arguments:
            value:
                The value that is stored in the database and
                needs to be converted to its Python equivalent.

        Returns:
            A :see:LocalizedValue instance containing the
            data extracted from the database.
        """

        if not value:
            if getattr(settings, 'LOCALIZED_FIELDS_EXPERIMENTAL', False):
                return None
            else:
                return cls.attr_class()

        return cls.attr_class(value)

    def to_python(self, value: dict) -> LocalizedValue:
        """Turns the specified database value into its Python
        equivalent.

        Arguments:
            value:
                The value that is stored in the database and
                needs to be converted to its Python equivalent.

        Returns:
            A :see:LocalizedValue instance containing the
            data extracted from the database.
        """

        if not value or not isinstance(value, dict):
            return self.attr_class()

        return self.attr_class(value)

    def get_prep_value(self, value: LocalizedValue) -> dict:
        """Turns the specified value into something the database
        can store.

        If an illegal value (non-LocalizedValue instance) is
        specified, we'll treat it as an empty :see:LocalizedValue
        instance, on which the validation will fail.

        Arguments:
            value:
                The :see:LocalizedValue instance to serialize
                into a data type that the database can understand.

        Returns:
            A dictionary containing a key for every language,
            extracted from the specified value.
        """

        # default to None if this is an unknown type
        if not isinstance(value, LocalizedValue) and value:
            value = None

        if value:
            cleaned_value = self.clean(value)
            self.validate(cleaned_value)
        else:
            cleaned_value = value

        return super(LocalizedField, self).get_prep_value(
            cleaned_value.__dict__ if cleaned_value else None
        )

    def clean(self, value, *_):
        """Cleans the specified value into something we
        can store in the database.

        For example, when all the language fields are
        left empty, and the field is allows to be null,
        we will store None instead of empty keys.

        Arguments:
            value:
                The value to clean.

        Returns:
            The cleaned value, ready for database storage.
        """

        if not value or not isinstance(value, LocalizedValue):
            return None

        # are any of the language fiels None/empty?
        is_all_null = True
        for lang_code, _ in settings.LANGUAGES:
            # NOTE(seroy): use check for None, instead of
            # `bool(value.get(lang_code))==True` condition, cause in this way
            # we can not save '' value
            if value.get(lang_code) is not None:
                is_all_null = False
                break

        # all fields have been left empty and we support
        # null values, let's return null to represent that
        if is_all_null and self.null:
            return None

        return value

    def validate(self, value: LocalizedValue, *_):
        """Validates that the value for the primary language
        has been filled in.

        Exceptions are raises in order to notify the user
        of invalid values.

        Arguments:
            value:
                The value to validate.
        """

        if self.null:
            return

        primary_lang_val = getattr(value, settings.LANGUAGE_CODE)

        # NOTE(seroy): use check for None, instead of `not primary_lang_val`
        # condition, cause in this way we can not save '' value
        if primary_lang_val is None:
            raise IntegrityError(
                'null value in column "%s.%s" violates not-null constraint' % (
                    self.name,
                    settings.LANGUAGE_CODE
                )
            )

    def formfield(self, **kwargs):
        """Gets the form field associated with this field."""

        defaults = {
            'form_class': LocalizedFieldForm
        }

        defaults.update(kwargs)
        return super().formfield(**defaults)

    def deconstruct(self):
        """Gets the values to pass to :see:__init__ when
        re-creating this object."""

        name, path, args, kwargs = super(
            LocalizedField, self).deconstruct()

        if self.uniqueness:
            kwargs['uniqueness'] = self.uniqueness

        return name, path, args, kwargs
