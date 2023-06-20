import re

from django import template
from django.conf import settings

from rr.models.serviceprovider import ServiceProvider

register = template.Library()
numeric_test = re.compile("^\d+$")


@register.filter
def get_item(value, arg):
    """
    Return field value with dynamic field name
    """
    if hasattr(value, str(arg)):
        return getattr(value, arg)
    elif hasattr(value, "has_key") and value in arg:
        return value[arg]
    elif numeric_test.match(str(arg)) and len(value) > int(arg):
        return value[int(arg)]
    else:
        return None


@register.filter
def compare_querysets(queryset_1, queryset_2):
    """
    Return true if QuerySets are equal
    """
    if list(queryset_1) == list(queryset_2):
        return True
    return False


@register.simple_tag
def privacy_policy_url(name):
    if name in ["PRIVACY_POLICY_URL"]:
        return getattr(settings, name, "")
    return ""


@register.filter
def get_production_status(obj):
    """
    Return production status from history if object is not validated
    Return false if there is no validated object
    """
    if obj.validated:
        return obj.production
    history = ServiceProvider.objects.filter(history=obj.pk).exclude(validated=None).last()
    if history:
        return history.production
    else:
        return False
