import json
import re

from django.core.validators import ValidationError
from django.db.models import Q
from django.forms import BooleanField, Form, ModelForm
from django.forms.fields import CharField
from django.forms.widgets import CheckboxInput, HiddenInput, Textarea
from django.utils.translation import gettext_lazy as _

from rr.models.nameidformat import NameIDFormat
from rr.models.serviceprovider import (
    ServiceProvider,
    ldap_entity_id_from_name,
    random_oidc_client_id,
    server_names_validator,
)
from rr.utils.missing_data import get_missing_sp_data


class BasicInformationForm(ModelForm):
    """
    Form for updating basic information from ServiceProvider object
    """

    class Meta:
        model = ServiceProvider
        fields = [
            "organization",
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
        ]
        help_texts = {
            "organization": _("Organization who is responsible for the data given to the service."),
            "name_fi": _(
                "Short (max 70 characters) and descriptive name for the service "
                'in Finnish.<div class="text-danger">'
                "Required for both production and test use.</div>"
            ),
            "name_en": _(
                "Short (max 70 characters) and descriptive name for the service "
                'in English.<div class="text-danger">'
                "Required for both production and test use.</div>"
            ),
            "name_sv": _("Short (max 70 characters) and descriptive name for the service in Swedish."),
            "description_fi": _(
                "Short (max 140 characters) description of the service "
                'in Finnish. <div class="text-danger">'
                "Required for both production and test use.</div>"
            ),
            "description_en": _(
                "Short (max 140 characters) description of the service "
                'in English. <div class="text-danger">'
                "Required for both production and test use.</div>"
            ),
            "description_sv": _("Short (max 140 characters) description of the service in Swedish."),
            "privacypolicy_org": _(
                "Get privacy policy URLs from the organization if such are "
                'set. <div class="text-danger">This or privacy policy URLs '
                "below are required for production use, if service requests "
                "any user information.</div>"
            ),
            "privacypolicy_fi": _("Link to privacy policy in Finnish. Link must be publicly accessible."),
            "privacypolicy_en": _("Link to privacy policy in English. Link must be publicly accessible."),
            "privacypolicy_sv": _("Link to privacy policy in Swedish. Link must be publicly accessible."),
            "login_page_url": _("Used for debugging and testing services."),
            "application_portfolio": _("Link to external application portfolio."),
            "notes": _("Additional notes about this service."),
            "admin_notes": _(
                "Additional administrative notes. Writable only by registry admins "
                "but showed in summary to SP admins."
            ),
        }

    def __init__(self, *args, **kwargs):
        """
        Only show admin_notes field for superusers
        """
        self.request = kwargs.pop("request", None)
        super(BasicInformationForm, self).__init__(*args, **kwargs)
        if not self.request.user.is_superuser:
            del self.fields["admin_notes"]

    def clean(self):
        """
        Check that name is given in English or in Finnish
        """
        name_en = self.cleaned_data["name_en"]
        name_fi = self.cleaned_data["name_fi"]
        if not name_en and not name_fi:
            raise ValidationError(_("Name in English or in Finnish is required."))
        organization = self.cleaned_data["organization"]
        privacypolicy_org = self.cleaned_data["privacypolicy_org"]
        if privacypolicy_org:
            if not organization:
                raise ValidationError(_("Select organization to use privacy policy URLs from organization."))
            if not organization.privacypolicy():
                raise ValidationError(
                    _(
                        "Selected organization does not have privacy policy URLs defined. "
                        "You cannot user privacy policy URLs from organization."
                    )
                )


