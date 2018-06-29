from django.db import models
from django.utils.translation import ugettext_lazy as _


class Attribute(models.Model):
    """
    Stores attribute information for available SAML attributes.
    Public flag controls attribute visibility to users.
    """
    friendlyname = models.CharField(max_length=255, verbose_name=_('Attribute FriendlyName'))
    info = models.TextField(blank=True, verbose_name=_('Attribute information'))
    name = models.CharField(max_length=255, verbose_name=_('Attribute OID'))
    attributeid = models.CharField(max_length=255, verbose_name=_('Attribute ID'))
    nameformat = models.CharField(max_length=255, verbose_name=_('Attribute NameFormat'))
    public = models.BooleanField(default=True, verbose_name=_('Show in attribute list'))
    schemalink = models.BooleanField(default=True, verbose_name=_('Show link to funetEduPerson-schema'))
    test_service = models.BooleanField(default=True, verbose_name=_('Show in Attribute test service'))
    test_service_required = models.BooleanField(default=False, verbose_name=_('Required attribute in test service'))
    regex_test = models.CharField(blank=True, max_length=255, verbose_name=_('Regex text for attribute validation'))
    shib_env = models.CharField(blank=True, max_length=255, verbose_name=_('Shibboelth environmental variable for the attribute'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    def __str__(self):
        return self.friendlyname
