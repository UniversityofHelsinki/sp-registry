from io import StringIO

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import RequestFactory, TestCase
from django.utils import timezone

from rr.models.contact import Contact
from rr.models.serviceprovider import ServiceProvider
from rr.models.spadmin import Keystore


class CleanDBTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.sp1 = ServiceProvider.objects.create(entity_id="test:entity:1", service_type="saml")
        self.sp2 = ServiceProvider.objects.create(entity_id="https://sp2.example.org/sp", service_type="saml")

    def test_cleandb_serviceprovider_default(self):
        self.sp1.end_at = timezone.now() - relativedelta(days=365)
        self.sp1.save()
        self.sp2.end_at = timezone.now() - relativedelta(days=364)
        self.sp2.save()
        call_command("cleandb", "-s")
        self.assertEqual(ServiceProvider.objects.all().count(), 1)

    def test_cleandb_serviceprovider_timelimit(self):
        self.sp1.end_at = timezone.now() - relativedelta(days=29)
        self.sp1.save()
        self.sp2.end_at = timezone.now() - relativedelta(days=31)
        self.sp2.save()
        call_command("cleandb", "-d 30", "-s")
        self.assertEqual(ServiceProvider.objects.all().count(), 1)

    def test_cleandb_serviceprovider_listonly(self):
        self.sp1.end_at = timezone.now() - relativedelta(days=365)
        self.sp1.save()
        self.sp2.end_at = timezone.now() - relativedelta(days=364)
        self.sp2.save()
        out = StringIO()
        call_command("cleandb", "-l", "-s", stdout=out)
        self.assertIn("(List only) Removing service provider: test:entity:1", out.getvalue())
        self.assertEqual(ServiceProvider.objects.all().count(), 2)

    def test_cleandb_contacts(self):
        self.sp1.end_at = timezone.now() - relativedelta(days=365)
        self.sp1.save()
        self.sp2.end_at = timezone.now() - relativedelta(days=364)
        self.sp2.save()
        Contact.objects.create(sp=self.sp1, type="administrative")
        Contact.objects.create(sp=self.sp2, type="administrative")
        call_command("cleandb", "-c")
        self.assertEqual(Contact.objects.all().count(), 1)

    def test_cleandb_users(self):
        User.objects.create(username="tester")
        User.objects.create(username="tester3", last_login=timezone.now() - relativedelta(days=365))
        test_user = User.objects.create(username="tester2", last_login=timezone.now() - relativedelta(days=365))
        self.sp1.admins.add(test_user)
        call_command("cleandb", "-u")
        self.assertEqual(User.objects.all().count(), 2)

    def test_cleandb_invites(self):
        user = User.objects.create(username="tester")
        Keystore.objects.create(
            sp=self.sp1,
            creator=user,
            activation_key="abc",
            email="test@example.org",
            valid_until=timezone.now() - relativedelta(days=1),
        )
        Keystore.objects.create(
            sp=self.sp1,
            creator=user,
            activation_key="abc",
            email="test@example.org",
            valid_until=timezone.now() + relativedelta(days=1),
        )
        call_command("cleandb", "-i")
        self.assertEqual(Keystore.objects.all().count(), 1)
