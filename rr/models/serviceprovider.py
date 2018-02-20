from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, get_language
from rr.models.attribute import Attribute
from rr.models.organization import Organization
from django.core.validators import MaxLengthValidator
from rr.models.nameidformat import NameIDFormat


class ServiceProvider(models.Model):
    """
    Stores a service provider, related to :model:`auth.User` and
    :model:`rr.Attribute` through :model:`rr.SPAttribute`
    """
    entity_id = models.CharField(max_length=255, verbose_name=_('Entity Id'))
    organization = models.ForeignKey(Organization, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_('Organization'))
    name_fi = models.CharField(max_length=70, blank=True, verbose_name=_('Service Name (Finnish)'), validators=[MaxLengthValidator(70)])
    name_en = models.CharField(max_length=70, blank=True, verbose_name=_('Service Name (English)'), validators=[MaxLengthValidator(70)])
    name_sv = models.CharField(max_length=70, blank=True, verbose_name=_('Service Name (Swedish)'), validators=[MaxLengthValidator(70)])
    description_fi = models.CharField(max_length=140, blank=True, verbose_name=_('Service Description (Finnish)'),
                                      validators=[MaxLengthValidator(140)])
    description_en = models.CharField(max_length=140, blank=True, verbose_name=_('Service Description (English)'),
                                      validators=[MaxLengthValidator(140)])
    description_sv = models.CharField(max_length=140, blank=True, verbose_name=_('Service Description (Swedish)'),
                                      validators=[MaxLengthValidator(140)])
    privacypolicy_fi = models.URLField(max_length=255, blank=True, verbose_name=_('Privacy Policy URL (Finnish)'))
    privacypolicy_en = models.URLField(max_length=255, blank=True, verbose_name=_('Privacy Policy URL (English)'))
    privacypolicy_sv = models.URLField(max_length=255, blank=True, verbose_name=_('Privacy Policy URL (Swedish)'))
    login_page_url = models.URLField(max_length=255, blank=True, verbose_name=_('Service Login Page URL'))
    discovery_service_url = models.URLField(max_length=255, blank=True, verbose_name=_('Discovery Service URL'))

    nameidformat = models.ManyToManyField(NameIDFormat, blank=True)

    sign_assertions = models.BooleanField(default=False, verbose_name=_('Sign SSO assertions'))
    sign_requests = models.BooleanField(default=False, verbose_name=_('Sign SSO requests'))
    sign_responses = models.BooleanField(default=True, verbose_name=_('Sign SSO responses'))
    encrypt_assertions = models.BooleanField(default=True, verbose_name=_('Encrypt SSO assertions'))

    production = models.BooleanField(default=False, verbose_name=_('Publish to production servers'))
    test = models.BooleanField(default=False, verbose_name=_('Publish to test servers'))

    saml_product = models.CharField(max_length=255, blank=True, verbose_name=_('SAML product this service is using'))
    autoupdate_idp_metadata = models.BooleanField(default=False, verbose_name=_('Does SP automatically update IdP metadata?'))
    application_portfolio = models.URLField(max_length=255, blank=True, verbose_name=_('Application portfolio URL'))
    notes = models.TextField(blank=True, verbose_name=_('Additional notes'))
    admin_notes = models.TextField(blank=True, verbose_name=_('Admin notes'))

    # Attributes are linked through SPAttribute model to include reason and validation information
    attributes = models.ManyToManyField(Attribute, through='SPAttribute')
    admins = models.ManyToManyField(User, blank=True, related_name="admins")

    modified = models.BooleanField(default=True, verbose_name=_('Modified'))
    history = models.IntegerField(blank=True, null=True, verbose_name=_('History key'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Updated by'))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_('Validated on'))

    def name(self):
        if get_language() == "fi" and self.name_fi:
            return self.name_fi
        elif get_language() == "sv" and self.name_sv:
            return self.name_sv
        else:
            if self.name_en:
                return self.name_en
            elif self.name_fi:
                return self.name_fi
            else:
                return self.name_sv

    def description(self):
        if get_language() == "fi" and self.description_fi:
            return self.description_fi
        elif get_language() == "sv" and self.description_sv:
            return self.description_sv
        else:
            if self.description_en:
                return self.description_en
            elif self.description_fi:
                return self.description_fi
            else:
                return self.description_sv

    def __str__(self):
        return self.entity_id

    def get_all_fields(self):
        """Returns a list of all field names on the instance."""
        fields = []
        for f in self._meta.fields:
            fname = f.name
            # resolve choices, with get_xyz_display() function
            get_choice = 'get_'+fname+'_display'
            if hasattr(self, get_choice):
                value = getattr(self, get_choice)()
            else:
                try:
                    value = getattr(self, fname)
                except AttributeError:
                    value = None
            # only display fields with values and skip some fields entirely
            if f.editable and f.name not in ('id', 'end_at', 'history', 'validated', 'modified'):
                fields.append(
                  {
                   'label': f.verbose_name,
                   'name': f.name,
                   'value': value,
                  }
                )
        return fields

    def get_basic_fields(self):
        """Returns a list of all field names on the instance."""
        fields = []
        for f in self._meta.fields:
            fname = f.name
            # resolve choices, with get_xyz_display() function
            get_choice = 'get_'+fname+'_display'
            if hasattr(self, get_choice):
                value = getattr(self, get_choice)()
            else:
                try:
                    value = getattr(self, fname)
                except AttributeError:
                    value = None
            # only display fields with values and skip some fields entirely
            if f.editable and f.name not in ('id', 'end_at', 'history', 'validated', 'modified', 'updated_by', 'entity_id',
                                             'discovery_service_url', 'name_format_transient', 'name_format_persistent',
                                             'sign_assertions', 'sign_requests', 'sign_responses', 'encrypt_assertions',
                                             'production', 'test', 'saml_product', 'autoupdate_idp_metadata'):
                fields.append(
                  {
                   'label': f.verbose_name,
                   'name': f.name,
                   'value': value,
                  }
                )
        return fields

    def get_technical_fields(self):
        """Returns a list of all field names on the instance."""
        fields = []
        for f in self._meta.fields:

            fname = f.name
            # resolve picklists/choices, with get_xyz_display() function
            get_choice = 'get_'+fname+'_display'
            if hasattr(self, get_choice):
                value = getattr(self, get_choice)()
            else:
                try:
                    value = getattr(self, fname)
                except AttributeError:
                    value = None
            # Skip fields in list
            if f.editable and f.name not in ('id', 'end_at', 'history', 'validated', 'modified', 'updated_by', 'name_fi', 'name_en',
                                             'name_sv', 'description_fi', 'description_en', 'description_sv',
                                             'privacypolicy_fi', 'privacypolicy_en', 'privacypolicy_sv',
                                             'login_page_url', 'application_portfolio', 'notes', 'admin_notes' ,'organization'):
                fields.append(
                  {
                   'label': f.verbose_name,
                   'name': f.name,
                   'value': value,
                  }
                )
        return fields


class SPAttribute(models.Model):
    """
    Stores iformation for SP attributes, related to :model:`rr.ServiceProvider`
    and :model:`rr.Attribute`
    """
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    sp = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255, verbose_name=_('Reason for the attribute requisition'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_('Validated on'))

    class Meta:
        ordering = ["attribute__friendlyname"]
