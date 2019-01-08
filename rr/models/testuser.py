from django.db import models
from django.utils.translation import ugettext_lazy as _

from rr.models.attribute import Attribute
from rr.models.serviceprovider import ServiceProvider


class TestUser(models.Model):
    """
    Stores a test user, related to :model:`rr.ServiceProvider`
    """
    sp = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    username = models.CharField(max_length=50, verbose_name=_('Login name'))
    password = models.CharField(max_length=64, verbose_name=_('Password'))
    firstname = models.CharField(blank=True, max_length=255,
                                 verbose_name=_('First name'))
    lastname = models.CharField(blank=True, max_length=255, verbose_name=_('Last name'))
    valid_for = models.ManyToManyField(ServiceProvider, blank=True, related_name="valid_for",
                                       verbose_name=_('Valid for selected SPs'))
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
    value = models.CharField(blank=True, null=True, max_length=511,
                             verbose_name=_('Attribute value'))
    username = models.CharField(max_length=50, verbose_name=_('Login name'))
    friendlyname = models.CharField(max_length=255, verbose_name=_('Attribute FriendlyName'))
    entity_id = models.CharField(max_length=255, verbose_name=_('Entity Id'))

    def save(self, *args, **kwargs):
        self.username = self.user.username
        self.friendlyname = self.attribute.friendlyname
        self.entity_id = self.user.sp.entity_id
        super().save(*args, **kwargs)

    def __str__(self):
        return '%s %s %s' % (self.entity_id, self.username, self.friendlyname)

    class Meta:
        indexes = [
            models.Index(fields=['username']),
        ]


def update_entity_ids(sp):
    """
    Update entity_id values for TestUserData in case of entity_id change
    """
    user_data = TestUserData.objects.filter(user__sp=sp)
    for data in user_data:
        if data.entity_id != data.user.sp.entity_id:
            data.entity_id = data.user.sp.entity_id
            data.save()
