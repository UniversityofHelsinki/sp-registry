from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from django.urls import reverse

from rr.forms.attribute import AttributeForm
from rr.models.attribute import Attribute
from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.views.attribute import attribute_list


class AttributeFormTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.admin_sp = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='saml')
        self.user_sp = ServiceProvider.objects.create(entity_id='https://sp2.example.org/sp', service_type='saml')
        self.user_sp.admins.add(self.user)
        self.attr_cn = Attribute.objects.create(friendlyname='cn',
                                                name='urn:oid:2.5.4.3',
                                                attributeid='id-urn:mace:dir:attribute-def:cn',
                                                nameformat='urn:oasis:names:tc:SAML:2.0:attrname-format:uri',
                                                public_saml=True,
                                                public_ldap=True)
        self.attr_eppn = Attribute.objects.create(friendlyname='eduPersonPrincipalName',
                                                  name='urn:oid:1.3.6.1.4.1.5923.1.1.1.6',
                                                  attributeid='id-urn:mace:dir:attribute-def:eduPersonPrincipalName',
                                                  nameformat='urn:oasis:names:tc:SAML:2.0:attrname-format:uri',
                                                  public_saml=True,
                                                  public_ldap=False)
        self.attr_uniqueid = Attribute.objects.create(friendlyname='schacPersonalUniqueID',
                                        name='urn:oid:1.3.6.1.4.1.25178.1.2.15',
                                        attributeid='id-urn:mace:terena.org:schac:attribute-def:schacPersonalUniqueID',
                                        nameformat='urn:oasis:names:tc:SAML:2.0:attrname-format:uri',
                                        public_saml=False,
                                        public_ldap=False)

    def test_attribute_form_content_saml_user(self):
        form = AttributeForm(sp=self.user_sp, is_admin=False)
        self.assertEqual(len(form.fields), 2)
        self.assertTrue('eduPersonPrincipalName' in form.fields)
        self.assertTrue('schacPersonalUniqueID' not in form.fields)

    def test_attribute_form_content_saml_superuser(self):
        form = AttributeForm(sp=self.user_sp, is_admin=True)
        self.assertEqual(len(form.fields), 3)
        self.assertTrue('schacPersonalUniqueID' in form.fields)

    def test_attribute_form_save_content_saml_user(self):
        form_data = {'eduPersonPrincipalName': 'User Identification'}
        form = AttributeForm(sp=self.user_sp, is_admin=False, data=form_data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.fields['eduPersonPrincipalName'].has_changed)
        self.assertEqual('Name: urn:oid:1.3.6.1.4.1.5923.1.1.1.6 (<a target="_blank" href="https://wiki.eduuni.fi/display/CSCHAKA/funetEduPersonSchema2dot2#funetEduPersonSchema2dot2-eduPersonPrincipalName">schema</a>)', form.fields['eduPersonPrincipalName'].help_text)

    def test_attribute_form_view(self):
        form_data = {'eduPersonPrincipalName': 'User Identification'}
        request = self.factory.post(reverse('attribute-list', kwargs={'pk': self.user_sp.pk}), form_data)
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response = attribute_list(request, pk=self.user_sp.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.user_sp.attributes.all()), 1)
        self.assertEqual(self.user_sp.attributes.all()[0], self.attr_eppn)

    def test_attribute_view_denies_anonymous(self):
        response = self.client.get(reverse('attribute-list', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('attribute-list', kwargs={'pk': self.user_sp.pk}))
        response = self.client.post(reverse('attribute-list', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('attribute-list', kwargs={'pk': self.user_sp.pk}))

    def test_attribute_view_denies_unauthorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('attribute-list', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('attribute-list', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)

    def test_attribute_view_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('attribute-list', kwargs={'pk': self.user_sp.pk}))
        self.assertEqual(response.status_code, 200)

    def test_attribute_view_post_attribute(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('attribute-list', kwargs={'pk': self.user_sp.pk}),
                                    {'add_attribute': 'ok', 'eduPersonPrincipalName': 'User identification'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user_sp.attributes.all()[0], self.attr_eppn)

    def test_attribute_view_remove_attribute(self):
        SPAttribute.objects.create(attribute=self.attr_eppn, sp=self.user_sp, reason='User identification')
        self.assertEqual(self.user_sp.attributes.all()[0], self.attr_eppn)
        self.client.force_login(self.user)
        response = self.client.post(reverse('attribute-list', kwargs={'pk': self.user_sp.pk}),
                                    {'add_attribute': 'ok', 'eduPersonPrincipalName': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(SPAttribute.objects.get(attribute=self.attr_eppn, sp=self.user_sp).end_at)
