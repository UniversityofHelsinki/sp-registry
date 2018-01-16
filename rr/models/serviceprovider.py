from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, get_language
from rr.models.attribute import Attribute


class ServiceProvider(models.Model):
    """
    Stores a service provider, related to :model:`auth.User` and
    :model:`rr.Attribute` through :model:`rr.SPAttribute`
    """
    entity_id = models.CharField(max_length=255, verbose_name=_('Entity Id'))
    name_fi = models.CharField(max_length=255, blank=True, verbose_name=_('Service Name (Finnish)'))
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
    name_format_transient = models.BooleanField(default=False, verbose_name=_('nameid-format:transient'))
    name_format_persistent = models.BooleanField(default=False, verbose_name=_('nameid-format:persistent'))
    encyrpt_attribute_assertions = models.BooleanField(default=False, verbose_name=_('Encrypt attribute assertions'))
    production = models.BooleanField(default=False, verbose_name=_('Publish to production servers'))
    test = models.BooleanField(default=False, verbose_name=_('Publish to test servers'))

    # Attributes are linked through SPAttribute model to include reason and validation information
    attributes = models.ManyToManyField(Attribute, through='SPAttribute')
    admins = models.ManyToManyField(User, related_name="admins")

    modified = models.BooleanField(default=True, verbose_name=_('Modified'))
    history = models.IntegerField(blank=True, null=True, verbose_name=_('History key'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Updated by'))
    validated = models.BooleanField(default=False, verbose_name=_('Validated'))

    def name(self):
        if get_language() == "fi" and self.name_fi:
            return self.name_fi
        elif get_language() == "sv" and self.name_sv:
            return self.name_sv
        else:
            return self.name_en

    def description(self):
        if get_language() == "fi" and self.description_fi:
            return self.description_fi
        elif get_language() == "sv" and self.description_sv:
            return self.description_sv
        else:
            return self.description_en

    def __str__(self):
        return self.entity_id

    def get_all_fields(self):
        """Returns a list of all field names on the instance."""
        fields = []
        for f in self._meta.fields:

            fname = f.name
            # resolve picklists/choices, with get_xyz_display() function
            get_choice = 'get_'+fname+'_display'
            if hasattr(self, get_choice):
                value = getattr(self, get_choice)()
            else:
                try:
                    value = getattr(self, fname)
                except AttributeError:
                    value = None
            # only display fields with values and skip some fields entirely
            if f.editable and f.name not in ('id', 'end_at', 'history', 'validated', 'modified'):
                fields.append(
                  {
                   'label': f.verbose_name,
                   'name': f.name,
                   'value': value,
                  }
                )
        return fields


class SPAttribute(models.Model):
    """
    Stores iformation for SP attributes, related to :model:`rr.ServiceProvider`
    and :model:`rr.Attribute`
    """
    attribute = models.ForeignKey(Attribute)
    sp = models.ForeignKey(ServiceProvider)
    reason = models.CharField(max_length=255, verbose_name=_('Reason for the attribute requisition'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_('Validated on'))

    class Meta:
        ordering = ["attribute__friendlyname"]
