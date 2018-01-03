from django.forms import Form, CharField
from rr.models.attribute import Attribute
from rr.models.serviceprovider import SPAttribute
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import TextInput


class AttributeForm(Form):
    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop('sp')
        super(AttributeForm, self).__init__(*args, **kwargs)
        attributes = Attribute.objects.filter(public=True)
        for field in attributes:
            self.fields[field.name] = CharField(max_length=256, required=False, help_text=_("OID: ") + field.oid)
            sp = SPAttribute.objects.filter(sp=self.sp, attribute=field).first()
            if sp:
                self.fields[field.name].widget = TextInput(attrs={'class': 'is-valid'})
                self.fields[field.name].initial = sp.reason
            else:
                self.fields[field.name].widget = TextInput(attrs={'class': 'is-invalid'})
