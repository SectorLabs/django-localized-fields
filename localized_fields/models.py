from django.db import models
from django.core.checks import Warning


class LocalizedModel(models.Model):
    """A model keeped for backwards compatibility"""

    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        errors.append(
            Warning(
                'localized_fields.LocalizedModel is deprecated',
                hint='There is no need to use localized_fields.LocalizedModel',
                obj=cls
            )
        )
        return errors

    class Meta:
        abstract = True
