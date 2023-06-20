from django.db import models
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _


class Organization(models.Model):
    """
    Stores an organization, related to :model:`rr.ServiceProvider`
    """

    name_fi = models.CharField(max_length=255, blank=True, verbose_name=_("Organization Name (Finnish)"))
    name_en = models.CharField(max_length=255, blank=True, verbose_name=_("Organization Name (English)"))
    name_sv = models.CharField(max_length=255, blank=True, verbose_name=_("Organization Name (Swedish)"))
    description_fi = models.CharField(max_length=255, blank=True, verbose_name=_("Organization Description (Finnish)"))
    description_en = models.CharField(max_length=255, blank=True, verbose_name=_("Organization Description (English)"))
    description_sv = models.CharField(max_length=255, blank=True, verbose_name=_("Organization Description (Swedish)"))
    url_fi = models.URLField(max_length=255, blank=True, verbose_name=_("Organization URL (Finnish)"))
    url_en = models.URLField(max_length=255, blank=True, verbose_name=_("Organization URL (English)"))
    url_sv = models.URLField(max_length=255, blank=True, verbose_name=_("Organization URL (Swedish)"))
    privacypolicy_fi = models.URLField(max_length=255, blank=True, verbose_name=_("Privacy Policy URL (Finnish)"))
    privacypolicy_en = models.URLField(max_length=255, blank=True, verbose_name=_("Privacy Policy URL (English)"))
    privacypolicy_sv = models.URLField(max_length=255, blank=True, verbose_name=_("Privacy Policy URL (Swedish)"))

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

    def name(self, lang=get_language()):
        """Returns name in given language (defaulting current language),
        or in priority order en->fi->sv if current is not available"""
        if lang == "fi" and self.name_fi:
            return self.name_fi
        elif lang == "sv" and self.name_sv:
            return self.name_sv
        else:
            if self.name_en:
                return self.name_en
            elif self.name_fi:
                return self.name_fi
            else:
                return self.name_sv

    def description(self, lang=get_language()):
        """Returns description in given language (defaulting current language),
        or in priority order en->fi->sv if current is not available"""
        if lang == "fi" and self.description_fi:
            return self.description_fi
        elif lang == "sv" and self.description_sv:
            return self.description_sv
        else:
            if self.description_en:
                return self.description_en
            elif self.description_fi:
                return self.description_fi
            else:
                return self.description_sv

    def url(self, lang=get_language()):
        """Returns url in given language (defaulting current language),
        or in priority order en->fi->sv if current is not available"""
        if lang == "fi" and self.url_fi:
            return self.url_fi
        elif lang == "sv" and self.url_sv:
            return self.url_sv
        else:
            if self.url_en:
                return self.url_en
            elif self.url_fi:
                return self.url_fi
            else:
                return self.url_sv

    def privacypolicy(self, lang=get_language()):
        """Returns privacy policy url in given language (defaulting current
        language), or in priority order en->fi->sv if current is not
        available"""
        if lang == "fi" and self.privacypolicy_fi:
            return self.privacypolicy_fi
        elif lang == "sv" and self.privacypolicy_sv:
            return self.privacypolicy_sv
        else:
            if self.privacypolicy_en:
                return self.privacypolicy_en
            elif self.privacypolicy_fi:
                return self.privacypolicy_fi
            elif self.privacypolicy_sv:
                return self.privacypolicy_sv
        return ""
