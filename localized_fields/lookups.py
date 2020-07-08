from django.conf import settings
from django.contrib.postgres.fields.hstore import KeyTransform
from django.contrib.postgres.lookups import (
    SearchLookup,
    TrigramSimilar,
    Unaccent,
)
from django.db.models import TextField, Transform
from django.db.models.expressions import Col, Func, Value
from django.db.models.functions import Coalesce
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

from .fields import LocalizedField

try:
    from django.db.models.functions import NullIf
except ImportError:
    # for Django < 2.2
    class NullIf(Func):
        function = "NULLIF"
        arity = 2


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


@LocalizedField.register_lookup
class ActiveRefLookup(Transform):
    output_field = TextField()
    lookup_name = "active_ref"
    arity = None

    def as_sql(self, compiler, connection):
        language = translation.get_language() or settings.LANGUAGE_CODE
        return KeyTransform(language, self.lhs).as_sql(compiler, connection)


@LocalizedField.register_lookup
class TranslatedRefLookup(Transform):
    output_field = TextField()
    lookup_name = "translated_ref"
    arity = None

    def as_sql(self, compiler, connection):
        language = translation.get_language()
        fallback_config = getattr(settings, "LOCALIZED_FIELDS_FALLBACKS", {})
        target_languages = fallback_config.get(language, [])
        if not target_languages and language != settings.LANGUAGE_CODE:
            target_languages.append(settings.LANGUAGE_CODE)

        if language:
            target_languages.insert(0, language)

        if len(target_languages) > 1:
            return Coalesce(
                *[
                    NullIf(KeyTransform(language, self.lhs), Value(""))
                    for language in target_languages
                ]
            ).as_sql(compiler, connection)

        return KeyTransform(target_languages[0], self.lhs).as_sql(
            compiler, connection
        )
