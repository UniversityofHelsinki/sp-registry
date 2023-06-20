from django.db import models
from django.utils.translation import ugettext_lazy as _


class ResponseType(models.Model):
    """
    Stores single OIDC response type.
    """

    name = models.CharField(max_length=10, verbose_name=_("Response type"))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class GrantType(models.Model):
    """
    Stores single OIDC grant type.
    """

    name = models.CharField(max_length=20, verbose_name=_("Grant type"))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class OIDCScope(models.Model):
    """
    Stores single OIDC scope.
    """

    name = models.CharField(max_length=25, verbose_name=_("OIDC Scope"))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
