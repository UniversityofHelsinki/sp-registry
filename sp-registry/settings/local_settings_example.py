SECRET_KEY = 'generated secret key'

ALLOWED_HOSTS = []

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

TIME_ZONE = 'EET'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Email address used as send address
SERVER_EMAIL = 'noreply@example.org'
# Will receive notifications of changes in metadata and also if error 500 occurs
ADMINS = 'idp-admins@example.org'
# Contact email shown in login page if user account is not activated automatically
DEFAULT_CONTACT_EMAIL = 'contact@example.org'
# Privacy policy url shown in login page
PRIVACY_POLICY_URL = 'https://example.org/DataPrivacyPolicy.pdf'
# Path to save test screenshots
TEST_SCREENSHOT_DIR = '/path/to/test-screenshots/'

SAML_LOGIN_URL = 'https://localhost/Shibboleth.sso/?target=https://localhost/login/?next='
SAML_ATTR_EPPN = 'shib_eppn'
SAML_ATTR_FIRST_NAME = 'shib_first_name'
SAML_ATTR_LAST_NAME = 'shib_last_name'
SAML_ATTR_EMAIL = 'shib_mail'
SAML_ATTR_AFFILIATION = 'shib_affiliation'

# Path to git repositorio
METADATA_GIT_REPOSITORIO = '/path/to/metadata/git/repo/'
# Metadata file used for upload
METADATA_FILENAME = 'metadata.xml'

# Path to static files for collection
STATIC_ROOT = '/path/to/rr/static/'
