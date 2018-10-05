import re

from django.core.validators import URLValidator, ValidationError
from django.db.models import Q
from django.forms import ModelForm, Form, BooleanField
from django.forms.fields import CharField
from django.forms.widgets import HiddenInput, Textarea, CheckboxInput
from django.utils.translation import ugettext as _

from rr.models.nameidformat import NameIDFormat
from rr.models.serviceprovider import ServiceProvider, ldap_entity_id_from_name


class BasicInformationForm(ModelForm):
    """
    Form for updating basic information from ServiceProvider object
    """

    class Meta:
        model = ServiceProvider
        fields = ['organization', 'name_fi', 'name_en', 'name_sv', 'description_fi',
                  'description_en', 'description_sv', 'privacypolicy_fi', 'privacypolicy_en',
                  'privacypolicy_sv', 'login_page_url', 'application_portfolio', 'notes',
                  'admin_notes']
        help_texts = {
            'organization': _('Organization name, only changeable by the registry admins.'),
            'name_fi': _('Short (max 70 characters) and descriptive name for the service '
                         'in Finnish.<div class="text-danger">'
                         'Required for both production and test use.</div>'),
            'name_en': _('Short (max 70 characters) and descriptive name for the service '
                         'in English.<div class="text-danger">'
                         'Required for both production and test use.</div>'),
            'name_sv': _('Short (max 70 characters) and descriptive name for the service '
                         'in Swedish.'),
            'description_fi': _('Short (max 140 characters) description of the service '
                                'in Finnish. <div class="text-danger">'
                                'Required for both production and test use.</div>'),
            'description_en': _('Short (max 140 characters) description of the service '
                                'in English. <div class="text-danger">'
                                'Required for both production and test use.</div>'),
            'description_sv': _('Short (max 140 characters) description of the service '
                                'in Swedish.'),
            'privacypolicy_fi': _('Link to privacy policy in Finnish. Link must be publicly'
                                  'accessible. <div class="text-danger">Required for production '
                                  'use if the service requests any personal information.</div>'),
            'privacypolicy_en': _('Link to privacy policy in English. Link must be publicly '
                                  'accessible. <div class="text-danger">Required for production '
                                  'use if the service requests any personal information.</div>'),
            'privacypolicy_sv': _('Link to privacy policy in Swedish. Link must be publicly '
                                  'accessible.'),
            'login_page_url': _('Used for debugging and testing services.'),
            'application_portfolio': _('Link to external application portfolio.'),
            'notes': _('Additional notes about this service.'),
            'admin_notes': _('Additional administrative notes. Writable only by registry admins '
                             'but showed in summary to SP admins.'),
        }

    def __init__(self, *args, **kwargs):
        """
        Only show admin_notes field for superusers
        """
        self.request = kwargs.pop('request', None)
        super(BasicInformationForm, self).__init__(*args, **kwargs)
        if not self.request.user.is_superuser:
            del self.fields['admin_notes']
            del self.fields['organization']


class TechnicalInformationForm(ModelForm):
    """
    Form for updating technical information from ServiceProvider object
    """

    class Meta:
        model = ServiceProvider
        fields = ['entity_id', 'discovery_service_url', 'nameidformat', 'sign_assertions',
                  'sign_requests', 'sign_responses', 'encrypt_assertions', 'production', 'test',
                  'saml_product', 'autoupdate_idp_metadata']
        help_texts = {
            'entity_id': _('Should be URI including scheme, hostname of your application and path '
                           'e.g. https://test.helsinki.fi/sp. <div class="text-danger">'
                           'Required for both production and test use.</div>'),
            'discovery_service_url': _('For service providers supporting discovery service. '
                                       'Usually only valid if you are accepting logins for '
                                       'multiple IdPs.'),
            'nameidformat': _(
                    'Support for name identifier formats. Check <a href="'
                    'https://wiki.shibboleth.net/confluence/display/CONCEPT/NameIdentifiers'
                    '" target="_blank">Shibboleth wiki</a> for more information.'),
            'sign_assertions': _('IdP sings attribute assertions sent to SP. Defaults to False '
                                 'because assertions are encrypted by default.'),
            'sign_requests': _('IdP requires signed authentication requests from this SP.'),
            'sign_responses': _('IdP signs responses sent to SP. Defaults to True and should not '
                                'be changed.'),
            'encrypt_assertions': _('IdP encrypts attribute assertions sent to SP. Defaults to '
                                    'True. Do not change unless you are using a SP that does '
                                    'not support encryption.'),
            'production': _('Publish this SP to the production IdP. Only validated data is used. '
                            'Any changes to production SPs must be validated by the IdP '
                            'administrators before coming into effect.'
                            '<div class="text-danger">Required for production use.</div>'),
            'test': _('Publish this SP to the test IdP using unvalidated data. '
                      'Any changes might take up to 15 minutes until they are published to '
                      'the test IdP.'),
            'saml_product': _('For administrative use e.g. for testing different SPs during IdP '
                              'updates.'),
            'autoupdate_idp_metadata': _('Does this SP automatically update IdP metadata at least '
                                         'once a day?'),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TechnicalInformationForm, self).__init__(*args, **kwargs)
        if not self.request.user.is_superuser:
            # Limit choices to public and current values
            self.fields['nameidformat'].queryset = NameIDFormat.objects.filter(
                Q(public=True) | Q(pk__in=self.instance.nameidformat.all()))

    def clean_entity_id(self):
        """
        Allow only superusers set entity id something else than URL.
        """
        entity_id = self.cleaned_data['entity_id']
        if not self.request.user.is_superuser and "entity_id" in self.changed_data:
            url_validator = URLValidator()
            try:
                url_validator(entity_id)
            except ValidationError:
                raise ValidationError(_("Entity Id should be URI, please contact IdP admins if "
                                        "this is not possible."))
        if ServiceProvider.objects.filter(entity_id=entity_id, end_at=None,
                                          history=None).exclude(pk=self.instance.pk):
            raise ValidationError(_("Entity Id already exists"))
        return entity_id


