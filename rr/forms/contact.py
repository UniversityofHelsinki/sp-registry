from django.forms import ModelForm
from rr.models.contact import Contact
from django.core.validators import ValidationError
from django.utils.translation import ugettext as _


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = ['type', 'firstname', 'lastname', 'email']

    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop('sp', None)
        super(ContactForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        contacttype = cleaned_data.get("type")
        firstname = cleaned_data.get("firstname")
        lastname = cleaned_data.get("lastname")
        email = cleaned_data.get("email")
        if Contact.objects.filter(sp=self.sp, type=contacttype, firstname=firstname, lastname=lastname, email=email, end_at=None).exists():
            raise ValidationError(_("Contact already exists"))
