from django.conf import settings
from django.db import connection
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import translation

from localized_fields.fields import LocalizedBooleanField
from localized_fields.value import LocalizedBooleanValue

from .fake_model import get_fake_model


class LocalizedBooleanFieldTestCase(TestCase):
    """Tests whether the :see:LocalizedBooleanField and
    :see:LocalizedIntegerValue works properly."""

    TestModel = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.TestModel = get_fake_model({"translated": LocalizedBooleanField()})

    def test_basic(self):
        """Tests the basics of storing boolean values."""

        obj = self.TestModel()
        for lang_code, _ in settings.LANGUAGES:
            obj.translated.set(lang_code, False)
        obj.save()

        obj = self.TestModel.objects.all().first()
        for lang_code, _ in settings.LANGUAGES:
            assert obj.translated.get(lang_code) is False

    def test_primary_language_required(self):
        """Tests whether the primary language is required by default and all
        other languages are optional."""

        # not filling in anything should raise IntegrityError,
        # the primary language is required
        with self.assertRaises(IntegrityError):
            obj = self.TestModel()
            obj.save()

        # when filling all other languages besides the primary language
        # should still raise an error because the primary is always required
        with self.assertRaises(IntegrityError):
            obj = self.TestModel()
            for lang_code, _ in settings.LANGUAGES:
                if lang_code == settings.LANGUAGE_CODE:
                    continue
                obj.translated.set(lang_code, True)
            obj.save()

    def test_default_value_none(self):
        """Tests whether the default value for optional languages is
        NoneType."""

        obj = self.TestModel()
        obj.translated.set(settings.LANGUAGE_CODE, True)
        obj.save()

        for lang_code, _ in settings.LANGUAGES:
            if lang_code == settings.LANGUAGE_CODE:
                continue

            assert obj.translated.get(lang_code) is None

    def test_translate(self):
        """Tests whether casting the value to a boolean results in the value
        being returned in the currently active language as a boolean."""

        obj = self.TestModel()
        for lang_code, _ in settings.LANGUAGES:
            obj.translated.set(lang_code, True)
        obj.save()

        obj.refresh_from_db()
        for lang_code, _ in settings.LANGUAGES:
            with translation.override(lang_code):
                assert bool(obj.translated) is True
                assert obj.translated.translate() is True

    def test_translate_primary_fallback(self):
        """Tests whether casting the value to a boolean results in the value
        being returned in the active language and falls back to the primary
        language if there is no value in that language."""

        obj = self.TestModel()
        obj.translated.set(settings.LANGUAGE_CODE, True)

        secondary_language = settings.LANGUAGES[-1][0]
        assert obj.translated.get(secondary_language) is None

        with translation.override(secondary_language):
            assert obj.translated.translate() is True
            assert bool(obj.translated) is True

    def test_get_default_value(self):
        """Tests whether getting the value in a specific language properly
        returns the specified default in case it is not available."""

        obj = self.TestModel()
        obj.translated.set(settings.LANGUAGE_CODE, True)

        secondary_language = settings.LANGUAGES[-1][0]
        assert obj.translated.get(secondary_language) is None
        assert obj.translated.get(secondary_language, False) is False

    def test_completely_optional(self):
        """Tests whether having all languages optional works properly."""

        model = get_fake_model(
            {
                "translated": LocalizedBooleanField(
                    null=True, required=[], blank=True
                )
            }
        )

        obj = model()
        obj.save()

        for lang_code, _ in settings.LANGUAGES:
            assert getattr(obj.translated, lang_code) is None

    def test_store_string(self):
        """Tests whether the field properly raises an error when trying to
        store a non-boolean."""

        for lang_code, _ in settings.LANGUAGES:
            obj = self.TestModel()
            with self.assertRaises(IntegrityError):
                obj.translated.set(lang_code, "haha")
                obj.save()

    def test_none_if_illegal_value_stored(self):
        """Tests whether None is returned for a language if the value stored in
        the database is not a boolean."""

        obj = self.TestModel()
        obj.translated.set(settings.LANGUAGE_CODE, False)
        obj.save()

        with connection.cursor() as cursor:
            table_name = self.TestModel._meta.db_table
            cursor.execute("update %s set translated = 'en=>haha'" % table_name)

        obj.refresh_from_db()
        assert obj.translated.get(settings.LANGUAGE_CODE) is None

    def test_default_value(self):
        """Tests whether a default is properly set when specified."""

        model = get_fake_model(
            {
                "translated": LocalizedBooleanField(
                    default={settings.LANGUAGE_CODE: True}
                )
            }
        )

        obj = model.objects.create()
        assert obj.translated.get(settings.LANGUAGE_CODE) is True

        obj = model()
        for lang_code, _ in settings.LANGUAGES:
            obj.translated.set(lang_code, None)
        obj.save()

        for lang_code, _ in settings.LANGUAGES:
            if lang_code == settings.LANGUAGE_CODE:
                assert obj.translated.get(lang_code) is True
            else:
                assert obj.translated.get(lang_code) is None

    def test_default_value_update(self):
        """Tests whether a default is properly set when specified during
        updates."""

        model = get_fake_model(
            {
                "translated": LocalizedBooleanField(
                    default={settings.LANGUAGE_CODE: True}, null=True
                )
            }
        )

        obj = model.objects.create(
            translated=LocalizedBooleanValue({settings.LANGUAGE_CODE: False})
        )
        assert obj.translated.get(settings.LANGUAGE_CODE) is False

        model.objects.update(
            translated=LocalizedBooleanValue({settings.LANGUAGE_CODE: None})
        )
        obj.refresh_from_db()
        assert obj.translated.get(settings.LANGUAGE_CODE) is True

    def test_callable_default_value(self):
        output = {"en": True}

        def func():
            return output

        model = get_fake_model({"test": LocalizedBooleanField(default=func)})
        obj = model.objects.create()

        assert obj.test["en"] == output["en"]
