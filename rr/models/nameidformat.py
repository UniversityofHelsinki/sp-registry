from django.db import models
from django.utils.translation import ugettext_lazy as _


class NameIDFormat(models.Model):
    """
    Stores a single name identifier format

    SAML specific. Used to list available name identifier formats.
    """

    nameidformat = models.CharField(max_length=255, verbose_name=_("Name Identifier Format"))
    public = models.BooleanField(default=True, verbose_name=_("Show in list"))

    def __str__(self):
        return self.nameidformat
