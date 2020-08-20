from datetime import timedelta

from django.db import models
from django.utils.translation import ugettext_lazy as _

from rr.models.serviceprovider import ServiceProvider


class Contact(models.Model):
    """
    Stores a single contact, related to :model:`rr.ServiceProvider`
    """
    sp = models.ForeignKey(ServiceProvider, related_name='contacts', on_delete=models.CASCADE)

    TYPECHOICES = (('administrative', _('Administrative')),
                   ('technical', _('Technical')),
                   ('support', _('Support')),)

    type = models.CharField(max_length=30, choices=TYPECHOICES, verbose_name=_('Contact Type'))
    firstname = models.CharField(max_length=50, blank=True, verbose_name=_('First Name'))
    lastname = models.CharField(max_length=50, blank=True, verbose_name=_('Last Name'))
    email = models.EmailField(blank=True, verbose_name=_('E-Mail'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_('Validated on'))

    def __str__(self):
        return '%s: %s %s' % (self.type, self.firstname, self.lastname)

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
