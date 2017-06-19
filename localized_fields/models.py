from psqlextra.models import PostgresModel

from .mixins import AtomicSlugRetryMixin


class LocalizedModel(AtomicSlugRetryMixin, PostgresModel):
    """Turns a model into a model that contains LocalizedField's.

    For basic localisation functionality, it isn't needed to inherit
    from LocalizedModel. However, for certain features, this is required.

    It is definitely needed for :see:LocalizedUniqueSlugField, unless you
    manually inherit from AtomicSlugRetryMixin."""

    class Meta:
        abstract = True
