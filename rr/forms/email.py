from django.utils.translation import ugettext as _
from django.forms.fields import BooleanField, MultipleChoiceField
from django.forms.forms import Form
from rr.models.serviceprovider import ServiceProvider
from rr.models.email import Template
from django.forms.models import ModelChoiceField


class EmailSelectForm(Form):
    """
    Form for selecting email addresses
    """
    production_sp = BooleanField(required=False, help_text=_("Select production SPs."))
    test_sp = BooleanField(required=False, help_text=_("Select test SPs"))
    SP_CHOICES = [[x.id, x] for x in ServiceProvider.objects.filter(end_at=None, history=None).order_by('entity_id')]
    individual_sp = MultipleChoiceField(choices=SP_CHOICES, required=False, help_text=_("Select individual SPs"))
    admin_emails = BooleanField(required=False, help_text=_("Select admin emails"))
    technical_contacts = BooleanField(required=False, help_text=_("Select technical contacts"))
    support_contacts = BooleanField(required=False, help_text=_("Select support contacts"))
    administrative_contacts = BooleanField(required=False, help_text=_("Select administrative contacts"))
    template = ModelChoiceField(queryset=Template.objects.all(), required=False, help_text=_('Select template if you want to send email'))
