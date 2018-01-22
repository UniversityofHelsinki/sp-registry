from django.db import models
from django.utils.translation import ugettext_lazy as _
from rr.models.serviceprovider import ServiceProvider
from rr.models.attribute import Attribute


class TestUser(models.Model):
    """
    Stores a test user, related to :model:`rr.ServiceProvider`
    """
    sp = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    username = models.CharField(max_length=255, verbose_name=_('Login name'))
    password = models.CharField(max_length=255, verbose_name=_('Password'))
    firstname = models.CharField(blank=True, null=True, max_length=255, verbose_name=_('First name'))
    lastname = models.CharField(blank=True, null=True, max_length=255, verbose_name=_('Last name'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))

    def __str__(self):
        return self.username


class TestUserData(models.Model):
    """
    Stores a attribute value for test user, related to :model:`rr.TestUser`
    and :model:`rr.Attribute`
    """
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    user = models.ForeignKey(TestUser, on_delete=models.CASCADE)
    value = models.CharField(blank=True, null=True, max_length=511, verbose_name=_('Attribute value'))