class SamlTechnicalInformationForm(ModelForm):
    """
    Form for updating SAML technical information from ServiceProvider object
    """

    class Meta:
        model = ServiceProvider
        fields = [
            "entity_id",
            "discovery_service_url",
            "nameidformat",
            "sign_assertions",
            "sign_requests",
            "sign_responses",
            "encrypt_assertions",
            "saml_subject_identifier",
            "force_mfa",
            "force_sha1",
            "force_nameidformat",
            "admin_require_manual_configuration",
            "production",
            "test",
            "saml_product",
            "autoupdate_idp_metadata",
        ]
        help_texts = {
            "entity_id": _(
                "Should be URI including scheme, hostname of your application and path "
                'e.g. https://test.helsinki.fi/sp. <div class="text-danger">'
                "Required for both production and test use.</div>"
            ),
            "discovery_service_url": _(
                "For service providers supporting discovery service. "
                "Usually only valid if you are accepting logins for "
                "multiple IdPs."
            ),
            "nameidformat": _(
                'Support for name identifier formats. Check <a href="'
                "https://wiki.shibboleth.net/confluence/display/CONCEPT/NameIdentifiers"
                '" target="_blank">Shibboleth wiki</a> for more information.'
            ),
            "sign_assertions": _(
                "IdP sings attribute assertions sent to SP. Defaults to False "
                "because assertions are encrypted by default."
            ),
            "sign_requests": _("IdP requires signed authentication requests from this SP."),
            "sign_responses": _("IdP signs responses sent to SP. Defaults to True and should not be changed."),
            "encrypt_assertions": _(
                "IdP encrypts attribute assertions sent to SP. Defaults to "
                "True. Do not change unless you are using a SP that does "
                "not support encryption."
            ),
            "force_mfa": _(
                "MFA authentication is required for all users. If set here, service "
                "must not require specific authentication context class as it will "
                "trigger an error."
            ),
            "force_sha1": _(
                "Forces using of SHA-1 algorithm in signatures. Default is SHA-256. "
                "Should not be used unless using old SAML software which does not support "
                "SHA-256."
            ),
            "force_nameidformat": _(
                "This service provider requires the specific NameIdFormat. If set, "
                "only one NameIdFormat must be chosen in the list above. "
                "Do not set if you do not know what this means, as this is almost newer "
                "required."
            ),
            "admin_require_manual_configuration": _(
                "This service provider requires manual configuration. Set by registry admins if necessary."
            ),
            "production": _(
                "Publish this SP to the production IdP. Only validated data is used. "
                "Any changes to production SPs must be validated by the IdP "
                "administrators before coming into effect."
                '<div class="text-danger">Required for production use.</div>'
            ),
            "test": _(
                "Publish this SP to the test IdP using unvalidated data. "
                "Any changes might take up to 10 minutes until they are published to "
                "the test IdP."
            ),
            "saml_product": _("For administrative use e.g. for testing different SPs during IdP updates."),
            "autoupdate_idp_metadata": _("Does this SP automatically update IdP metadata at least once a day?"),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(SamlTechnicalInformationForm, self).__init__(*args, **kwargs)
        # Show missing fields
        missing = get_missing_sp_data(self.instance)
        if missing:
            warning = _("Following parameters are missing for production use: ")
            self.fields["production"].help_text += (
                '<div class="text-danger">' + str(warning) + "<br>" + str("<br>".join(missing)) + "</div>"
            )
        if not self.request.user.is_superuser:
            # Disable production if missing fields
            if missing and not self.instance.production:
                self.fields["production"].widget.attrs["disabled"] = True
            # Limit choices to public and current values
            self.fields["nameidformat"].queryset = NameIDFormat.objects.filter(
                Q(public=True) | Q(pk__in=self.instance.nameidformat.all())
            )
            del self.fields["admin_require_manual_configuration"]

    def clean_entity_id(self):
        """
        Allow only superusers set entity id something else than URL.
        """
        entity_id = self.cleaned_data["entity_id"]
        if not self.request.user.is_superuser and "entity_id" in self.changed_data and ":" not in entity_id:
            raise ValidationError(_("Entity Id should be URI, please contact IdP admins if this is not possible."))
        if ServiceProvider.objects.filter(entity_id=entity_id, end_at=None, history=None).exclude(pk=self.instance.pk):
            raise ValidationError(_("Entity Id already exists"))
        return entity_id


class LdapTechnicalInformationForm(ModelForm):
    """
    Form for updating LDAP technical information from ServiceProvider object
    """

    class Meta:
        model = ServiceProvider
        fields = [
            "uses_ldapauth",
            "server_names",
            "target_group",
            "service_account",
            "service_account_contact",
            "can_access_all_ldap_groups",
            "local_storage_users",
            "local_storage_passwords",
            "local_storage_passwords_info",
            "local_storage_groups",
            "admin_require_manual_configuration",
            "production",
        ]
        widgets = {
            "service_account_contact": Textarea(attrs={"rows": 2}),
            "local_storage_passwords_info": Textarea(attrs={"rows": 5}),
            "service_account": CheckboxInput(attrs={"data-bs-toggle": "collapse", "href": "#serviceAccountCollapse"}),
            "local_storage_passwords": CheckboxInput(
                attrs={"data-bs-toggle": "collapse", "href": "#localPasswordCollapse"}
            ),
        }
        help_texts = {
            "uses_ldapauth": _(
                "Does this service use the LDAPAuth proxy in order to access "
                "user and group data for authentication and access control?"
            ),
            "server_names": _("Full server names (not IPs), separated by space. User for access control."),
            "target_group": _("What is the target group (users) of this service?"),
            "service_account": _("Separate service account is used for LDAP queries (recommended way)."),
            "service_account_contact": _(
                "Email and phone number for delivering service account "
                "credentials. Use a firstname.lastname@helsinki.fi "
                "address and the same person's mobile phone in "
                "non-international format, that is, start it with 0. "
                "Separete the email and phone number by space."
            ),
            "can_access_all_ldap_groups": _("Service requires access to all LDAP groups."),
            "local_storage_users": _(
                "Service stores all users and released attributes locally. "
                "If you only save user data when user logs in, do not check "
                "this."
            ),
            "local_storage_passwords": _("Service stores user passwords locally."),
            "local_storage_passwords_info": _(
                "Why is this service storing user passwords locally and how? This is not generally a good idea."
            ),
            "local_storage_groups": _("Service stores requested groups and their member lists locally."),
            "admin_require_manual_configuration": _(
                "This service provider requires manual configuration. Set by registry admins if necessary."
            ),
            "production": _("Publish this service to LDAP production servers."),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(LdapTechnicalInformationForm, self).__init__(*args, **kwargs)
        # Show missing fields
        missing = get_missing_sp_data(self.instance)
        if missing:
            warning = _("Following parameters are missing for production use: ")
            self.fields["production"].help_text += (
                '<div class="text-danger">' + str(warning) + "<br>" + str("<br>".join(missing)) + "</div>"
            )
        if not self.request.user.is_superuser:
            # Disable production if missing fields
            if missing and not self.instance.production:
                self.fields["production"].widget.attrs["disabled"] = True
            del self.fields["admin_require_manual_configuration"]

    def clean_server_names(self):
        """
        Check server names format
        """
        server_names = self.cleaned_data["server_names"]
        server_names_validator(server_names, ValidationError)
        return server_names

    def clean_service_account_contact(self):
        """
        Check service account contact format
        """
        service_account_contact = self.cleaned_data["service_account_contact"]
        pattern = re.compile(r"^($|[-a-z.]+@helsinki.fi 0\d+)", re.I)
        if not self.request.user.is_superuser and not pattern.match(service_account_contact):
            raise ValidationError(_("Invalid service account contact."))
        if self.request.user.is_superuser:
            pattern = re.compile(r"^($|[-a-z.]+@[-a-z.]+ 0\d+)", re.I)
            if not pattern.match(service_account_contact):
                raise ValidationError(_("Invalid service account contact."))
        return service_account_contact

    def clean(self):
        cleaned_data = super().clean()
        service_account = cleaned_data.get("service_account")
        service_account_contact = cleaned_data.get("service_account_contact")
        local_storage_passwords = cleaned_data.get("local_storage_passwords")
        local_storage_passwords_info = cleaned_data.get("local_storage_passwords_info")
        if service_account and not service_account_contact:
            self.add_error("service_account_contact", "Please give contact information.")
        if local_storage_passwords and not local_storage_passwords_info:
            self.add_error("local_storage_passwords_info", "Please give a reason for saving passwords.")


class OidcTechnicalInformationForm(ModelForm):
    """
    Form for updating technical information from OIDC ServiceProvider object
    """

    reset_client_secret = BooleanField(label=_("Reset client secret"), required=False)
    remove_client_secret = BooleanField(label=_("Remove client secret"), required=False)

    class Meta:
        model = ServiceProvider
        fields = [
            "entity_id",
            "admin_require_manual_configuration",
            "grant_types",
            "response_types",
            "oidc_scopes",
            "application_type",
            "subject_identifier",
            "token_endpoint_auth_method",
            "jwks_uri",
            "jwks",
            "production",
            "test",
            "saml_product",
            "autoupdate_idp_metadata",
        ]
        help_texts = {
            "entity_id": _(
                "Client identifier of the relying party. "
                "It is usually recommended to use random identifier. "
                '<div class="text-danger">Required for both production and test use.</div>'
            ),
            "admin_require_manual_configuration": _(
                "This service provider requires manual configuration. Set by registry admins if necessary."
            ),
            "grant_types": _("Grant types allowed for this RP (grant_types metadata value)."),
            "response_types": _("Response types allowed for this RP (response_types metadata value)."),
            "oidc_scopes": _(
                'OIDC scopes used. "openid" scope is automatically added. You may also require '
                "user attributes as claims from the Attributes section."
            ),
            "application_type": _("Application type. Used for validating redirect_uris."),
            "subject_identifier": _("Request a specific subject identifier."),
            "token_endpoint_auth_method": _("If empty, uses client_secret_basic by default."),
            "jwks_uri": _("URI for RPs JSON Web Key document (jwks_uri)."),
            "jwks": _(
                "RPs JSON Web Key document (jwks) passed as a parameter. Should only be used if the use of "
                "jwks_uri is not possible."
            ),
            "production": _(
                "Publish this RP to the production OP. Only validated data is used. "
                "Any changes to production RPs must be validated by the IdP "
                "administrators before coming into effect."
                '<div class="text-danger">Required for production use.</div>'
            ),
            "test": _(
                "Publish this RP to the test IdP using unvalidated data. "
                "Any changes might take up to 10 minutes until they are published to "
                "the test IdP."
            ),
            "saml_product": _(
                "OIDC product used by this client. For administrative use e.g. for testing "
                "different RPs during IdP updates."
            ),
            "autoupdate_idp_metadata": _("Does this RP automatically update IdP metadata at least once a day?"),
            "reset_client_secret": _("Resets the client secret."),
            "remove_client_secret": _(
                "Removes the client secret. Secret is not used if jwks are provided for "
                "client identification or application type is native."
            ),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(OidcTechnicalInformationForm, self).__init__(*args, **kwargs)
        self.fields["saml_product"].label = "OIDC product"
        # Show missing fields
        missing = get_missing_sp_data(self.instance)
        if missing:
            warning = _("Following parameters are missing for production use: ")
            self.fields["production"].help_text += (
                '<div class="text-danger">' + str(warning) + "<br>" + str("<br>".join(missing)) + "</div>"
            )
        if not self.request.user.is_superuser:
            # Disable production if missing fields
            if missing and not self.instance.production:
                self.fields["production"].widget.attrs["disabled"] = True
            del self.fields["admin_require_manual_configuration"]

    def clean_entity_id(self):
        """
        Allow only superusers set entity id something else than URL.
        """
        entity_id = self.cleaned_data["entity_id"]
        if ServiceProvider.objects.filter(entity_id=entity_id, end_at=None, history=None).exclude(pk=self.instance.pk):
            raise ValidationError(_("Client ID already exists."))
        return entity_id

    def clean_jwks(self):
        """
        Validate jwks
        """
        jwks_data = self.cleaned_data["jwks"]
        if not jwks_data:
            return jwks_data
        try:
            jwks = json.loads(jwks_data)
        except json.JSONDecodeError:
            raise ValidationError(_("Not a valid JSON."))
        if list(jwks.keys()) != ["keys"]:
            raise ValidationError(_("Invalid JSON keys."))
        if len(jwks["keys"]) == 0:
            raise ValidationError(_("No keys found."))
        for jwk in jwks["keys"]:
            if not jwk.get("kid"):
                raise ValidationError(_("JWK missing key ID."))
            if not (
                (jwk.get("kty") == "RSA" and jwk.get("n"))
                or (jwk.get("kty") == "EC" and jwk.get("x") and jwk.get("y"))
            ):
                raise ValidationError(_("Invalid JWK."))
        return jwks_data

    def clean(self):
        cleaned_data = super().clean()
        grant_types = cleaned_data.get("grant_types").values_list("name", flat=True)
        response_types = cleaned_data.get("response_types").values_list("name", flat=True)
        if cleaned_data.get("reset_client_secret") and cleaned_data.get("remove_client_secret"):
            self.add_error("remove_client_secret", _("Both remove and reset client secret selected."))
        if cleaned_data.get("jwks_uri") and cleaned_data.get("jwks"):
            self.add_error("jwks", _("Both jwks and jwks_uri selected. Use only jwks_uri if it is supported."))
        if "code" in response_types and "authorization_code" not in grant_types:
            self.add_error("grant_types", _("authorization_code grant type must be set for code response type."))
        if "token" in response_types and "implicit" not in grant_types:
            self.add_error("grant_types", _("implicit grant type must be set for token response type."))
        if "id_token" in response_types and "implicit" not in grant_types:
            self.add_error("grant_types", _("implicit grant type must be set for id_token response type."))


class SamlServiceProviderCreateForm(ModelForm):
    """
    Form for creating a service provider. Same as basic information form and entity_id.
    """

    class Meta:
        model = ServiceProvider
        fields = [
            "entity_id",
            "name_fi",
            "name_en",
            "name_sv",
            "description_fi",
            "description_en",
            "description_sv",
            "privacypolicy_fi",
            "privacypolicy_en",
            "privacypolicy_sv",
            "login_page_url",
            "application_portfolio",
            "notes",
        ]
        help_texts = {
            "entity_id": _(
                "Should be URI including scheme, hostname of your application and path "
                'e.g. https://test.helsinki.fi/sp. <div class="text-danger">'
                "Required for both production and test use.</div>"
            ),
            "name_fi": _(
                "Short (max 70 characters) and descriptive name for the service "
                'in Finnish.<div class="text-danger">'
                "Required for both production and test use.</div>"
            ),
            "name_en": _(
                "Short (max 70 characters) and descriptive name for the service "
                'in English.<div class="text-danger">'
                "Required for both production and test use.</div>"
            ),
            "name_sv": _("Short (max 70 characters) and descriptive name for the service in Swedish."),
            "description_fi": _(
                "Short (max 140 characters) description of the service "
                'in Finnish. <div class="text-danger">'
                "Required for both production and test use.</div>"
            ),
            "description_en": _(
                "Short (max 140 characters) description of the service "
                'in English. <div class="text-danger">'
                "Required for both production and test use.</div>"
            ),
            "description_sv": _("Short (max 140 characters) description of the service in Swedish."),
            "privacypolicy_fi": _(
                "Link to privacy policy in Finnish. Link must be publicly "
                'accessible. <div class="text-danger">Required for production '
                "use if the service requests any personal information.</div>"
            ),
            "privacypolicy_en": _(
                "Link to privacy policy in English. Link must be publicly "
                'accessible. <div class="text-danger">Required for production '
                "use if the service requests any personal information.</div>"
            ),
            "privacypolicy_sv": _("Link to privacy policy in Swedish. Link must be publicly accessible."),
            "login_page_url": _("Used for debugging and testing services."),
            "application_portfolio": _("Link to external application portfolio."),
            "notes": _("Additional notes about this service."),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(SamlServiceProviderCreateForm, self).__init__(*args, **kwargs)

    def clean_entity_id(self):
        """
        Allow only superusers set entity id something else than URL.
        """
        entity_id = self.cleaned_data["entity_id"]
        if not self.request.user.is_superuser and "entity_id" in self.changed_data and ":" not in entity_id:
            raise ValidationError(_("Entity Id should be URI, please contact IdP admins if this is not possible."))

        if ServiceProvider.objects.filter(entity_id=entity_id, end_at=None, history=None).exclude(pk=self.instance.pk):
            raise ValidationError(_("Entity Id already exists"))
        return entity_id

    def clean(self):
        """
        Check that name is given in English or in Finnish
        """
        name_en = self.cleaned_data["name_en"]
        name_fi = self.cleaned_data["name_fi"]
        if not name_en and not name_fi:
            raise ValidationError(_("Name in English or in Finnish is required."))


class LdapServiceProviderCreateForm(ModelForm):
    """
    Form for creating a service provider. Same as basic information form and entity_id.
    """

    class Meta:
        model = ServiceProvider
        fields = [
            "uses_ldapauth",
            "server_names",
            "name_fi",
            "name_en",
            "name_sv",
            "description_fi",
            "description_en",
            "description_sv",
            "privacypolicy_fi",
            "privacypolicy_en",
            "privacypolicy_sv",
            "login_page_url",
            "application_portfolio",
            "notes",
        ]
        help_texts = {
            "uses_ldapauth": _(
                "Does this service use the LDAPAuth proxy in order to access "
                "user and group data for authentication and access control?"
            ),
            "server_names": _(
                "Full server names (not IPs), one per line. Used for access "
                'control. <div class="text-danger">Required for non-ldapauth.</div>'
            ),
            "name_fi": _(
                "Short (max 70 characters) and descriptive name for the service in "
                'Finnish. <div class="text-danger">Required. </div>'
            ),
            "name_en": _("Short (max 70 characters) and descriptive name for the service in English."),
            "name_sv": _("Short (max 70 characters) and descriptive name for the service in Swedish."),
            "description_fi": _(
                "Short (max 140 characters) description of the service in "
                'Finnish. <div class="text-danger">Required.</div>'
            ),
            "description_en": _("Short (max 140 characters) description of the service in English."),
            "description_sv": _("Short (max 140 characters) description of the service in Swedish."),
            "privacypolicy_fi": _(
                "Link to privacy policy in Finnish. Link must be publicly "
                'accessible. <div class="text-danger">Required if the '
                "service requests any personal information.</div>"
            ),
            "privacypolicy_en": _("Link to privacy policy in English. Link must be publicly accessible."),
            "privacypolicy_sv": _("Link to privacy policy in Swedish. Link must be publicly accessible."),
            "login_page_url": _("Used for debugging and testing services."),
            "application_portfolio": _("Link to external application portfolio."),
            "notes": _("Additional notes about this service."),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(LdapServiceProviderCreateForm, self).__init__(*args, **kwargs)
        self.fields["name_fi"].required = True

    def clean_server_names(self):
        """
        Check server names format
        """
        server_names = self.cleaned_data["server_names"]
        server_names_list = server_names.splitlines()
        pattern = re.compile(
            r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*"
            r"([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
        )
        for server_name in server_names_list:
            if not pattern.match(server_name):
                raise ValidationError(_("Invalid list of server names."))
        return server_names

    def clean_name_fi(self):
        """
        Check name_fi format
        """
        name_fi = self.cleaned_data["name_fi"]
        if len(ldap_entity_id_from_name(name_fi)) == 0:
            raise ValidationError(_("Invalid Finnish name."))
        return name_fi


class OidcServiceProviderCreateForm(ModelForm):
    """
    Form for creating a OIDC Relying Party. Same as basic information form and entity_id / client_id.
    """

    class Meta:
        model = ServiceProvider
        fields = [
            "entity_id",
            "name_fi",
            "name_en",
            "name_sv",
            "description_fi",
            "description_en",
            "description_sv",
            "privacypolicy_fi",
            "privacypolicy_en",
            "privacypolicy_sv",
            "login_page_url",
            "application_portfolio",
            "notes",
        ]
        help_texts = {
            "entity_id": _(
                "Client identifier of the relying party. "
                "It is usually recommended to use random identifier. "
                '<div class="text-danger">Required for both production and test use.</div>'
            ),
            "name_fi": _(
                "Short (max 70 characters) and descriptive name for the service "
                'in Finnish.<div class="text-danger">'
                "Required for both production and test use.</div>"
            ),
            "name_en": _(
                "Short (max 70 characters) and descriptive name for the service "
                'in English.<div class="text-danger">'
                "Required for both production and test use.</div>"
            ),
            "name_sv": _("Short (max 70 characters) and descriptive name for the service in Swedish."),
            "description_fi": _(
                "Short (max 140 characters) description of the service "
                'in Finnish. <div class="text-danger">'
                "Required for both production and test use.</div>"
            ),
            "description_en": _(
                "Short (max 140 characters) description of the service "
                'in English. <div class="text-danger">'
                "Required for both production and test use.</div>"
            ),
            "description_sv": _("Short (max 140 characters) description of the service in Swedish."),
            "privacypolicy_fi": _(
                "Link to privacy policy in Finnish. Link must be publicly "
                'accessible. <div class="text-danger">Required for production '
                "use if the service requests any personal information.</div>"
            ),
            "privacypolicy_en": _(
                "Link to privacy policy in English. Link must be publicly "
                'accessible. <div class="text-danger">Required for production '
                "use if the service requests any personal information.</div>"
            ),
            "privacypolicy_sv": _("Link to privacy policy in Swedish. Link must be publicly accessible."),
            "login_page_url": _("Used for debugging and testing services."),
            "application_portfolio": _("Link to external application portfolio."),
            "notes": _("Additional notes about this service."),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(OidcServiceProviderCreateForm, self).__init__(*args, **kwargs)
        self.fields["entity_id"].label = "Client ID"
        self.fields["entity_id"].initial = random_oidc_client_id

    def clean_entity_id(self):
        """
        Checks that client id is unique
        """
        entity_id = self.cleaned_data["entity_id"]
        if ServiceProvider.objects.filter(entity_id=entity_id, end_at=None, history=None).exclude(pk=self.instance.pk):
            raise ValidationError(_("Client ID already exists"))
        return entity_id

    def clean(self):
        """
        Check that name is given in English or in Finnish
        """
        name_en = self.cleaned_data["name_en"]
        name_fi = self.cleaned_data["name_fi"]
        if not name_en and not name_fi:
            raise ValidationError(_("Name in English or in Finnish is required."))


class ServiceProviderCloseForm(Form):
    """
    Form for closing service provider.
    """

    confirm = BooleanField(help_text=_("Confirm closing"))


class ServiceProviderValidationForm(Form):
    """
    Form for validation service provider.
    """

    no_email = BooleanField(required=False, help_text=_("Do not send validation email to SP admins."))
    modified_date = CharField()

    def __init__(self, *args, **kwargs):
        self.modified_date = kwargs.pop("modified_date", None)
        super(ServiceProviderValidationForm, self).__init__(*args, **kwargs)
        self.fields["modified_date"].widget = HiddenInput()
        self.fields["modified_date"].initial = self.modified_date
