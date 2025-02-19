import logging
import os
import re
import unicodedata
from datetime import timedelta

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

from rr.models.attribute import Attribute
from rr.models.nameidformat import NameIDFormat
from rr.models.oidc import GrantType, OIDCScope, ResponseType
from rr.models.organization import Organization
from rr.utils.notifications import admin_notification_modified_sp

logger = logging.getLogger(__name__)

BASIC_INFORMATION_FIELDS = [
    "name_fi",
    "name_en",
    "name_sv",
    "description_fi",
    "description_en",
    "description_sv",
    "privacypolicy_org",
    "privacypolicy_fi",
    "privacypolicy_en",
    "privacypolicy_sv",
    "login_page_url",
    "application_portfolio",
    "notes",
    "admin_notes",
    "organization",
]
BASIC_LINKED_FIELDS = ["admins", "admin_groups", "attributes", "contacts"]
SAML_TECHNICAL_FIELDS = [
    "entity_id",
    "discovery_service_url",
    "sign_assertions",
    "sign_requests",
    "sign_responses",
    "encrypt_assertions",
    "saml_subject_identifier",
    "force_mfa",
    "force_sha1",
    "force_nameidformat",
    "production",
    "test",
    "saml_product",
    "autoupdate_idp_metadata",
]
SAML_LINKED_FIELDS = ["certificates", "endpoints", "nameidformat"]
LDAP_TECHNICAL_FIELDS = [
    "uses_ldapauth",
    "server_names",
    "target_group",
    "service_account",
    "service_account_contact",
    "local_storage_users",
    "local_storage_passwords",
    "local_storage_passwords_info",
    "local_storage_groups",
    "production",
    "can_access_all_ldap_groups",
]
LDAP_LINKED_FIELDS = ["usergroups"]
OIDC_TECHNICAL_FIELDS = [
    "entity_id",
    "grant_types",
    "response_types",
    "application_type",
    "subject_identifier",
    "oidc_scopes",
    "token_endpoint_auth_method",
    "jwks_uri",
    "jwks",
    "production",
    "test",
    "saml_product",
    "autoupdate_idp_metadata",
]
OIDC_LINKED_FIELDS = ["grant_types", "oidc_scopes", "response_types", "redirecturis"]
META_FIELDS = ["modified", "created_at", "updated_at", "updated_by", "validated"]


def get_field_names(types):
    field_list = []
    if "basic" in types:
        field_list.extend(BASIC_INFORMATION_FIELDS)
    if "basic_linked" in types:
        field_list.extend(BASIC_LINKED_FIELDS)
    if "meta" in types:
        field_list.extend(META_FIELDS)
    if "saml" in types:
        field_list.extend(SAML_TECHNICAL_FIELDS)
    if "saml_linked" in types:
        field_list.extend(SAML_LINKED_FIELDS)
    if "ldap" in types:
        field_list.extend(LDAP_TECHNICAL_FIELDS)
    if "ldap_linked" in types:
        field_list.extend(LDAP_LINKED_FIELDS)
    if "oidc" in types:
        field_list.extend(OIDC_TECHNICAL_FIELDS)
    if "oidc_linked" in types:
        field_list.extend(OIDC_LINKED_FIELDS)
    return field_list


def get_fernet_instance():
    """Initializes Fernet instance for client secret encryption."""
    if hasattr(settings, "OIDC_CLIENT_SECRET_KEY") and settings.OIDC_CLIENT_SECRET_KEY:
        key = settings.OIDC_CLIENT_SECRET_KEY.encode()
        try:
            f = Fernet(key)
        # Invalid key value returns an exception of type Error.
        except Exception:
            logger.error("Invalid OIDC_CLIENT_SECRET_KEY.")
            f = None
    return f


def server_names_validator(server_names, error):
    """
    Validates server names list

    error: Raised error class
    """
    server_names_list = server_names.splitlines()
    pattern = re.compile(
        r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*"
        r"([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
    )
    for server_name in server_names_list:
        if not pattern.match(server_name):
            raise error(_("Invalid list of server names."))
    return server_names


