from datetime import timedelta

from django.db import models
from django.utils.translation import ugettext_lazy as _
from rr.models.serviceprovider import ServiceProvider


class UserGroup(models.Model):
    """
    Stores a single user group, related to :model:`rr.ServiceProvider`

    LDAP specific. Used for specifying user groups where LDAP service
    has access.
    """
    sp = models.ForeignKey(ServiceProvider, related_name='usergroups', on_delete=models.CASCADE)

    name = models.CharField(max_length=255, verbose_name=_('Group name'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_('Validated on'))

    def __str__(self):
        return '%s: %s' % (self.sp, self.name)

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
