from django.contrib.auth.models import Group, User
from django.core import mail
from django.test import RequestFactory, TestCase
from django.urls import reverse

from rr.forms.spadmin import SPAdminForm
from rr.models.serviceprovider import ServiceProvider
from rr.models.spadmin import Keystore


class SPAdminFormTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="tester")
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.admin_sp = ServiceProvider.objects.create(entity_id="test:entity:1", service_type="saml")
        self.user_sp = ServiceProvider.objects.create(entity_id="https://sp2.example.org/sp", service_type="saml")
        self.user_sp.admins.add(self.user)
        self.group = Group.objects.create(name="testgroup")
        self.admin_sp.admin_groups.add(self.group)

    def test_spadmin_form_content_saml_user(self):
        form = SPAdminForm(superuser=False)
        self.assertEqual(len(form.fields), 1)
        self.assertTrue("email" in form.fields)
        self.assertTrue("template" not in form.fields)

    def test_spadmin_form_content_saml_superuser(self):
        form = SPAdminForm(superuser=True)
        self.assertEqual(len(form.fields), 2)
        self.assertTrue("template" in form.fields)

    def test_spadmin_view_denies_anonymous(self):
        response = self.client.get(reverse("admin-list", kwargs={"pk": self.user_sp.pk}), follow=True)
        self.assertRedirects(
            response, reverse("login") + "?next=" + reverse("admin-list", kwargs={"pk": self.user_sp.pk})
        )
        response = self.client.post(reverse("admin-list", kwargs={"pk": self.user_sp.pk}), follow=True)
        self.assertRedirects(
            response, reverse("login") + "?next=" + reverse("admin-list", kwargs={"pk": self.user_sp.pk})
        )

    def test_spadmin_view_denies_unauthorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin-list", kwargs={"pk": self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse("admin-list", kwargs={"pk": self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)

    def test_spadmin_view_user_group(self):
        self.user.groups.add(self.group)
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin-list", kwargs={"pk": self.admin_sp.pk}))
        self.assertEqual(response.status_code, 200)

    def test_spadmin_view_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin-list", kwargs={"pk": self.user_sp.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["object_list"]), 0)

    def test_spadmin_view_post_invite(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("admin-list", kwargs={"pk": self.user_sp.pk}), {"add_invite": "ok", "email": "test@example.org"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["object_list"]), 1)
        self.assertEqual(mail.outbox[0].subject, "[SP-Registry] Access key for managing the service provider")

    def test_spadmin_view_use_invite(self):
        key = Keystore.objects.create_key(sp=self.admin_sp, creator=self.superuser, email="test@example.org")
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("invite-activate-key", kwargs={"invite_key": key.activation_key}), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("summary-view", kwargs={"pk": self.admin_sp.pk}))
        self.assertIn(self.user, self.admin_sp.admins.all())

    def test_spadmin_view_add_group(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("admin-list", kwargs={"pk": self.user_sp.pk}), {"add_admin_group": "ok", "group": "newgroup"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.user_sp.admin_groups.all()), 1)
        self.assertEqual(len(Group.objects.all()), 2)

    def test_spadmin_view_remove_group(self):
        self.user_sp.admin_groups.add(self.group)
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("admin-list", kwargs={"pk": self.user_sp.pk}),
            {"remove_admin_groups": "ok", str(self.group.pk): "on"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.user_sp.admin_groups.all()), 0)
