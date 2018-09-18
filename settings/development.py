from .common import *

DEBUG = True

INSTALLED_APPS += (
    'behave_django',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'dev.log',
            'formatter': 'file',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'rr': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

from .local_settings import *
