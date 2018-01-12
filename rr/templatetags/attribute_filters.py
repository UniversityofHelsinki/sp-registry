from django import template
import re

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
