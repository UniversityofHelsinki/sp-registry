from django.db import models
from django.utils.translation import ugettext_lazy as _
from rr.models.serviceprovider import ServiceProvider


class Ldap(models.Model):
    """
    Stores LDAP technical information, related to :model:`rr.ServiceProvider`
    """
    sp = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    password_saving = models.BooleanField(default=False, verbose_name=_('Does the service locally store user passwords?'))
    password_saving_info = models.TextField(blank=True, null=True, verbose_name=_('How are you storing the saved passwords and why?'))
    server_names = models.CharField(max_length=511, verbose_name=_('Server names (not IPs), separated with space'))
    TARGETGROUPCHOICES = (('internet', _('Internet')),
                          ('university', _('University of Helsinki users')),
                          ('restricted', _('Restricted user group')))
    target_group = models.CharField(max_length=10, choices=TARGETGROUPCHOICES, verbose_name=_('Target group for the service'))
    service_account = models.BooleanField(default=False, verbose_name=_('Does the service use a service account?'))
    service_account_contact = models.TextField(blank=True, null=True,
                                               verbose_name=_('Email address and phone number for delivering the service account credentials.'))
    local_storage_users = models.BooleanField(default=False, verbose_name=_('Service stores a local copy of users and their information?'))
    local_storage_groups = models.BooleanField(default=False, verbose_name=_('Service stores a local copy of groups and group members?'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_('Validated on'))
