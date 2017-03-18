from django.core.checks import Warning

class AtomicSlugRetryMixin:
    """A Mixin keeped for backwards compatibility"""

    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        errors.append(
            Warning(
                'localized_fields.AtomicSlugRetryMixin is deprecated',
                hint='There is no need to use '
                     'localized_fields.AtomicSlugRetryMixin',
                obj=cls
            )
        )
        return errors
