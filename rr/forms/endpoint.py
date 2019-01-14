from django.core.validators import ValidationError
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from rr.models.endpoint import Endpoint


class EndpointForm(ModelForm):
    class Meta:
        model = Endpoint
        fields = ['type', 'binding', 'location', 'response_location', 'index', 'is_default']
        help_texts = {
            'response_location': _('Almost never used, leave empty if you do not know for sure.'),
            'index': _('Usually not used and is safe to leave empty.'),
            'is_default': _('Usually not used and is safe to leave empty.'),
            }

    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop('sp', None)
        super(EndpointForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        servicetype = cleaned_data.get("type")
        binding = cleaned_data.get("binding")
        location = cleaned_data.get("location")
        index = cleaned_data.get("index")
        is_default = cleaned_data.get("is_default")
        if Endpoint.objects.filter(sp=self.sp, type=servicetype, binding=binding, location=location,
                                   end_at=None).exists():
            raise ValidationError(_("Endpoint already exists"))
        elif index and Endpoint.objects.filter(sp=self.sp, type=servicetype, binding=binding,
                                               index=index, end_at=None).exists():
            raise ValidationError(_("Index already exists"))
        elif is_default and not index:
            raise ValidationError(_("Default endpoint must be indexed"))
        elif is_default and Endpoint.objects.filter(sp=self.sp, type=servicetype, binding=binding,
                                                    is_default=True, end_at=None).exists():
            raise ValidationError(_("Default endpoint already exists"))
