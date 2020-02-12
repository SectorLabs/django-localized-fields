import django

from django.conf import settings
from django.db import connection
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import translation

from localized_fields.fields import LocalizedIntegerField
from localized_fields.value import LocalizedIntegerValue

from .fake_model import get_fake_model


class LocalizedIntegerFieldTestCase(TestCase):
    """Tests whether the :see:LocalizedIntegerField and
    :see:LocalizedIntegerValue works properly."""

    TestModel = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.TestModel = get_fake_model({"score": LocalizedIntegerField()})

    def test_basic(self):
        """Tests the basics of storing integer values."""

        obj = self.TestModel()
        for index, (lang_code, _) in enumerate(settings.LANGUAGES):
            obj.score.set(lang_code, index + 1)
        obj.save()

        obj = self.TestModel.objects.all().first()
        for index, (lang_code, _) in enumerate(settings.LANGUAGES):
            assert obj.score.get(lang_code) == index + 1

    def test_primary_language_required(self):
        """Tests whether the primary language is required by default and all
        other languages are optiona."""

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
                obj.score.set(lang_code, 23)
            obj.save()

    def test_default_value_none(self):
        """Tests whether the default value for optional languages is
        NoneType."""

        obj = self.TestModel()
        obj.score.set(settings.LANGUAGE_CODE, 1234)
        obj.save()

        for lang_code, _ in settings.LANGUAGES:
            if lang_code == settings.LANGUAGE_CODE:
                continue

            assert obj.score.get(lang_code) is None

    def test_translate(self):
        """Tests whether casting the value to an integer results in the value
        being returned in the currently active language as an integer."""

        obj = self.TestModel()
        for index, (lang_code, _) in enumerate(settings.LANGUAGES):
            obj.score.set(lang_code, index + 1)
        obj.save()

        obj.refresh_from_db()
        for index, (lang_code, _) in enumerate(settings.LANGUAGES):
            with translation.override(lang_code):
                assert int(obj.score) == index + 1
                assert obj.score.translate() == index + 1

    def test_translate_primary_fallback(self):
        """Tests whether casting the value to an integer results in the value
        begin returned in the active language and falls back to the primary
        language if there is no value in that language."""

        obj = self.TestModel()
        obj.score.set(settings.LANGUAGE_CODE, 25)

        secondary_language = settings.LANGUAGES[-1][0]
        assert obj.score.get(secondary_language) is None

        with translation.override(secondary_language):
            assert obj.score.translate() == 25
            assert int(obj.score) == 25

    def test_get_default_value(self):
        """Tests whether getting the value in a specific language properly
        returns the specified default in case it is not available."""

        obj = self.TestModel()
        obj.score.set(settings.LANGUAGE_CODE, 25)

        secondary_language = settings.LANGUAGES[-1][0]
        assert obj.score.get(secondary_language) is None
        assert obj.score.get(secondary_language, 1337) == 1337

    def test_completely_optional(self):
        """Tests whether having all languages optional works properly."""

        model = get_fake_model(
            {"score": LocalizedIntegerField(null=True, required=[], blank=True)}
        )

        obj = model()
        obj.save()

        for lang_code, _ in settings.LANGUAGES:
            assert getattr(obj.score, lang_code) is None

    def test_store_string(self):
        """Tests whether the field properly raises an error when trying to
        store a non-integer."""

        for lang_code, _ in settings.LANGUAGES:
            obj = self.TestModel()
            with self.assertRaises(IntegrityError):
                obj.score.set(lang_code, "haha")
                obj.save()

    def test_none_if_illegal_value_stored(self):
        """Tests whether None is returned for a language if the value stored in
        the database is not an integer."""

        obj = self.TestModel()
        obj.score.set(settings.LANGUAGE_CODE, 25)
        obj.save()

        with connection.cursor() as cursor:
            table_name = self.TestModel._meta.db_table
            cursor.execute("update %s set score = 'en=>haha'" % table_name)

        obj.refresh_from_db()
        assert obj.score.get(settings.LANGUAGE_CODE) is None

    def test_default_value(self):
        """Tests whether a default is properly set when specified."""

        model = get_fake_model(
            {
                "score": LocalizedIntegerField(
                    default={settings.LANGUAGE_CODE: 75}
                )
            }
        )

        obj = model.objects.create()
        assert obj.score.get(settings.LANGUAGE_CODE) == 75

        obj = model()
        for lang_code, _ in settings.LANGUAGES:
            obj.score.set(lang_code, None)
        obj.save()

        for lang_code, _ in settings.LANGUAGES:
            if lang_code == settings.LANGUAGE_CODE:
                assert obj.score.get(lang_code) == 75
            else:
                assert obj.score.get(lang_code) is None

    def test_default_value_update(self):
        """Tests whether a default is properly set when specified during
        updates."""

        model = get_fake_model(
            {
                "score": LocalizedIntegerField(
                    default={settings.LANGUAGE_CODE: 75}, null=True
                )
            }
        )

        obj = model.objects.create(
            score=LocalizedIntegerValue({settings.LANGUAGE_CODE: 35})
        )
        assert obj.score.get(settings.LANGUAGE_CODE) == 35

        model.objects.update(
            score=LocalizedIntegerValue({settings.LANGUAGE_CODE: None})
        )
        obj.refresh_from_db()
        assert obj.score.get(settings.LANGUAGE_CODE) == 75

    def test_callable_default_value(self):
        output = {'en': 5}

        def func():
            return output

        model = get_fake_model({"test": LocalizedIntegerValue(default=func)})
        obj = model()

        assert obj.test['en'] == output['en']

    def test_order_by(self):
        """Tests whether ordering by a :see:LocalizedIntegerField key works
        expected."""

        # using key transforms (score__en) in order_by(..) is only
        # supported since Django 2.1
        # https://github.com/django/django/commit/2162f0983de0dfe2178531638ce7ea56f54dd4e7#diff-0edd853580d56db07e4020728d59e193

        if django.VERSION < (2, 1):
            return

        model = get_fake_model(
            {
                "score": LocalizedIntegerField(
                    default={settings.LANGUAGE_CODE: 1337}, null=True
                )
            }
        )

        model.objects.create(score=dict(en=982))
        model.objects.create(score=dict(en=382))
        model.objects.create(score=dict(en=1331))

        res = list(
            model.objects.values_list("score__en", flat=True).order_by(
                "-score__en"
            )
        )
        assert res == [1331, 982, 382]