class LdapTechnicalInformationForm(ModelForm):
    """
    Form for updating LDAP technical information from ServiceProvider object
    """

    class Meta:
        model = ServiceProvider
        fields = ['server_names', 'target_group', 'service_account', 'service_account_contact', 'can_access_all_ldap_groups',
                  'local_storage_users', 'local_storage_passwords', 'local_storage_passwords_info', 'local_storage_groups', 'production']
        widgets = {
          'service_account_contact': Textarea(attrs={'rows': 2}),
          'local_storage_passwords_info': Textarea(attrs={'rows': 5}),
          'service_account': CheckboxInput(attrs={'class': 'hideCheck1'}),
          'local_storage_passwords': CheckboxInput(attrs={'class': 'hideCheck2'}),
        }
        help_texts = {
            'server_names': _('Full server names (not IPs), separated by space. User for access control.'),
            'target_group': _('What is the target group (users) of this service?'),
            'service_account': _('Separate service account is used for LDAP queries (recommended way).'),
            'service_account_contact': _('Email and phone number for delivering service account credentials.'),
            'can_access_all_ldap_groups': _('Service requires access to all LDAP groups.'),
            'local_storage_users': _('Service stores user name and released attributes locally.'),
            'local_storage_passwords': _('Service stores user passwords locally.'),
            'local_storage_passwords_info': _('Why is this service storing user passwords locally and how? This is not generally a good idea.'),
            'local_storage_groups': _('Service stores requested groups and their member lists locally.'),
            'production': _('Publish this service to LDAP production servers.'),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(LdapTechnicalInformationForm, self).__init__(*args, **kwargs)

    def clean_server_names(self):
        """
        Check server names format
        """
        server_names = self.cleaned_data['server_names']
        server_names_list = server_names.splitlines()
        pattern = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
        for server_name in server_names_list:
            if not pattern.match(server_name):
                raise ValidationError(_("Invalid list of server names."))
        return server_names

    def clean(self):
        cleaned_data = super().clean()
        service_account = cleaned_data.get("service_account")
        service_account_contact = cleaned_data.get("service_account_contact")
        local_storage_passwords = cleaned_data.get("local_storage_passwords")
        local_storage_passwords_info = cleaned_data.get("local_storage_passwords_info")
        if service_account:
            if not service_account_contact:
                self.add_error('service_account_contact', "Please give contact information.")
        if local_storage_passwords:
            if not local_storage_passwords_info:
                self.add_error('local_storage_passwords_info', "Please give a reason for saving passwords.")


class SamlServiceProviderCreateForm(ModelForm):
    """
    Form for creating a service provider. Same as basic information form and entity_id.
    """

    class Meta:
        model = ServiceProvider
        fields = ['entity_id', 'name_fi', 'name_en', 'name_sv', 'description_fi', 'description_en',
                  'description_sv', 'privacypolicy_fi', 'privacypolicy_en', 'privacypolicy_sv',
                  'login_page_url', 'application_portfolio', 'notes']
        help_texts = {
            'entity_id': _('Should be URI including scheme, hostname of your application and path '
                           'e.g. https://test.helsinki.fi/sp. <div class="text-danger">'
                           'Required for both production and test use.</div>'),
            'name_fi': _('Short (max 70 characters) and descriptive name for the service '
                         'in Finnish.<div class="text-danger">'
                         'Required for both production and test use.</div>'),
            'name_en': _('Short (max 70 characters) and descriptive name for the service '
                         'in English.<div class="text-danger">'
                         'Required for both production and test use.</div>'),
            'name_sv': _('Short (max 70 characters) and descriptive name for the service '
                         'in Swedish.'),
            'description_fi': _('Short (max 140 characters) description of the service '
                                'in Finnish. <div class="text-danger">'
                                'Required for both production and test use.</div>'),
            'description_en': _('Short (max 140 characters) description of the service '
                                'in English. <div class="text-danger">'
                                'Required for both production and test use.</div>'),
            'description_sv': _('Short (max 140 characters) description of the service '
                                'in Swedish.'),
            'privacypolicy_fi': _('Link to privacy policy in Finnish. Link must be publicly'
                                  'accessible. <div class="text-danger">Required for production '
                                  'use if the service requests any personal information.</div>'),
            'privacypolicy_en': _('Link to privacy policy in English. Link must be publicly '
                                  'accessible. <div class="text-danger">Required for production '
                                  'use if the service requests any personal information.</div>'),
            'privacypolicy_sv': _('Link to privacy policy in Swedish. Link must be publicly '
                                  'accessible.'),
            'login_page_url': _('Used for debugging and testing services.'),
            'application_portfolio': _('Link to external application portfolio.'),
            'notes': _('Additional notes about this service.'),
         }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SamlServiceProviderCreateForm, self).__init__(*args, **kwargs)

    def clean_entity_id(self):
        """
        Allow only superusers set entity id something else than URL.
        """
        entity_id = self.cleaned_data['entity_id']
        if not self.request.user.is_superuser and "entity_id" in self.changed_data:
            url_validator = URLValidator()
            try:
                url_validator(entity_id)
            except ValidationError:
                raise ValidationError(_("Entity Id should be URI, please contact IdP admins if "
                                        "this is not possible."))
        if ServiceProvider.objects.filter(entity_id=entity_id, end_at=None,
                                          history=None).exclude(pk=self.instance.pk):
            raise ValidationError(_("Entity Id already exists"))
        return entity_id


