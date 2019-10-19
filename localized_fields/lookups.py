from django.conf import settings
from django.contrib.postgres.fields.hstore import KeyTransform
from django.contrib.postgres.lookups import (
    SearchLookup,
    TrigramSimilar,
    Unaccent,
)
from django.db.models.expressions import Col
from django.db.models.lookups import (
    Contains,
    EndsWith,
    Exact,
    IContains,
    IEndsWith,
    IExact,
    In,
    IRegex,
    IsNull,
    IStartsWith,
    Regex,
    StartsWith,
)
from django.utils import translation


class LocalizedLookupMixin:
    def process_lhs(self, qn, connection):
        if isinstance(self.lhs, Col):
            language = translation.get_language() or settings.LANGUAGE_CODE
            self.lhs = KeyTransform(language, self.lhs)
        return super().process_lhs(qn, connection)

    def get_prep_lookup(self):
        return str(self.rhs)


class LocalizedSearchLookup(LocalizedLookupMixin, SearchLookup):
    pass


class LocalizedUnaccent(LocalizedLookupMixin, Unaccent):
    pass


class LocalizedTrigramSimilair(LocalizedLookupMixin, TrigramSimilar):
    pass


class LocalizedExact(LocalizedLookupMixin, Exact):
    pass


class LocalizedIExact(LocalizedLookupMixin, IExact):
    pass


class LocalizedIn(LocalizedLookupMixin, In):
    pass


class LocalizedContains(LocalizedLookupMixin, Contains):
    pass


class LocalizedIContains(LocalizedLookupMixin, IContains):
    pass


class LocalizedStartsWith(LocalizedLookupMixin, StartsWith):
    pass


class LocalizedIStartsWith(LocalizedLookupMixin, IStartsWith):
    pass


class LocalizedEndsWith(LocalizedLookupMixin, EndsWith):
    pass


class LocalizedIEndsWith(LocalizedLookupMixin, IEndsWith):
    pass


class LocalizedIsNullWith(LocalizedLookupMixin, IsNull):
    pass


class LocalizedRegexWith(LocalizedLookupMixin, Regex):
    pass


class LocalizedIRegexWith(LocalizedLookupMixin, IRegex):
    pass
