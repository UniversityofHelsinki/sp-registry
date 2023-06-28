from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings

from auth.shibboleth import get_activation, update_groups


class ActivationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="tester")

    @override_settings(AUTO_ACTIVATE_AFFILIATIONS=["testaff"])
    @override_settings(AUTO_ACTIVATE_GROUPS=["testa", "testgroup", "testb"])
    def test_no_activation(self):
        self.assertFalse(get_activation([], []))
        self.assertFalse(get_activation(["test2"], []))
        self.assertFalse(get_activation(["test"], ["test1"]))

    @override_settings(AUTO_ACTIVATE_AFFILIATIONS=["testaff"])
    @override_settings(AUTO_ACTIVATE_GROUPS=["testgroup"])
    def test_affiliate_activation(self):
        self.assertTrue(get_activation(["test3", "testaff"], []))

    @override_settings(AUTO_ACTIVATE_AFFILIATIONS=["testaff"])
    @override_settings(AUTO_ACTIVATE_GROUPS=["testa", "testgroup", "testb"])
    def test_group_activation(self):
        self.assertTrue(get_activation([], ["testgroup", "test"]))


class UpdateGroupsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="tester")
        self.test_group = Group.objects.create(name="testgroup")
        self.test_group2 = Group.objects.create(name="betatesters")

    def test_group_addition(self):
        update_groups(self.user, ["testgroup"])
        self.assertEqual(self.user.groups.all().count(), 1)
        self.assertEqual(self.user.groups.all().first().name, "testgroup")

    def test_group_addition_multiple(self):
        update_groups(self.user, ["testgroup", "alpha", "betatesters"])
        self.assertEqual(self.user.groups.all().count(), 2)

    def test_group_removal(self):
        self.user.groups.add(self.test_group)
        self.user.groups.add(self.test_group2)
        self.assertEqual(self.user.groups.all().count(), 2)
        update_groups(self.user, ["testgroup", ""])
        self.assertEqual(self.user.groups.all().count(), 1)
        self.assertEqual(self.user.groups.all().first().name, "testgroup")
