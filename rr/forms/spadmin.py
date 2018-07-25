from django.forms import Form, EmailField, ModelChoiceField
from django.utils.translation import ugettext as _

from rr.models.email import Template


class SPAdminForm(Form):
    """
    Form for sending email invites
    """
    email = EmailField(label=_('Email where invitation is sent'))
    template = ModelChoiceField(queryset=Template.objects.all(), required=False,
                                help_text=_('Using default template if none given.'))

    def __init__(self, *args, **kwargs):
        """
        Only show admin_notes field for superusers
        """
        self.superuser = kwargs.pop('superuser', False)
        super(SPAdminForm, self).__init__(*args, **kwargs)
        if not self.superuser:
            del self.fields['template']
