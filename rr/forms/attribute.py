from django.db.models import Q
from django.forms import BooleanField, CharField, Form
from django.forms.widgets import TextInput
from django.utils.translation import gettext as _

from rr.models.attribute import Attribute
from rr.models.serviceprovider import SPAttribute


class AttributeForm(Form):
    """
    Generates form including all public attributes and gives reason when SP is using that argument
    Pass ServiceProvider object as argument
    """

    def create_help_text(self, field):
        if self.sp.service_type == "oidc":
            help_text = _("OIDC claim: ") + field.oidc_claim
        else:
            help_text = _("Name: ") + field.name
        if field.schemalink:
            schema_link = (
                "https://wiki.eduuni.fi/display/CSCHAKA/funetEduPersonSchema2dot2"
                "#funetEduPersonSchema2dot2-" + field.friendlyname
            )
            help_text = help_text + ' (<a target="_blank" href="' + schema_link + '">' + _("schema") + "</a>)"
        if self.is_admin and self.sp.service_type == "saml" and not field.public_saml:
            not_public_text = _("Not a public SAML attribute, might not be available for SAML services.")
            help_text = help_text + '<p class="text-danger">' + not_public_text + "</p>"
        if self.is_admin and self.sp.service_type == "ldap" and not field.public_ldap:
            not_public_text = _("Not a public LDAP attribute, might not be available from LDAP.")
            help_text = help_text + '<p class="text-danger">' + not_public_text + "</p>"
        if self.is_admin and self.sp.service_type == "oidc" and not field.public_oidc:
            not_public_text = _("Not a public OIDC attribute.")
            help_text = help_text + '<p class="text-danger">' + not_public_text + "</p>"
        return help_text

    def get_attributes(self):
        if self.is_admin:
            attributes = Attribute.objects.all().order_by("friendlyname")
        elif self.sp.service_type == "saml":
            attributes = Attribute.objects.filter(
                Q(public_saml=True) | Q(spattributes__sp=self.sp, spattributes__end_at=None)
            ).order_by("friendlyname")
        elif self.sp.service_type == "ldap":
            attributes = Attribute.objects.filter(
                Q(public_ldap=True) | Q(spattributes__sp=self.sp, spattributes__end_at=None)
            ).order_by("friendlyname")
        elif self.sp.service_type == "oidc":
            attributes = Attribute.objects.filter(
                Q(public_oidc=True) | Q(spattributes__sp=self.sp, spattributes__end_at=None)
            ).order_by("friendlyname")
        else:
            attributes = Attribute.objects.none()
        return attributes

    def set_initial_values(self, field):
        attribute = SPAttribute.objects.filter(sp=self.sp, attribute=field, end_at=None).first()
        if attribute:
            if attribute.validated:
                self.fields[field.friendlyname].widget = TextInput(attrs={"class": "is-valid"})
            else:
                self.fields[field.friendlyname].widget = TextInput(attrs={"class": "is-invalid"})
            self.fields[field.friendlyname].initial = attribute.reason
            if self.sp.service_type == "oidc":
                self.fields["extra_userinfo_" + field.friendlyname].initial = attribute.oidc_userinfo
                self.fields["extra_id_token_" + field.friendlyname].initial = attribute.oidc_id_token
            self.fields[field.friendlyname].widget = TextInput(attrs={"placeholder": ""})

    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop("sp")
        self.is_admin = kwargs.pop("is_admin")
        super(AttributeForm, self).__init__(*args, **kwargs)
        attributes = self.get_attributes()
        for field in attributes:
            if self.sp.service_type == "oidc" and not field.oidc_claim:
                continue
            help_text = self.create_help_text(field)
            self.fields[field.friendlyname] = CharField(
                label=field.friendlyname, max_length=256, required=False, help_text=help_text
            )
            if self.sp.service_type == "oidc":
                self.fields["extra_userinfo_" + field.friendlyname] = BooleanField(
                    label="Userinfo", required=False, help_text=_("Release from the userinfo endpoint")
                )
                self.fields["extra_id_token_" + field.friendlyname] = BooleanField(
                    label="ID Token", required=False, help_text=_("Release in the ID Token")
                )
            self.set_initial_values(field)
