from django.test import TestCase

from localized_fields.fields import LocalizedField

from .fake_model import get_fake_model


class LocalizedQuerySetTestCase(TestCase):
    """Tests query sets with models containing :see:LocalizedField."""

    Model = None

    @classmethod
    def setUpClass(cls):
        """Creates the test models in the database."""

        super(LocalizedQuerySetTestCase, cls).setUpClass()

        cls.Model = get_fake_model({"title": LocalizedField()})

    @classmethod
    def test_assign_raw_dict(cls):
        inst = cls.Model()
        inst.title = dict(en="Bread", ro="Paine")
        inst.save()

        inst = cls.Model.objects.get(pk=inst.pk)
        assert inst.title.en == "Bread"
        assert inst.title.ro == "Paine"

    @classmethod
    def test_assign_raw_dict_update(cls):
        inst = cls.Model.objects.create(title=dict(en="Bread", ro="Paine"))

        cls.Model.objects.update(title=dict(en="Beer", ro="Bere"))

        inst = cls.Model.objects.get(pk=inst.pk)
        assert inst.title.en == "Beer"
        assert inst.title.ro == "Bere"
