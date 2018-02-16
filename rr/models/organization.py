from django.db import models
from django.utils.translation import ugettext_lazy as _, get_language


class Organization(models.Model):
    """
    Stores an organization, related to :model:`rr.ServiceProvider`
    """
    name_fi = models.CharField(max_length=255, blank=True, verbose_name=_('Organization Name (Finnish)'))
    name_en = models.CharField(max_length=255, blank=True, verbose_name=_('Organization Name (English)'))
    name_sv = models.CharField(max_length=255, blank=True, verbose_name=_('Organization Name (Swedish)'))
    description_fi = models.CharField(max_length=255, blank=True, verbose_name=_('Organization Description (Finnish)'))
    description_en = models.CharField(max_length=255, blank=True, verbose_name=_('Organization Description (English)'))
    description_sv = models.CharField(max_length=255, blank=True, verbose_name=_('Organization Description (Swedish)'))
    url_fi = models.URLField(max_length=255, blank=True, verbose_name=_('Organization URL (Finnish)'))
    url_en = models.URLField(max_length=255, blank=True, verbose_name=_('Organization URL (English)'))
    url_sv = models.URLField(max_length=255, blank=True, verbose_name=_('Organization URL (Swedish)'))

    def __str__(self):
        if get_language() == "fi" and self.name_fi:
            return self.name_fi
        elif get_language() == "sv" and self.name_sv:
            return self.name_sv
        else:
            if self.name_en:
                return self.name_en
            elif self.name_fi:
                return self.name_fi
            else:
                return self.name_sv

    def name(self):
        if get_language() == "fi" and self.name_fi:
            return self.name_fi
        elif get_language() == "sv" and self.name_sv:
            return self.name_sv
        else:
            if self.name_en:
                return self.name_en
            elif self.name_fi:
                return self.name_fi
            else:
                return self.name_sv

    def description(self):
        if get_language() == "fi" and self.description_fi:
            return self.description_fi
        elif get_language() == "sv" and self.description_sv:
            return self.description_sv
        else:
            if self.description_en:
                return self.description_en
            elif self.description_fi:
                return self.description_fi
            else:
                return self.description_sv

    def url(self):
        if get_language() == "fi" and self.url_fi:
            return self.url_fi
        elif get_language() == "sv" and self.url_sv:
            return self.url_sv
        else:
            if self.url_en:
                return self.url_en
            elif self.url_fi:
                return self.url_fi
            else:
                return self.url_sv
