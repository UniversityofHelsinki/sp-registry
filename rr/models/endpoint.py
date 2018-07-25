from django.db import models
from django.utils.translation import ugettext_lazy as _

from rr.models.serviceprovider import ServiceProvider


class Endpoint(models.Model):
    """
    Stores a single certificate, related to :model:`rr.ServiceProvider`
    """
    sp = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)

    TYPECHOICES = (('AssertionConsumerService', _('AssertionConsumerService')),
                   ('SingleLogoutService', _('SingleLogoutService')),
                   ('ArtifactResolutionService', _('ArtifactResolutionService')))

    BINDINGCHOICES = (('urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
                       _('urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST')),
                      ('urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
                       _('urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect')),
                      ('urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact',
                       _('urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact')),
                      ('urn:oasis:names:tc:SAML:2.0:bindings:SOAP',
                       _('urn:oasis:names:tc:SAML:2.0:bindings:SOAP')))

    type = models.CharField(max_length=30, choices=TYPECHOICES, verbose_name=_('Endpoint Type'))
    binding = models.CharField(max_length=60, choices=BINDINGCHOICES,
                               verbose_name=_('Endpoint Binding'))
    url = models.URLField(max_length=255, verbose_name=_('Endpoint URL'))
    index = models.SmallIntegerField(null=True, blank=True, verbose_name=_('Endpoint Index'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_('Validated on'))
