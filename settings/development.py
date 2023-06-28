from .common import *

DEBUG = True

INSTALLED_APPS += ("behave_django",)

try:
    from .local_logging import *
except ModuleNotFoundError:
    from .logging import *

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

from .local_settings import *
