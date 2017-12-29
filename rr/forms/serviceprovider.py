from django.forms import ModelForm
from rr.models.serviceprovider import ServiceProvider


class BasicInformationForm(ModelForm):
    class Meta:
        model = ServiceProvider
        fields = ['entity_id', 'name_fi', 'name_en', 'name_sv', 'description_fi', 'description_en', 'description_sv',
                  'privacypolicy_fi', 'privacypolicy_en', 'privacypolicy_sv',
                  'login_page_url', 'discovery_service_url', 'name_format_transient', 'name_format_persistent',
                  'encyrpt_attribute_assertions', 'production', 'test']
