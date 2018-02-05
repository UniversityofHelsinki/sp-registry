from django.forms import ModelForm
from rr.models.serviceprovider import ServiceProvider
from django.utils.translation import ugettext_lazy as _
from django.core.validators import URLValidator, ValidationError


class BasicInformationForm(ModelForm):

    class Meta:
        model = ServiceProvider
        fields = ['entity_id', 'name_fi', 'name_en', 'name_sv', 'description_fi', 'description_en', 'description_sv',
                  'privacypolicy_fi', 'privacypolicy_en', 'privacypolicy_sv',
                  'login_page_url', 'discovery_service_url', 'name_format_transient', 'name_format_persistent',
                  'sign_assertions', 'sign_requests', 'sign_responses', 'encyrpt_assertions', 'production', 'test',
                  'saml_product', 'autoupdate_idp_metadata', 'application_portfolio', 'notes', 'admin_notes']
        help_texts = {
            'entity_id': _('Should be URI including scheme, hostname of your application and path e.g. https://test.helsinki.fi/sp. <div class="text-danger">Required for both production and test use.</div>'),
            'name_fi': _('Short and descriptive name for the service in Finnish. <div class="text-danger">Required for both production and test use.</div>'),
            'name_en': _('Short and descriptive name for the service in English. <div class="text-danger">Required for both production and test use.</div>'),
            'name_sv': _('Short and descriptive name for the service in Swedish.'),
            'description_fi': _('Short (less than 140 characters) description of the service in Finnish. <div class="text-danger">Required for both production and test use.</div>'),
            'description_en': _('Short (less than 140 characters) description of the service in English. <div class="text-danger">Required for both production and test use.</div>'),
            'description_sv': _('Short (less than 140 characters) description of the service in Swedish.'),
            'privacypolicy_fi': _('Link to privacy policy in Finnish. Link must be publicly accessible. <div class="text-danger">Required for production use if the service requests any personal information.</div>'),
            'privacypolicy_en': _('Link to privacy policy in English. Link must be publicly accessible. <div class="text-danger">Required for production use if the service requests any personal information.</div>'),
            'privacypolicy_sv': _('Link to privacy policy in Swedish. Link must be publicly accessible.'),
            'login_page_url': _('Used for debugging and testing services.'),
            'discovery_service_url': _('For service providers supporting discovery service. Usually only valid if you are accepting logins for multiple IdPs.'),
            'name_format_transient': _('Support for transient name identifier format. Check <a href="https://wiki.shibboleth.net/confluence/display/CONCEPT/NameIdentifiers" target="_blank">Shibboleth wiki</a> for more information.'),
            'name_format_persistent': _('Support for persistent name identifier format. Check <a href="https://wiki.shibboleth.net/confluence/display/CONCEPT/NameIdentifiers" target="_blank">Shibboleth wiki</a> for more information.'),
            'sign_assertions': _('Sign SSO assertions. Defaults to False, do not change if you do not know what you are doing.'),
            'sign_requests': _('Sign SSO requests. Defaults to False, do not change if you do not know what you are doing.'),
            'sign_responses': _('Sign SSO responses. Defaults to True, do not change if you do not know what you are doing.'),
            'encyrpt_assertions': _('Encrypt SSO assertions. Defaults to True, do not change if you do not know what you are doing.'),
            'production': _('Publish this SP to production IdP. Only validated data is used.'),
            'test': _('Publish this SP to test IdP using unvalidated data.'),
            'saml_product': _('For administrative use e.g. for testing different SPs during IdP updates.'),
            'autoupdate_idp_metadata': _('Does this SP automatically update IdP metadata?'),
            'application_portfolio': _('Link to external application portfolio.'),
            'notes': _('Additional notes about this service.'),
            'admin_notes': _('Additional administrative notes. Writable only by registry admins but showed in summary to SP admins.'),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BasicInformationForm, self).__init__(*args, **kwargs)
        if not self.request.user.is_superuser:
            del self.fields['admin_notes']

    def clean_entity_id(self):
        entity_id = self.cleaned_data['entity_id']
        if not self.request.user.is_superuser and "entity_id" in self.changed_data:
            url_validator = URLValidator()
            try:
                url_validator(entity_id)
            except ValidationError:
                raise ValidationError(_("Entity Id should be URI, please contact IdP admins if this is not possible."))
        if ServiceProvider.objects.filter(entity_id=entity_id, end_at=None, history=None).exclude(pk=self.instance.pk):
            raise ValidationError(_("Entity Id already exists"))
        return entity_id
