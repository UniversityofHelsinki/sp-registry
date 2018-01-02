from django.forms import ModelForm
from rr.models.contact import Contact


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = ['type', 'firstname', 'lastname', 'email']
