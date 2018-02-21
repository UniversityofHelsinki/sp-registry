from django.forms import Form, Textarea, HiddenInput
from django.utils.translation import ugettext as _
from django.forms.fields import CharField, BooleanField
from lxml import etree
from django.core.exceptions import ValidationError
from rr.models.serviceprovider import ServiceProvider
from django.core.validators import URLValidator


class MetadataForm(Form):
    """
    Form for importing metadata.
    """
    metadata = CharField(widget=Textarea,
                         help_text=_("Service Provider metadata"))
    disable_checks = BooleanField(required=False, help_text=_("Disable checks for Endpoint bindings"))
    validate = BooleanField(required=False, help_text=_("Validate imported metadata"))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(MetadataForm, self).__init__(*args, **kwargs)
        if not self.user.is_superuser:
            del self.fields['disable_checks']
            del self.fields['validate']

    def clean(self):
        cleaned_data = super().clean()
        metadata = cleaned_data.get("metadata")
        parser = etree.XMLParser(ns_clean=True, remove_comments=True, remove_blank_text=True)
        try:
            root = etree.fromstring(metadata, parser)
        except etree.XMLSyntaxError as e:
            raise ValidationError(_("Not valid XML: " + str(e)))
        if root.tag != "EntityDescriptor":
            raise ValidationError(_("First element should be EntityDescriptor"))
        entity_id = root.get("entityID") 
        if not entity_id:
            raise ValidationError(_("Could not find entityID"))
        if not self.user.is_superuser:
            url_validator = URLValidator()
            try:
                url_validator(entity_id)
            except ValidationError:
                raise ValidationError(_("Entity Id should be URI, please contact IdP admins if this is not possible."))
        if ServiceProvider.objects.filter(entity_id=entity_id, end_at=None, history=None):
            raise ValidationError(_("Entity Id already exists"))


class MetadataCommitForm(Form):
    """
    Form for committing metadata.
    """
    commit_message = CharField(initial='Metadata update', help_text=_("Commit message"))
    diff_hash = CharField()

    def __init__(self, *args, **kwargs):
        self.diff_hash = kwargs.pop('diff_hash', None)
        super(MetadataCommitForm, self).__init__(*args, **kwargs)
        self.fields['diff_hash'].widget = HiddenInput()
        self.fields['diff_hash'].initial = self.diff_hash
