from django.forms import ModelForm
from rr.models.endpoint import Endpoint
from django.core.validators import ValidationError
from django.utils.translation import ugettext as _


class EndpointForm(ModelForm):
    class Meta:
        model = Endpoint
        fields = ['type', 'binding', 'url', 'index']

    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop('sp', None)
        super(EndpointForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        servicetype = cleaned_data.get("type")
        binding = cleaned_data.get("binding")
        location = cleaned_data.get("url")
        index = cleaned_data.get("index")
        if Endpoint.objects.filter(sp=self.sp, type=servicetype, binding=binding, url=location, index=index, end_at=None).exists():
            raise ValidationError(_("Endpoint already exists"))
