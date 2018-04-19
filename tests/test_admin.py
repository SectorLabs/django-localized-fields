from django.apps import apps
from django.contrib import admin
from django.contrib.admin.checks import check_admin_app
from django.db import models
from django.test import TestCase

from localized_fields.fields import LocalizedField
from localized_fields.admin import LocalizedFieldsAdminMixin

from tests.fake_model import get_fake_model


class LocalizedFieldsAdminMixinTestCase(TestCase):
    """Tests the :see:LocalizedFieldsAdminMixin class."""

    TestModel = None
    TestRelModel = None

    @classmethod
    def setUpClass(cls):
        """Creates the test model in the database."""

        super(LocalizedFieldsAdminMixinTestCase, cls).setUpClass()

        cls.TestRelModel = get_fake_model(
            {
                'description': LocalizedField()
            }
        )
        cls.TestModel = get_fake_model(
            {
                'title': LocalizedField(),
                'rel': models.ForeignKey(cls.TestRelModel,
                                         on_delete=models.CASCADE)
            }
        )

    def tearDown(self):
        if admin.site.is_registered(self.TestModel):
            admin.site.unregister(self.TestModel)
        if admin.site.is_registered(self.TestRelModel):
            admin.site.unregister(self.TestRelModel)

    @classmethod
    def test_model_admin(cls):
        """Tests whether :see:LocalizedFieldsAdminMixin
        mixin are works with admin.ModelAdmin"""

        @admin.register(cls.TestModel)
        class TestModelAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
            pass

        assert len(check_admin_app(apps.get_app_configs())) == 0

    @classmethod
    def test_stackedmodel_admin(cls):
        """Tests whether :see:LocalizedFieldsAdminMixin mixin are works
        with admin.StackedInline"""

        class TestModelStackedInline(LocalizedFieldsAdminMixin,
                                     admin.StackedInline):
            model = cls.TestModel

        @admin.register(cls.TestRelModel)
        class TestRelModelAdmin(admin.ModelAdmin):
            inlines = [
                TestModelStackedInline,
            ]

        assert len(check_admin_app(apps.get_app_configs())) == 0

    @classmethod
    def test_tabularmodel_admin(cls):
        """Tests whether :see:LocalizedFieldsAdminMixin mixin are works
        with admin.TabularInline"""

        class TestModelTabularInline(LocalizedFieldsAdminMixin,
                                     admin.TabularInline):
            model = cls.TestModel

        @admin.register(cls.TestRelModel)
        class TestRelModelAdmin(admin.ModelAdmin):
            inlines = [
                TestModelTabularInline,
            ]

        assert len(check_admin_app(apps.get_app_configs())) == 0
