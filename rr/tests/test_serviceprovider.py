from django.contrib.auth.models import Group, User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from rr.models.serviceprovider import ServiceProvider
from rr.views.serviceprovider import ServiceProviderList


class ServiceProviderListTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.admin_sp = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='saml')
        self.user_sp = ServiceProvider.objects.create(entity_id='https://sp2.example.org/sp', service_type='saml',
                                                      production=True)
        self.user_sp.admins.add(self.user)
        self.group = Group.objects.create(name='testgroup')
        self.admin_sp.admin_groups.add(self.group)

    def test_sp_view_list_denies_anonymous(self):
        response = self.client.get(reverse('serviceprovider-list'), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('serviceprovider-list'))
        response = self.client.post(reverse('serviceprovider-list'), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('serviceprovider-list'))

    def test_sp_view_list_normal_user(self):
        request = self.factory.get(reverse('serviceprovider-list'))
        request.user = self.user
        response = ServiceProviderList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.admin_sp not in response.context_data['object_list'])
        self.assertTrue(self.user_sp in response.context_data['object_list'])

    def test_sp_view_list_normal_user_group_permissions(self):
        self.user.groups.add(self.group)
        request = self.factory.get(reverse('serviceprovider-list'))
        request.user = self.user
        response = ServiceProviderList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.admin_sp in response.context_data['object_list'])
        self.assertTrue(self.user_sp in response.context_data['object_list'])

    def test_sp_view_list_super_user(self):
        request = self.factory.get(reverse('serviceprovider-list'))
        request.user = self.superuser
        response = ServiceProviderList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.admin_sp in response.context_data['object_list'])
        self.assertTrue(self.user_sp in response.context_data['object_list'])


class ServiceProviderDetailTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.admin_sp = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='saml')
        self.user_sp = ServiceProvider.objects.create(entity_id='https://sp2.example.org/sp', service_type='saml')
        self.user_sp.admins.add(self.user)

    def test_sp_view_denies_anonymous(self):
        response = self.client.get(reverse('summary-view', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('summary-view', kwargs={'pk': self.user_sp.pk}))
        response = self.client.post(reverse('summary-view', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('summary-view', kwargs={'pk': self.user_sp.pk}))

    def test_sp_view_denies_unauthorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('summary-view', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('summary-view', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You should not be here.', response.content.decode())

    def test_sp_view_summary(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('summary-view', kwargs={'pk': self.user_sp.pk}))
        self.assertEqual(response.status_code, 200)

    def test_sp_view_validation_message(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('summary-view', kwargs={'pk': self.user_sp.pk}))
        self.assertIn('Waiting for validation', response.content.decode())

    def test_sp_view_validation_message_superuser(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('summary-view', kwargs={'pk': self.user_sp.pk}))
        self.assertIn('Validate changes', response.content.decode())

    def test_sp_view_modify_before_validate(self):
        self.client.force_login(self.superuser)
        modified_date = self.user_sp.updated_at.strftime("%Y%m%d%H%M%S%f")
        self.user_sp.save()
        response = self.client.post(reverse('summary-view', kwargs={'pk': self.user_sp.pk}),
                                    {'validate_changes': 'ok', 'modified_date': modified_date},
                                    follow=True)
        self.assertIn('Validate changes', response.content.decode())
        self.assertEqual(response.status_code, 200)

    def test_sp_view_validate(self):
        self.client.force_login(self.superuser)
        modified_date = self.user_sp.updated_at.strftime("%Y%m%d%H%M%S%f")
        response = self.client.post(reverse('summary-view', kwargs={'pk': self.user_sp.pk}),
                                    {'validate_changes': 'ok', 'modified_date': modified_date},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Validate changes', response.content.decode())
        self.assertEqual(ServiceProvider.objects.all().count(), 2)
        self.assertEqual(ServiceProvider.objects.filter(validated=None).count(), 1)
        self.assertIsNotNone(ServiceProvider.objects.get(pk=self.user_sp.pk).validated)


class ServiceProviderBasicInformationTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.admin_sp = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='saml')
        self.user_sp = ServiceProvider.objects.create(entity_id='https://sp2.example.org/sp', service_type='saml')
        self.user_sp.admins.add(self.user)

    def test_sp_basic_information_view_denies_anonymous(self):
        response = self.client.get(reverse('basicinformation-update', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('basicinformation-update', kwargs={'pk': self.user_sp.pk}))
        response = self.client.post(reverse('basicinformation-update', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('basicinformation-update', kwargs={'pk': self.user_sp.pk}))

    def test_sp_basic_information_view_denies_unauthorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('basicinformation-update', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('basicinformation-update', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)

    def test_sp_basic_information_view_summary(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('basicinformation-update', kwargs={'pk': self.user_sp.pk}))
        self.assertEqual(response.status_code, 200)

    def test_sp_basic_information_admin_field_visiblity(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('basicinformation-update', kwargs={'pk': self.user_sp.pk}))
        self.assertNotIn('organization', response.content.decode())
        self.assertNotIn('admin_notes', response.content.decode())
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('basicinformation-update', kwargs={'pk': self.user_sp.pk}))
        self.assertIn('organization', response.content.decode())
        self.assertIn('admin_notes', response.content.decode())

    def test_sp_basic_information_name_required(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('basicinformation-update', kwargs={'pk': self.user_sp.pk}),
                                    {'name_fi': '', 'name_en': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Name in English or in Finnish is required.', response.content.decode())
        response = self.client.post(reverse('basicinformation-update', kwargs={'pk': self.user_sp.pk}),
                                    {'name_fi': 'abc', 'name_en': ''}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Name in English or in Finnish is required.', response.content.decode())
        response = self.client.post(reverse('basicinformation-update', kwargs={'pk': self.user_sp.pk}),
                                    {'name_fi': '', 'name_en': 'abc'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Name in English or in Finnish is required.', response.content.decode())

