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
                  'encyrpt_attribute_assertions', 'production', 'test', 'saml_product', 'autoupdate_idp_metadata', 'notes', 'admin_notes']
        help_texts = {
            'entity_id': _('Should be URI including scheme, hostname of your application and path e.g. https://test.helsinki.fi/sp'),
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
