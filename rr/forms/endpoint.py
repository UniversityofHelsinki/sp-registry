from django.forms import ModelForm
from rr.models.endpoint import Endpoint


class EndpointForm(ModelForm):
    class Meta:
        model = Endpoint
        fields = ['type', 'binding', 'url']
