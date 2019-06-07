from django.db import models
from django.utils.translation import ugettext_lazy as _
from rr.models.serviceprovider import ServiceProvider


class RedirectUri(models.Model):
    """
    Stores a single redirect uri, related to :model:`rr.ServiceProvider`

    OIDC specific. Allowed redirect URIs
    """
    sp = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)

    uri = models.CharField(max_length=255, verbose_name=_('Redirect URI'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_('Validated on'))
