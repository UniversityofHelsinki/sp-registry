from django.forms import CheckboxSelectMultiple, MultipleChoiceField
from django.forms.fields import BooleanField
from django.forms.forms import Form
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField
from django.utils.translation import ugettext_lazy as _

from rr.models.email import Template
from rr.models.serviceprovider import ServiceProvider


class EmailSelectForm(Form):
    """
    Form for selecting email addresses
    """
    SERVICETYPECHOICES = (('saml', _('SAML / Shibboleth')),
                          ('ldap', _('LDAP')),
                          ('oidc', _('OIDC')))
    service_type = MultipleChoiceField(required=True, widget=CheckboxSelectMultiple,
                                       choices=SERVICETYPECHOICES)
    production_sp = BooleanField(required=False, help_text=_("Select production SPs."))
    test_sp = BooleanField(required=False, help_text=_("Select test SPs"))
    individual_sp = ModelMultipleChoiceField(
            queryset=ServiceProvider.objects.filter(end_at=None,
                                                    history=None).order_by('entity_id'),
            required=False, help_text=_("Select individual SPs"))
    admin_emails = BooleanField(required=False, help_text=_("Select admin emails"))
    technical_contacts = BooleanField(required=False, help_text=_("Select technical contacts"))
    support_contacts = BooleanField(required=False, help_text=_("Select support contacts"))
    administrative_contacts = BooleanField(required=False,
                                           help_text=_("Select administrative contacts"))
    template = ModelChoiceField(queryset=Template.objects.all(), required=False,
                                help_text=_('Select template if you want to send email'))
