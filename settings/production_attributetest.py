from .common import *

DEBUG = False

try:
    from .local_logging import *
except ModuleNotFoundError:
    from .logging import *

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SHIBBOLETH_LOGOUT_URL = ""

from .local_settings import *

ROOT_URLCONF = "urls_attributetest"
