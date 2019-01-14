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

# Activate SAML/LDAP SP listing
ACTIVATE_SAML = True
ACTIVATE_LDAP = True
ACTIVATE_OIDC = True

# Attribute test service
ATTRIBUTE_TEST_SERVICE = True
ATTRIBUTE_TEST_SERVICE_LOGOUT_URL = 'https://localhost:8080/testservice/Shibboleth.sso/Logout'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Email address used as send address
SERVER_EMAIL = 'noreply@example.org'
# Will receive notifications of changes in metadata and also if error 500 occurs
# Format should be a list of tuples of (Full name, email address).
# Example: [('John', 'john@example.com'), ('Mary', 'mary@example.com')]
ADMINS = [('IDP Admins', 'idp-admins@example.org')]
# Contact email shown in login page if user account is not activated automatically
DEFAULT_CONTACT_EMAIL = 'contact@example.org'
# Send email to emails defined in ADMINS when changes have been made
ADMIN_NOTIFICATION = True
# Send email to service admins when changes have been validated
VALIDATION_NOTIFICATION = True

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

# Uncomment to redirect logout to local Shibboleth logout
# SHIBBOLETH_LOGOUT_URL = "/Shibboleth.sso/Logout"

ATTRIBUTE_TEST_SERVICE = True
ATTRIBUTE_TEST_SERVICE_LOGOUT_URL = 'https://localhost/testservice/Shibboleth.sso/Logout'

# Path to git repositorio
METADATA_GIT_REPOSITORIO = '/path/to/metadata/git/repo/'
LDAP_GIT_REPOSITORIO = '/path/to/ldap/git/repo/'
# Metadata file used for upload
METADATA_FILENAME = 'metadata.xml'
LDAP_METADATA_FILENAME = 'ldap-metadata.xml'

# Path to static files for collection
STATIC_ROOT = '/path/to/rr/static/'

MFA_AUTHENTICATION_CONTEXT = 'https://refeds.org/profile/mfa'
