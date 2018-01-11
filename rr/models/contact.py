from django.db import models
from django.utils.translation import ugettext_lazy as _
from rr.models.serviceprovider import ServiceProvider


class Contact(models.Model):
    """
    Stores a single contact, related to :model:`rr.ServiceProvider`
    """
    sp = models.ForeignKey(ServiceProvider)

    TYPECHOICES = (('administrative', _('Administrative')),
                   ('technical', _('Technical')),
                   ('support', _('Support')),)

    type = models.CharField(max_length=30, choices=TYPECHOICES, verbose_name=_('Contact Type'))
    firstname = models.CharField(max_length=50, blank=True, verbose_name=_('First Name'))
    lastname = models.CharField(max_length=50, blank=True, verbose_name=_('Last Name'))
    email = models.EmailField(blank=True, verbose_name=_('E-Mail'))
    created = models.DateTimeField(null=True, blank=True, verbose_name=_('Created at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
