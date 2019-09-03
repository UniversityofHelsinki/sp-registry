from django.db import models
from django.utils.translation import ugettext_lazy as _
from rr.models.serviceprovider import ServiceProvider


class Statistics(models.Model):
    """
    Stores usage statistics information, related to :model:`rr.ServiceProvider`
    """
    sp = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)

    logins = models.IntegerField(verbose_name=_('Number of logins'))
    date = models.DateField(verbose_name=_('Login date'))

    class Meta:
        ordering = ['-date']
