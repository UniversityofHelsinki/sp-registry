from django import template
import re
from django.conf import settings

register = template.Library()
numeric_test = re.compile("^\d+$")


@register.filter
def get_item(value, arg):
    """
    Return field value with dynamic field name
    """
    if hasattr(value, str(arg)):
        return getattr(value, arg)
    elif hasattr(value, 'has_key') and value in arg:
        return value[arg]
    elif numeric_test.match(str(arg)) and len(value) > int(arg):
        return value[int(arg)]
    else:
        return None


@register.simple_tag
def privacy_policy_url(name):
    if name in ["PRIVACY_POLICY_URL"]:
        return getattr(settings, name, "")
    return ""