class ServiceProvider(models.Model):
    """
    Stores a service provider, related to :model:`auth.User` and
    :model:`rr.Attribute` through :model:`rr.SPAttribute`
    """

    entity_id = models.CharField(max_length=255, verbose_name=_("Entity Id"))
    SERVICETYPECHOICES = (("saml", _("SAML / Shibboleth")), ("ldap", _("LDAP")), ("oidc", _("OIDC")))
    service_type = models.CharField(
        max_length=10, choices=SERVICETYPECHOICES, verbose_name=_("Service type (SAML/LDAP)")
    )

    # Basic information
    organization = models.ForeignKey(
        Organization, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_("Organization")
    )
    name_fi = models.CharField(
        max_length=140, blank=True, verbose_name=_("Service Name (Finnish)"), validators=[MaxLengthValidator(70)]
    )
    name_en = models.CharField(
        max_length=140, blank=True, verbose_name=_("Service Name (English)"), validators=[MaxLengthValidator(70)]
    )
    name_sv = models.CharField(
        max_length=140, blank=True, verbose_name=_("Service Name (Swedish)"), validators=[MaxLengthValidator(70)]
    )
    description_fi = models.CharField(
        max_length=140,
        blank=True,
        verbose_name=_("Service Description (Finnish)"),
        validators=[MaxLengthValidator(140)],
    )
    description_en = models.CharField(
        max_length=140,
        blank=True,
        verbose_name=_("Service Description (English)"),
        validators=[MaxLengthValidator(140)],
    )
    description_sv = models.CharField(
        max_length=140,
        blank=True,
        verbose_name=_("Service Description (Swedish)"),
        validators=[MaxLengthValidator(140)],
    )
    privacypolicy_org = models.BooleanField(default=False, verbose_name=_("Privacy Policy URLs from Organization"))
    privacypolicy_fi = models.URLField(max_length=255, blank=True, verbose_name=_("Privacy Policy URL (Finnish)"))
    privacypolicy_en = models.URLField(max_length=255, blank=True, verbose_name=_("Privacy Policy URL (English)"))
    privacypolicy_sv = models.URLField(max_length=255, blank=True, verbose_name=_("Privacy Policy URL (Swedish)"))
    login_page_url = models.URLField(max_length=255, blank=True, verbose_name=_("Service Login Page URL"))

    application_portfolio = models.URLField(max_length=255, blank=True, verbose_name=_("Application portfolio URL"))
    notes = models.TextField(blank=True, verbose_name=_("Additional notes"))
    admin_notes = models.TextField(blank=True, verbose_name=_("Admin notes"))

    # SAML Technical information
    discovery_service_url = models.URLField(max_length=255, blank=True, verbose_name=_("Discovery Service URL"))

    nameidformat = models.ManyToManyField(NameIDFormat, blank=True)

    sign_assertions = models.BooleanField(default=False, verbose_name=_("Sign SSO assertions"))
    sign_requests = models.BooleanField(default=False, verbose_name=_("Sign SSO requests"))
    sign_responses = models.BooleanField(default=True, verbose_name=_("Sign SSO responses"))
    encrypt_assertions = models.BooleanField(default=True, verbose_name=_("Encrypt SSO assertions"))
    force_mfa = models.BooleanField(default=False, verbose_name=_("Require MFA authentication"))
    force_sha1 = models.BooleanField(default=False, verbose_name=_("Use SHA-1 as signature algorithm"))
    force_nameidformat = models.BooleanField(default=False, verbose_name=_("Force use of specific nameIDFormat"))

    grant_types = models.ManyToManyField(
        GrantType,
        blank=True,
    )
    response_types = models.ManyToManyField(
        ResponseType,
        blank=True,
    )
    oidc_scopes = models.ManyToManyField(
        OIDCScope,
        blank=True,
    )

    encrypted_client_secret = models.TextField(blank=True, verbose_name=_("Client secret"))

    jwks_uri = models.URLField(max_length=255, blank=True, verbose_name=_("URL for the JSON Web Key Set"))

    jwks = models.TextField(blank=True, verbose_name=_("JSON Web Key Set"))

    APPLICATIONTYPES = (("web", _("web")), ("native", _("native")))
    application_type = models.CharField(
        default="web", max_length=8, choices=APPLICATIONTYPES, verbose_name=_("Application type")
    )

    SUBJECTIDENTIFIERS = (("public", _("public")), ("pairwise", _("pairwise")))
    subject_identifier = models.CharField(
        blank=True, max_length=8, choices=SUBJECTIDENTIFIERS, verbose_name=_("Subject identifier")
    )

    SAML_SUBJECTIDENTIFIERS = (
        ("none", _("none")),
        ("any", _("any")),
        ("pairwise-id", _("pairwise-id")),
        ("subject-id", _("subject-id")),
    )
    saml_subject_identifier = models.CharField(
        default="none", max_length=11, choices=SAML_SUBJECTIDENTIFIERS, verbose_name=_("Subject identifier")
    )

    TOKENENDPOINTAUTHMETHODS = (
        ("client_secret_basic", _("client_secret_basic")),
        ("client_secret_post", _("client_secret_post")),
        ("client_secret_jwt", _("client_secret_jwt")),
        ("private_key_jwt", _("private_key_jwt")),
        ("none", _("none")),
    )
    token_endpoint_auth_method = models.CharField(
        blank=True,
        max_length=19,
        choices=TOKENENDPOINTAUTHMETHODS,
        verbose_name=_("Token endpoint authentication method"),
    )

    admin_require_manual_configuration = models.BooleanField(
        default=False, verbose_name=_("This service requires manual configuration")
    )

    production = models.BooleanField(default=False, verbose_name=_("Publish to production servers"))
    test = models.BooleanField(default=False, verbose_name=_("Publish to test servers"))

    saml_product = models.CharField(max_length=255, blank=True, verbose_name=_("SAML product this service is using"))
    autoupdate_idp_metadata = models.BooleanField(
        default=False, verbose_name=_("SP updates IdP metadata automatically")
    )

    # LDAP Technical information
    uses_ldapauth = models.BooleanField(default=False, verbose_name=_("Does this service use the LDAPAuth proxy?"))
    server_names = models.TextField(blank=True, verbose_name=_("Server names (not IPs), one per line"))
    TARGETGROUPCHOICES = (
        ("internet", _("Internet")),
        ("university", _("University of Helsinki users")),
        ("restricted", _("Restricted user group")),
    )
    target_group = models.CharField(
        max_length=10, blank=True, choices=TARGETGROUPCHOICES, verbose_name=_("Target group for the service")
    )
    service_account = models.BooleanField(default=False, verbose_name=_("Does the service use a service account?"))
    service_account_contact = models.TextField(
        blank=True, verbose_name=_("Email address and phone number for delivering the service account credentials")
    )
    can_access_all_ldap_groups = models.BooleanField(
        default=False, verbose_name=_("Service requires access to all LDAP groups")
    )
    local_storage_users = models.BooleanField(
        default=False, verbose_name=_("Service stores a local copy of users and their information")
    )
    # Checking if user stores passwords so we can reject the application
    local_storage_passwords = models.BooleanField(
        default=False, verbose_name=_("Service stores a local copy of user passwords")
    )
    local_storage_passwords_info = models.TextField(
        blank=True, verbose_name=_("How is this service storing the saved passwords and why?")
    )
    local_storage_groups = models.BooleanField(
        default=False, verbose_name=_("Service stores a local copy of groups and group members")
    )

    # Attributes are linked through SPAttribute model to include reason and validation information
    attributes = models.ManyToManyField(Attribute, through="SPAttribute")
    admins = models.ManyToManyField(User, blank=True, related_name="admins")
    admin_groups = models.ManyToManyField(Group, blank=True, related_name="admin_groups")

    # Meta
    modified = models.BooleanField(default=True, verbose_name=_("Modified"))
    history = models.IntegerField(blank=True, null=True, verbose_name=_("History key"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Entry end time"))
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Updated by")
    )
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_("Validated on"))

    def display_identifier(self):
        """Returns an entity_id for SAML service and first server for
        LDAP service (or entity_id if servers are not defined)"""
        if self.service_type == "saml":
            return self.entity_id
        elif self.service_type == "ldap":
            return self.entity_id
        elif self.service_type == "oidc":
            return self.name()
        else:
            return None

    def name(self, lang=get_language()):
        """Returns name in given language (defaulting current language),
        or in priority order en->fi->sv if current is not available"""
        if lang == "fi" and self.name_fi:
            return self.name_fi
        elif lang == "sv" and self.name_sv:
            return self.name_sv
        else:
            if self.name_en:
                return self.name_en
            elif self.name_fi:
                return self.name_fi
            else:
                return self.name_sv

    def description(self, lang=get_language()):
        """Returns description in given language (defaulting current language),
        or in priority order en->fi->sv if current is not available"""
        if lang == "fi" and self.description_fi:
            return self.description_fi
        elif lang == "sv" and self.description_sv:
            return self.description_sv
        else:
            if self.description_en:
                return self.description_en
            elif self.description_fi:
                return self.description_fi
            else:
                return self.description_sv

    def privacypolicy(self, lang=get_language()):
        """Returns privacy policy url in given language (defaulting current language),
        or in priority order en->fi->sv if current is not available"""
        if lang == "fi" and self.privacypolicy_fi:
            return self.privacypolicy_fi
        elif lang == "sv" and self.privacypolicy_sv:
            return self.privacypolicy_sv
        else:
            if self.privacypolicy_en:
                return self.privacypolicy_en
            elif self.privacypolicy_fi:
                return self.privacypolicy_fi
            elif self.privacypolicy_sv:
                return self.privacypolicy_sv
        if self.privacypolicy_org:
            return self.organization.privacypolicy(lang=lang)
        return ""

    def __str__(self):
        return self.entity_id

    def _get_fields(self, types):
        """Returns a list of technical information field names on the instance."""
        fields = []
        for f in self._meta.fields:
            field_name = f.name
            # resolve picklists/choices, with get_xyz_display() function
            get_choice = "get_" + field_name + "_display"
            if hasattr(self, get_choice):
                value = getattr(self, get_choice)()
            else:
                try:
                    value = getattr(self, field_name)
                except AttributeError:
                    value = None
            # Skip fields in list
            field_list = get_field_names(types)
            if f.editable and f.name in field_list:
                fields.append(
                    {
                        "label": f.verbose_name,
                        "name": f.name,
                        "value": value,
                    }
                )
        return fields

    def get_basic_fields(self):
        """Returns a list of basic information field names on the instance."""
        return self._get_fields(types=["basic"])

    def get_saml_technical_fields(self):
        """Returns a list of SAML technical information field names on the instance."""
        return self._get_fields(types=["saml"])

    def get_ldap_technical_fields(self):
        """Returns a list of LDAP technical information field names on the instance."""
        return self._get_fields(types=["ldap"])

    def get_oidc_technical_fields(self):
        """Returns a list of OIDC technical information field names on the instance."""
        return self._get_fields(types=["oidc"])

    def get_client_secret(self):
        """Returns decrypted client secret in text."""
        if self.encrypted_client_secret:
            f = get_fernet_instance()
            if f:
                try:
                    return f.decrypt(self.encrypted_client_secret.encode()).decode()
                except TypeError:
                    return None
                except InvalidToken:
                    logger.error("Incorrect OIDC_CLIENT_SECRET_KEY.")
                    return _("Invalid decryption key, could not show the client secret.")
        return None

    def generate_client_secret(self):
        """Generates client secret and encrypts it to model field."""
        f = get_fernet_instance()
        if f:
            try:
                self.encrypted_client_secret = f.encrypt(("secret_" + os.urandom(16).hex()).encode()).decode()
            except TypeError:
                return None
            self.save()
            return self.encrypted_client_secret
        return None

    def _create_notification(self):
        services = ServiceProvider.objects.filter(end_at=None, modified=True).order_by("entity_id")
        in_production = []
        add_production = []
        remove_production = []
        in_test = []
        for service in services:
            history = ServiceProvider.objects.filter(history=service.pk).exclude(validated=None).last()
            if history and history.production and service.production:
                in_production.append(service.name() + " (" + service.entity_id + ")")
            elif history and history.production and not service.production:
                remove_production.append(service.name() + " (" + service.entity_id + ")")
            elif service.production and service.validated:
                in_production.append(service.name() + " (" + service.entity_id + ")")
            elif service.production:
                add_production.append(service.name() + " (" + service.entity_id + ")")
            if service.test:
                in_test.append(service.name() + " (" + service.entity_id + ")")
        modified_sp = self.name() + " (" + self.entity_id + ")"
        admin_notification_modified_sp(modified_sp, in_production, add_production, remove_production, in_test)

    def save_modified(self, *args, **kwargs):
        """Saves model and send notification if it was unmodified"""
        try:
            sp = ServiceProvider.objects.get(pk=self.pk)
        except ServiceProvider.DoesNotExist:
            sp = None
        if not sp or (sp.production and not sp.modified) or (sp.production != self.production):
            self.modified = True
            self.save()
            self._create_notification()
        else:
            self.save()


