import re

from django.core.validators import ValidationError
from django.forms import CharField, Form, EmailField, ModelChoiceField
from django.utils.translation import ugettext_lazy as _

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


class SPAdminGroupForm(Form):
    """
    Form for adding admin groups
    """
    group = CharField(label=_('Group name'),
                      help_text=_('6-32 characters, allowed characters are [a-z0-9-]. May not start or end with "-".'))

    def clean_group(self):
        group = self.cleaned_data['group']
        if len(group) < 7:
            raise ValidationError(_("Minimum length 6 characters."))
        if len(group) > 32:
            raise ValidationError(_("Maximum length 32 characters."))
        pattern = re.compile("^([a-z0-9])([a-z0-9-])*([a-z0-9])$")
        if not pattern.match(group):
            raise ValidationError(_("Invalid characters in group name."))
        return group
