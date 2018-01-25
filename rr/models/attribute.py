from django.db import models
from django.utils.translation import ugettext_lazy as _


class Attribute(models.Model):
    """
    Stores attribute information for available SAML attributes.
    Public flag controls if attribute is visilible to users.
    """
    friendlyname = models.CharField(max_length=255, verbose_name=_('Attribute FriendlyName'))
    info = models.TextField(blank=True, verbose_name=_('Attribute information'))
    name = models.CharField(max_length=255, verbose_name=_('Attribute OID'))
    attributeid = models.CharField(max_length=255, verbose_name=_('Attribute ID'))
    nameformat = models.CharField(max_length=255, verbose_name=_('Attribute NameFormat'))
    public = models.BooleanField(default=True, verbose_name=_('Show in attribute list'))
    schemalink = models.BooleanField(default=True, verbose_name=_('Show link to funetEduPerson-schema'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    def __str__(self):
        return self.friendlyname
