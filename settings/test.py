from .common import *
from .local_settings_example import *
from .logging import LOGGING

DEBUG = True

INSTALLED_APPS += ("behave_django",)

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
    }
}

LOGGING["loggers"]["django.request"] = {"level": "ERROR"}
