from django.db.models import Q
from django.forms import Form, CharField
from django.forms.widgets import TextInput
from django.utils.translation import ugettext as _

from rr.models.attribute import Attribute
from rr.models.serviceprovider import SPAttribute


class AttributeForm(Form):
    """
    Generates form including all public attributes and gives reason when SP is using that argument
    Pass ServiceProvider object as argument
    """
    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop('sp')
        self.is_admin = kwargs.pop('is_admin')
        super(AttributeForm, self).__init__(*args, **kwargs)
        if self.is_admin:
            attributes = Attribute.objects.all().order_by('friendlyname')
        else:
            attributes = Attribute.objects.filter(Q(public=True) | Q(
                    spattribute__sp=self.sp, spattribute__end_at=None)).order_by('friendlyname')
        for field in attributes:
            if field.schemalink:
                schema_link = "https://wiki.eduuni.fi/display/CSCHAKA/funetEduPersonSchema2dot2" \
                             "#funetEduPersonSchema2dot2-" + field.friendlyname
                help_text = '<a target="_blank" href="' + schema_link + '">' + field.name + '</a>'
            else:
                help_text = field.name
            if self.is_admin and not field.public:
                not_public_text = _('Not a public attribute')
                help_text = help_text + '<p class="text-danger">' + not_public_text + '</p>'
            self.fields[field.friendlyname] = CharField(label=field.friendlyname, max_length=256,
                                                        required=False, help_text=help_text)
            attribute = SPAttribute.objects.filter(sp=self.sp, attribute=field,
                                                   end_at=None).first()
            if attribute:
                if attribute.validated:
                    self.fields[field.friendlyname].widget = TextInput(
                        attrs={'class': 'is-valid'})
                else:
                    self.fields[field.friendlyname].widget = TextInput(
                        attrs={'class': 'is-invalid'})
                self.fields[field.friendlyname].initial = attribute.reason
            else:
                self.fields[field.friendlyname].widget = TextInput(attrs={'placeholder': ''})
