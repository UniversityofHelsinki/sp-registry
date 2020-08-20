from datetime import timedelta

from django.db import models
from django.utils.translation import ugettext_lazy as _

from rr.models.serviceprovider import ServiceProvider


def redirecturi_validator(sp, uri, error):
    """
    Validates redirect URI

    error: Raised error class
    """
    if ':' not in uri or uri.startswith(':') or uri.endswith(':'):
        raise error(_('Enter a valid URI.'))
    if RedirectUri.objects.filter(sp=sp, uri=uri, end_at=None).exists():
        raise error(_('URI already exists'))
    if sp.application_type == 'web' and not uri.startswith('https://'):
        raise error(_('Web application URIs must begin with https: scheme'))
    if '#' in uri:
        raise error(_('URIs must not contain fragments'))
    if (sp.application_type == 'native' and uri.startswith('http') and
            not uri.startswith('http://localhost')):
        raise error(_('Native applications must use custom URI schemes or http: scheme with '
                      'localhost as the hostname.'))


class RedirectUri(models.Model):
    """
    Stores a single redirect uri, related to :model:`rr.ServiceProvider`

    OIDC specific. Allowed redirect URIs
    """
    sp = models.ForeignKey(ServiceProvider, related_name='redirecturis', on_delete=models.CASCADE)

    uri = models.CharField(max_length=255, verbose_name=_('Redirect URI'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_('Validated on'))

    def __str__(self):
        return '%s: %s' % (self.sp, self.uri)

    @property
    def status(self):
        if self.end_at and not self.validated or self.end_at and self.validated > self.end_at:
            return _('removed')
        elif self.end_at:
            return _('pending removal')
        elif not self.validated:
            return _('pending validation')
        elif self.updated_at > self.validated + timedelta(minutes=1):
            return _('update pending validation')
        else:
            return _('validated')
