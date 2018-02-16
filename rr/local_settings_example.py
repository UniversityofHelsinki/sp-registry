import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'generated secret key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rr_db',
        'USER': 'rr_db',
        'PASSWORD': 'rr_db',
        'HOST': 'localhost',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

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
            'filename': '/path/to/log/debug.log',
            'formatter': 'file',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
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

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@example.org'
DEFAULT_CONTACT_EMAIL = 'contact@example.org'

TEST_SCREENSHOT_DIR = '/path/to/test-screenshots/'

SAML_LOGIN_URL = 'https://localhost/Shibboleth.sso/?target=https://localhost/login/?next='
SAML_ATTR_EPPN = 'shib_eppn'
SAML_ATTR_FIRST_NAME = 'shib_first_name'
SAML_ATTR_LAST_NAME = 'shib_last_name'
SAML_ATTR_EMAIL = 'shib_mail'
SAML_ATTR_AFFILIATION = 'shib_affiliation'

STATIC_ROOT = '/path/to/rr/static/'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
