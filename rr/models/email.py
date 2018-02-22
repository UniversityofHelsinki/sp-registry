from django.db import models
from django.utils.translation import ugettext_lazy as _


class Template(models.Model):
    title = models.CharField(max_length=78, blank=True, null=True, verbose_name=_('Message title'))
    body = models.TextField(blank=True, null=True, verbose_name=_('Message body'))

    def __str__(self):
        return self.title