class SPAttribute(models.Model):
    """
    Stores information for SP attributes, related to :model:`rr.ServiceProvider`
    and :model:`rr.Attribute`
    """

    attribute = models.ForeignKey(Attribute, related_name="spattributes", on_delete=models.CASCADE)
    sp = models.ForeignKey(ServiceProvider, related_name="spattributes", on_delete=models.CASCADE)
    reason = models.CharField(max_length=255, verbose_name=_("Reason for the attribute requisition"))
    oidc_userinfo = models.BooleanField(default=False, verbose_name=_("Release from the userinfo endpoint"))
    oidc_id_token = models.BooleanField(default=False, verbose_name=_("Release in the ID Token"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Entry end time"))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_("Validated on"))

    class Meta:
        ordering = ["attribute__friendlyname"]

    @property
    @extend_schema_field(OpenApiTypes.STR)
    def status(self):
        if self.end_at and not self.validated or self.end_at and self.validated > self.end_at:
            return _("removed")
        elif self.end_at:
            return _("pending removal")
        elif not self.validated:
            return _("pending validation")
        elif self.updated_at > self.validated + timedelta(minutes=1):
            return _("update pending validation")
        else:
            return _("validated")


def ldap_entity_id_from_name(horribleunicodestring):
    """
    Creates an LDAP Entity ID from it's human language name that's probably a
    horribleunicode string.

    horribleunicodestring: Human language name

    return cleaned-up string containing only lowercase ascii characters and underscores
    """
    s = unicodedata.normalize("NFKD", horribleunicodestring).encode("ascii", "ignore")
    s = s.decode()
    s = re.sub(r"\.helsinki\.fi$", "", s)
    s = re.sub(r"[./|]", "_", s)
    s = re.sub(r"[\W]", "", s)
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


def random_oidc_client_id():
    """
    Creates unique and random hex32 client ID value for OIDC RP.
    """
    while True:
        client_id = "id_" + os.urandom(16).hex()
        sp = ServiceProvider.objects.filter(entity_id=client_id, end_at=None).first()
        if not sp:
            break
    return client_id
