from django.forms import Form, CharField
from rr.models.serviceprovider import SPAttribute
from rr.models.attribute import Attribute
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import TextInput


class AttributeForm(Form):
    """
    Generates form including all public attributes and gives reason when SP is using that argument
    Pass ServiceProvider object as argument
    """
    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop('sp')
        super(AttributeForm, self).__init__(*args, **kwargs)
        attributes = Attribute.objects.filter(public=True).order_by('name')
        for field in attributes:
            self.fields[field.friendlyname] = CharField(label=field.friendlyname, max_length=256, required=False, help_text=_("Name: ") + field.name)
            sp = SPAttribute.objects.filter(sp=self.sp, attribute=field, end_at=None).first()
            if sp:
                if sp.validated:
                    self.fields[field.friendlyname].widget = TextInput(attrs={'class': 'is-valid'})
                else:
                    self.fields[field.friendlyname].widget = TextInput(attrs={'class': 'is-invalid'})
                self.fields[field.friendlyname].initial = sp.reason
            else:
                self.fields[field.friendlyname].widget = TextInput(attrs={'placeholder': ''})
