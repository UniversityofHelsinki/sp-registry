from django.db import models
from django.utils.translation import ugettext_lazy as _


class Attribute(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Attribute name'))
    info = models.TextField(verbose_name=_('Attribute information'))
    oid = models.CharField(max_length=255, verbose_name=_('Attribute OID'))
    public = models.BooleanField(default=True, verbose_name=_('Show in attribute list'))

    def __str__(self):
        return self.name
