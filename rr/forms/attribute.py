from django.forms import Form, CharField
from rr.models.serviceprovider import SPAttribute
from rr.models.attribute import Attribute
from django.forms.widgets import TextInput


class AttributeForm(Form):
    """
    Generates form including all public attributes and gives reason when SP is using that argument
    Pass ServiceProvider object as argument
    """
    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop('sp')
        super(AttributeForm, self).__init__(*args, **kwargs)
        attributes = Attribute.objects.filter(public=True).order_by('friendlyname')
        for field in attributes:
            if field.schemalink:
                help_text = '<a target="_blank" href="https://wiki.eduuni.fi/display/CSCHAKA/funetEduPersonSchema2dot2#funetEduPersonSchema2dot2-' + field.friendlyname + '">' + field.name + '</a>'
            else:
                help_text = field.name
            self.fields[field.friendlyname] = CharField(label=field.friendlyname, max_length=256, required=False, help_text=help_text)
            attribute = SPAttribute.objects.filter(sp=self.sp, attribute=field, end_at=None).first()
            if attribute:
                if attribute.validated:
                    self.fields[field.friendlyname].widget = TextInput(attrs={'class': 'is-valid'})
                else:
                    self.fields[field.friendlyname].widget = TextInput(attrs={'class': 'is-invalid'})
                self.fields[field.friendlyname].initial = attribute.reason
            else:
                self.fields[field.friendlyname].widget = TextInput(attrs={'placeholder': ''})
