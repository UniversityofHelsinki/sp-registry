from datetime import timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

from rr.models.serviceprovider import ServiceProvider


def endpoint_validator(sp, binding, index, is_default, location, endpoint_type, error):
    """
    Validates endpoint

    error: Raised error class
    """
    if Endpoint.objects.filter(sp=sp, type=endpoint_type, binding=binding, location=location, end_at=None).exists():
        raise error(_("Endpoint already exists"))
    elif (
        index
        and Endpoint.objects.filter(sp=sp, type=endpoint_type, binding=binding, index=index, end_at=None).exists()
    ):
        raise error(_("Index already exists"))
    elif is_default and not index:
        raise error(_("Default endpoint must be indexed"))
    elif (
        is_default
        and Endpoint.objects.filter(sp=sp, type=endpoint_type, binding=binding, is_default=True, end_at=None).exists()
    ):
        raise error(_("Default endpoint already exists"))


class Endpoint(models.Model):
    """
    Stores a single certificate, related to :model:`rr.ServiceProvider`

    SAML specific for saving SAML Endpoints of a service.
    """

    sp = models.ForeignKey(ServiceProvider, related_name="endpoints", on_delete=models.CASCADE)

    TYPECHOICES = (
        ("AssertionConsumerService", _("AssertionConsumerService")),
        ("SingleLogoutService", _("SingleLogoutService")),
        ("ArtifactResolutionService", _("ArtifactResolutionService")),
    )

    BINDINGCHOICES = (
        ("urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST", _("urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST")),
        (
            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            _("urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"),
        ),
        (
            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact",
            _("urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact"),
        ),
        ("urn:oasis:names:tc:SAML:2.0:bindings:SOAP", _("urn:oasis:names:tc:SAML:2.0:bindings:SOAP")),
    )

    type = models.CharField(max_length=30, choices=TYPECHOICES, verbose_name=_("Endpoint Type"))
    binding = models.CharField(max_length=60, choices=BINDINGCHOICES, verbose_name=_("Binding"))
    location = models.URLField(max_length=255, verbose_name=_("Location"))
    response_location = models.URLField(blank=True, max_length=255, verbose_name=_("ResponseLocation"))
    index = models.SmallIntegerField(null=True, blank=True, verbose_name=_("Index"))
    is_default = models.BooleanField(default=False, verbose_name=_("isDefault"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Entry end time"))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_("Validated on"))

    def __str__(self):
        return "%s: %s %s" % (self.type, self.binding, self.location)

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
