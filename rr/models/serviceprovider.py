from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _, get_language

from rr.models.attribute import Attribute
from rr.models.nameidformat import NameIDFormat
from rr.models.organization import Organization
from rr.utils.notifications import admin_notification_modified_sp

import unicodedata
import re


class ServiceProvider(models.Model):
    """
    Stores a service provider, related to :model:`auth.User` and
    :model:`rr.Attribute` through :model:`rr.SPAttribute`
    """
    entity_id = models.CharField(max_length=255, verbose_name=_('Entity Id'))
    SERVICETYPECHOICES = (('saml', _('SAML / Shibboleth')),
                          ('ldap', _('LDAP')))
    service_type = models.CharField(max_length=10, choices=SERVICETYPECHOICES,
                                    verbose_name=_('Service type (SAML/LDAP)'))

    # Basic information
    organization = models.ForeignKey(Organization, blank=True, null=True,
                                     on_delete=models.SET_NULL, verbose_name=_('Organization'))
    name_fi = models.CharField(max_length=140, blank=True,
                               verbose_name=_('Service Name (Finnish)'),
                               validators=[MaxLengthValidator(70)])
    name_en = models.CharField(max_length=140, blank=True,
                               verbose_name=_('Service Name (English)'),
                               validators=[MaxLengthValidator(70)])
    name_sv = models.CharField(max_length=140, blank=True,
                               verbose_name=_('Service Name (Swedish)'),
                               validators=[MaxLengthValidator(70)])
    description_fi = models.CharField(max_length=140, blank=True,
                                      verbose_name=_('Service Description (Finnish)'),
                                      validators=[MaxLengthValidator(140)])
    description_en = models.CharField(max_length=140, blank=True,
                                      verbose_name=_('Service Description (English)'),
                                      validators=[MaxLengthValidator(140)])
    description_sv = models.CharField(max_length=140, blank=True,
                                      verbose_name=_('Service Description (Swedish)'),
                                      validators=[MaxLengthValidator(140)])
    privacypolicy_fi = models.URLField(max_length=255, blank=True,
                                       verbose_name=_('Privacy Policy URL (Finnish)'))
    privacypolicy_en = models.URLField(max_length=255, blank=True,
                                       verbose_name=_('Privacy Policy URL (English)'))
    privacypolicy_sv = models.URLField(max_length=255, blank=True,
                                       verbose_name=_('Privacy Policy URL (Swedish)'))
    login_page_url = models.URLField(max_length=255, blank=True,
                                     verbose_name=_('Service Login Page URL'))

    application_portfolio = models.URLField(max_length=255, blank=True,
                                            verbose_name=_('Application portfolio URL'))
    notes = models.TextField(blank=True, verbose_name=_('Additional notes'))
    admin_notes = models.TextField(blank=True, verbose_name=_('Admin notes'))

    # SAML Technical information
    discovery_service_url = models.URLField(max_length=255, blank=True,
                                            verbose_name=_('Discovery Service URL'))

    nameidformat = models.ManyToManyField(NameIDFormat, blank=True)

    sign_assertions = models.BooleanField(default=False, verbose_name=_('Sign SSO assertions'))
    sign_requests = models.BooleanField(default=False, verbose_name=_('Sign SSO requests'))
    sign_responses = models.BooleanField(default=True, verbose_name=_('Sign SSO responses'))
    encrypt_assertions = models.BooleanField(default=True,
                                             verbose_name=_('Encrypt SSO assertions'))

    production = models.BooleanField(default=False,
                                     verbose_name=_('Publish to production servers'))
    test = models.BooleanField(default=False, verbose_name=_('Publish to test servers'))

    saml_product = models.CharField(max_length=255, blank=True,
                                    verbose_name=_('SAML product this service is using'))
    autoupdate_idp_metadata = models.BooleanField(
        default=False,
        verbose_name=_('SP updates IdP metadata automatically'))

    # LDAP Technical information
    server_names = models.TextField(blank=True,
                                    verbose_name=_('Server names (not IPs), one per line'))
    TARGETGROUPCHOICES = (('internet', _('Internet')),
                          ('university', _('University of Helsinki users')),
                          ('restricted', _('Restricted user group')))
    target_group = models.CharField(max_length=10, blank=True, choices=TARGETGROUPCHOICES,
                                    verbose_name=_('Target group for the service'))
    service_account = models.BooleanField(default=False,
                                          verbose_name=_('Does the service use a service account?'))
    service_account_contact = models.TextField(blank=True,
                                               verbose_name=_('Email address and phone number for delivering the service account credentials'))
    can_access_all_ldap_groups = models.BooleanField(default=False,
                                                     verbose_name=_('Service requires access to all LDAP groups'))
    local_storage_users = models.BooleanField(default=False,
                                              verbose_name=_('Service stores a local copy of users and their information'))
    # Checking if user stores passwords so we can reject the application
    local_storage_passwords = models.BooleanField(default=False,
                                                  verbose_name=_('Service stores a local copy of user passwords'))
    local_storage_passwords_info = models.TextField(blank=True,
                                                    verbose_name=_('How is this service storing the saved passwords and why?'))
    local_storage_groups = models.BooleanField(default=False,
                                               verbose_name=_('Service stores a local copy of groups and group members'))

    # Attributes are linked through SPAttribute model to include reason and validation information
    attributes = models.ManyToManyField(Attribute, through='SPAttribute')
    admins = models.ManyToManyField(User, blank=True, related_name="admins")

    # Meta
    modified = models.BooleanField(default=True, verbose_name=_('Modified'))
    history = models.IntegerField(blank=True, null=True, verbose_name=_('History key'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name=_('Updated by'))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_('Validated on'))

    def display_identifier(self):
        """Returns an entity_id for SAML service and first server for LDAP service (or entity_id if servers are not defined)"""
        if self.service_type == "saml":
            return self.entity_id
        elif self.service_type == "ldap":
            return self.entity_id
        else:
            return None

    def name(self):
        """Returns name in current language, or in priority order
           en->fi->sv if current is not available"""
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
        """Returns description in current language, or in priority order
           en->fi->sv if current is not available"""
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
        """Returns a list of basic information field names on the instance."""
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
            if f.editable and f.name in ('name_fi', 'name_en',
                                         'name_sv', 'description_fi', 'description_en', 'description_sv',
                                         'privacypolicy_fi', 'privacypolicy_en', 'privacypolicy_sv',
                                         'login_page_url', 'application_portfolio', 'notes', 'admin_notes', 'organization'):
                fields.append(
                  {
                   'label': f.verbose_name,
                   'name': f.name,
                   'value': value,
                  }
                )
        return fields

    def get_technical_fields(self):
        """Returns a list of technical information field names on the instance."""
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
            if f.editable and f.name in ('entity_id', 'discovery_service_url', 'name_format_transient', 'name_format_persistent',
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

    def get_ldap_technical_fields(self):
        """Returns a list of LDAP technical information field names on the instance."""
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
            if f.editable and f.name in ('server_names', 'target_group', 'service_account', 'service_account_contact', 'local_storage_users',
                                         'local_storage_passwords', 'local_storage_passwords_info', 'local_storage_groups', 'production',
                                         'can_access_all_ldap_groups'):
                fields.append(
                  {
                   'label': f.verbose_name,
                   'name': f.name,
                   'value': value,
                  }
                )
        return fields

    def save_modified(self, *args, **kwargs):
        """ Saves model and send notification if it was unmodified """
        if self.modified and not self.production:
            self.save()
        else:
            self.modified = True
            self.save()
            services = ServiceProvider.objects.filter(end_at=None,
                                                      modified=True).order_by('entity_id')
            in_production = []
            add_production = []
            remove_production = []
            in_test = []
            for service in services:
                history = ServiceProvider.objects.filter(
                    history=service.pk).exclude(validated=None).last()
                if history and history.production and service.production:
                    in_production.append(service.entity_id)
                elif history and history.production and not service.production:
                    remove_production.append(service.entity_id)
                elif service.production and service.validated:
                    in_production.append(service.entity_id)
                elif service.production:
                    add_production.append(service.entity_id)
                if service.test:
                    in_test.append(service.entity_id)
            admin_notification_modified_sp(self.entity_id, in_production, add_production,
                                           remove_production, in_test)


class SPAttribute(models.Model):
    """
    Stores information for SP attributes, related to :model:`rr.ServiceProvider`
    and :model:`rr.Attribute`
    """
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    sp = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255,
                              verbose_name=_('Reason for the attribute requisition'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_('Validated on'))

    class Meta:
        ordering = ["attribute__friendlyname"]


def ldap_entity_id_from_name(horribleunicodestring):
    """
    Creates an LDAP Entity ID from it's human language name that's probably a
    horribleunicode string.

    horribleunicodestring: Human language name

    return cleaned-up string containing only lowercase ascii characters
    """
    s = unicodedata.normalize('NFKD', horribleunicodestring).encode('ascii', 'ignore')
    s = s.decode()
    s = re.sub(r"\.helsinki\.fi$", "", s)
    s = re.sub(r"[-,! ()\]\[{}]", "", s)
    s = re.sub(r"[./|]", "_", s)
    s = s.lower()

    return s


def new_ldap_entity_id_from_name(horribleunicodestring):
    """
    Creates an LDAP Entity ID from it's human language name that's probably a
    horribleunicode string. If an object with the same Entity ID already
    exists, returns the ID with a number appended, so that this will be a new
    Entity ID. Not thread safe or anything.

    horribleunicodestring: Human language name

    return cleaned-up string plus possibly a running number
    """
    entity_id = ldap_entity_id_from_name(horribleunicodestring)
    sp = ServiceProvider.objects.filter(entity_id=entity_id).first()
    n = 0
    while sp:
        n = n + 1
        entity_id = "%s%i" % (entity_id, n)
        sp = ServiceProvider.objects.filter(entity_id=entity_id).first()

    return entity_id
