
from django.contrib.auth.models import Group, User
from django.test import TestCase

from auth.shibboleth import update_groups


class UpdateGroupsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='tester')
        self.test_group = Group.objects.create(name="testgroup")
        self.test_group2 = Group.objects.create(name="betatesters")

    def test_group_addition(self):
        update_groups(self.user, 'testgroup')
        self.assertEqual(self.user.groups.all().count(), 1)
        self.assertEqual(self.user.groups.all().first().name, 'testgroup')

    def test_group_addition_multiple(self):
        update_groups(self.user, 'testgroup;alpha;betatesters')
        self.assertEqual(self.user.groups.all().count(), 2)

    def test_group_removal(self):
        self.user.groups.add(self.test_group)
        self.user.groups.add(self.test_group2)
        self.assertEqual(self.user.groups.all().count(), 2)
        update_groups(self.user, 'testgroup;')
        self.assertEqual(self.user.groups.all().count(), 1)
        self.assertEqual(self.user.groups.all().first().name, 'testgroup')
