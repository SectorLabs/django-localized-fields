from django.conf import settings
from django.utils import six, translation


class LocalizedValueDescriptor:
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
        """Initializes a new instance of :see:LocalizedValueDescriptor."""

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
            language = translation.get_language() or settings.LANGUAGE_CODE
            self.__get__(instance).set(language, value)  # pylint: disable=no-member
        else:
            instance.__dict__[self.field.name] = value
