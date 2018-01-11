from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from rr.models.attribute import Attribute


class ServiceProvider(models.Model):
    """
    Stores a service provider, related to :model:`auth.User` and
    :model:`rr.Attribute` through :model:`rr.SPAttribute`
    """
    entity_id = models.CharField(max_length=255, verbose_name=_('Entity Id'))
    name_fi = models.CharField(max_length=255, verbose_name=_('Service Name (Finnish)'))
    name_en = models.CharField(max_length=255, blank=True, verbose_name=_('Service Name (English)'))
    name_sv = models.CharField(max_length=255, blank=True, verbose_name=_('Service Name (Swedish)'))
    description_fi = models.CharField(max_length=255, blank=True, verbose_name=_('Service Description (Finnish)'))
    description_en = models.CharField(max_length=255, blank=True, verbose_name=_('Service Description (English)'))
    description_sv = models.CharField(max_length=255, blank=True, verbose_name=_('Service Description (Swedish)'))
    privacypolicy_fi = models.URLField(max_length=255, blank=True, verbose_name=_('Privacy Policy URL (Finnish)'))
    privacypolicy_en = models.URLField(max_length=255, blank=True, verbose_name=_('Privacy Policy URL (English)'))
    privacypolicy_sv = models.URLField(max_length=255, blank=True, verbose_name=_('Privacy Policy URL (Swedish)'))
    login_page_url = models.URLField(max_length=255, blank=True, verbose_name=_('Service Login Page URL'))
    discovery_service_url = models.URLField(max_length=255, blank=True, verbose_name=_('Discovery Service URL'))
    name_format_transient = models.BooleanField(default=False, verbose_name=_('urn:oasis:names:tc:SAML:2.0:nameid-format:transient'))
    name_format_persistent = models.BooleanField(default=False, verbose_name=_('urn:oasis:names:tc:SAML:2.0:nameid-format:persistent'))
    encyrpt_attribute_assertions = models.BooleanField(default=False, verbose_name=_('Encrypt attribute assertions'))
    production = models.BooleanField(default=False, verbose_name=_('Publish to production servers'))
    test = models.BooleanField(default=False, verbose_name=_('Publish to test servers'))

    # Attributes are lingked through SPAttribute model to include reason and validation information
    attributes = models.ManyToManyField(Attribute, through='SPAttribute')
    admins = models.ManyToManyField(User, related_name="admins")

    updated = models.DateTimeField(null=True, blank=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Updated by'))
    validated = models.BooleanField(default=False, verbose_name=_('Validated'))

    def __str__(self):
        return self.entity_id

#     def save(self, *args, **kwargs):
#         if self.pk:
#             sp = ServiceProvider.objects.get(pk=self.pk)
#             sp.pk = None
#             sp.end_at = timezone.now()
#             sp.save()
#             sp.admins.set(self.admins.all())
# #             attributes = SPAttribute.objects.filter(sp=self.sp)
# #             for attribute in attributes:
# #                 SPAttribute.objects.create(sp=sp, attribute=attribute.attribute, reason=attribute.reason, update=attribute.updated, validated=attribute.validaded)
#             # self.pk.updated = timezone.now()
#
#         return super(ServiceProvider, self).save(*args, **kwargs)


class SPAttribute(models.Model):
    """
    Stores iformation for SP attributes, related to :model:`rr.ServiceProvider`
    and :model:`rr.Attribute`
    """
    attribute = models.ForeignKey(Attribute)
    sp = models.ForeignKey(ServiceProvider)
    reason = models.CharField(max_length=255, verbose_name=_('Reason for the attribute requisition'))
    updated = models.DateTimeField(null=True, blank=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_('Validated on'))
