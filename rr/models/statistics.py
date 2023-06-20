from django.db import models
from django.utils.translation import ugettext_lazy as _

from rr.models.serviceprovider import ServiceProvider


class Statistics(models.Model):
    """
    Stores usage statistics information, related to :model:`rr.ServiceProvider`
    """

    sp = models.ForeignKey(ServiceProvider, related_name="statistics", on_delete=models.CASCADE)

    logins = models.IntegerField(verbose_name=_("Number of logins"))
    users = models.IntegerField(null=True, verbose_name=_("Number of unique users"))
    date = models.DateField(verbose_name=_("Login date"))

    class Meta:
        ordering = ["-date"]
