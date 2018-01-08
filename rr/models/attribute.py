from django.db import models
from django.utils.translation import ugettext_lazy as _


class Attribute(models.Model):
    friendlyname = models.CharField(max_length=255, verbose_name=_('Attribute FriendlyName'))
    info = models.TextField(blank=True, verbose_name=_('Attribute information'))
    name = models.CharField(max_length=255, verbose_name=_('Attribute OID'))
    attributeid = models.CharField(max_length=255, verbose_name=_('Attribute ID'))
    nameformat = models.CharField(max_length=255, verbose_name=_('Attribute NameFormat'))
    public = models.BooleanField(default=True, verbose_name=_('Show in attribute list'))

    def __str__(self):
        return self.friendlyname
