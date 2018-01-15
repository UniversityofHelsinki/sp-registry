from django.forms import Form, EmailField
from django.utils.translation import ugettext_lazy as _


class AdminForm(Form):
    """
    Form for sending email invites
    """
    email = EmailField(label=_('Email where invitation is sent'))