class LdapServiceProviderCreateForm(ModelForm):
    """
    Form for creating a service provider. Same as basic information form and entity_id.
    """

    class Meta:
        model = ServiceProvider
        fields = ['server_names', 'name_fi', 'name_en', 'name_sv', 'description_fi', 'description_en', 'description_sv',
                  'privacypolicy_fi', 'privacypolicy_en', 'privacypolicy_sv',
                  'login_page_url', 'application_portfolio', 'notes']
        help_texts = {
            'server_names': _('Full server names (not IPs), one per line. Used for access control. <div class="text-danger">Required.</div>'),
            'name_fi': _('Short (max 70 characters) and descriptive name for the service in Finnish. <div class="text-danger">Required. </div>'),
            'name_en': _('Short (max 70 characters) and descriptive name for the service in English.'),
            'name_sv': _('Short (max 70 characters) and descriptive name for the service in Swedish.'),
            'description_fi': _('Short (max 140 characters) description of the service in Finnish. <div class="text-danger">Required.</div>'),
            'description_en': _('Short (max 140 characters) description of the service in English.'),
            'description_sv': _('Short (max 140 characters) description of the service in Swedish.'),
            'privacypolicy_fi': _('Link to privacy policy in Finnish. Link must be publicly accessible. <div class="text-danger">Required if the service requests any personal information.</div>'),
            'privacypolicy_en': _('Link to privacy policy in English. Link must be publicly accessible.'),
            'privacypolicy_sv': _('Link to privacy policy in Swedish. Link must be publicly accessible.'),
            'login_page_url': _('Used for debugging and testing services.'),
            'application_portfolio': _('Link to external application portfolio.'),
            'notes': _('Additional notes about this service.'),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(LdapServiceProviderCreateForm, self).__init__(*args, **kwargs)
        self.fields['name_fi'].required = True

    def clean_server_names(self):
        """
        Check server names format
        """
        server_names = self.cleaned_data['server_names']
        server_names_list = server_names.splitlines()
        pattern = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
        for server_name in server_names_list:
            if not pattern.match(server_name):
                raise ValidationError(_("Invalid list of server names."))
        return server_names

    def clean_name_fi(self):
        """
        Check name_fi format
        """
        name_fi = self.cleaned_data['name_fi']
        if len(ldap_entity_id_from_name(name_fi)) == 0:
            raise ValidationError(_("Invalid Finnish name."))
        return name_fi


class ServiceProviderCloseForm(Form):
    """
    Form for closing service provider.
    """
    confirm = BooleanField(help_text=_("Confirm closing"))


class ServiceProviderValidationForm(Form):
    """
    Form for validation service provider.
    """
    no_email = BooleanField(required=False, help_text=_("Do not send validation email to SP "
                                                        "admins."))
    modified_date = CharField()

    def __init__(self, *args, **kwargs):
        self.modified_date = kwargs.pop('modified_date', None)
        super(ServiceProviderValidationForm, self).__init__(*args, **kwargs)
        self.fields['modified_date'].widget = HiddenInput()
        self.fields['modified_date'].initial = self.modified_date
