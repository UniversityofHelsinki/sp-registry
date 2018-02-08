from django.forms import Form, EmailField
from django.utils.translation import ugettext as _


class SPAdminForm(Form):
    """
    Form for sending email invites
    """
    email = EmailField(label=_('Email where invitation is sent'))
