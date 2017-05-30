from django.conf import settings
from django.utils import translation

from psqlextra import expressions


class LocalizedRef(expressions.HStoreRef):
    """Expression that selects the value in a field only in
    the currently active language."""

    def __init__(self, name: str, lang: str=None):
        """Initializes a new instance of :see:LocalizedRef.

        Arguments:
            name:
                The field/column to select from.

            lang:
                The language to get the field/column in.
                If not specified, the currently active language
                is used.
        """

        language = lang or translation.get_language() or settings.LANGUAGE_CODE
        super().__init__(name, language)
