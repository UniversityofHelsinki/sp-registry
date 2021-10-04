# SP Resource Registry
Used for maintaining information about services connected to SAML, OIDC and LDAP.

Allows registration of new services by the users and validation of information by IdP admins, before transferring
metadata to production.

## Project structure
* ansible : Ansible files for test environment installation
* auth : Login templates and Shibboleth authentication backend for Django
* features : Tests using behave
* requirements : requirements files for development and production
* rr : main SP Resource Registry program
  * fixtures : json fixtures for models
  * forms : forms
  * locale : Finnish translations
  * management : command line tools
  * migrations : database migration history
  * models : database models
  * serializers: serializer for API
  * static : static files
  * templates : templates
  * templatetags : template functions
  * testdata : generated data for tests
  * tests : unit tests
  * utils : generic functions, i.e. metadata generation and parsing
  * views : views
  * views_api : views for API
* settings : settings for development and production

## Documentation
Project uses Django admin docs for development documentation:
https://docs.djangoproject.com/en/2.2/ref/contrib/admin/admindocs/

## Usage
### Users
Users log with SSO. Staff and faculty affiliations will get automatic activation, you will have to activate others
through Django admin backend.

You may add local accounts with Django admin backend

Create a superuser with
"./manage.py createsuperuser" command

### Menu structure
#### If you have logged in
* Service Providers
  * Lists all user's services / all services for site admins
  * Click the entityID for more information
  * Anyone who has access to site, can create a new service provider
* API
  * Allows creating, resetting and removing API key.

#### If you have selected a service
* Summary
  * SP summary and possible modifications since last validation.
  * Validation for site admins
  * Possibility to remove SP, if it is validated and not in production or test use
* Basic Information
  * Basic administrative information and notes
  * Admin notes is only shown here if admin. It is shown to users in Summary view
* Technical Attributes
  * Technical attributes like entity_id, publishing to production etc.
     * Entity Id must be in URI format and unique in the system
     * Site admins may override the URI requirement
* Attributes
  * Attribute requisitions and reasons for them
  * Only listing attributes that are marked for publishing
* Certificates (SAML only)
  * Certificates for the service
* SAML Endpoints (SAML only)
  * Allows only SAML2 bindings, admins may override this with metadata import
* User Groups (LDAP only)
  * List of groups that service has access
* Redirect URIs (OIDC only)
  * Allowed redirect URIs for OIDC
* Contacts
  * Technical, administrative and support contacts for the service
* Admins
  * SP admins who can access and modify this SP in the registy
  * New admins may be invited by email, invitations are valid for 30 days
  * Permission groups management
* Test Users
  * Custom test users for test services
* View Metadata (SAML and OIDC only)
  * Shows SP metadata. You may choose between validated and unvalidated metadata
* Login Statistics (SAML only)
  * Show daily login statistics

#### For site admins
* Attributes
  * All attributes in the service
  * By clicking the attribute, you get list of SPs requesting it
  * Modification through Django Admin backend
* Certificates
  * Lists expired and less than 2048 bit certificates
* SAML Special Configs
  * SAML configuration summaries
    * non-default signing and encryption
    * NameId settings
    * MFA and authorization
    * SAML products
* SAML Login Summary
  * Login statistics for SAML services
* Emails
  * Sending email to server admins. Templates are managed in django admin
* Manage SAML metadata
  * Saves updated SAML metadata to git repository
* Manage LDAP metadata
  * Saves updated LDAP metadata to git repository
* Manage OIDC metadata
  * Saves updated OIDC metadata to git repository
* Database Admin
  * Django Admin backend

### Command line commands
For more information run "./manage.py <command> -h"
* cleandb
  * Cleans old services or personal information from the db
* decryptclientsecret
  * Decrypt client secrets from OIDC metadata (if ecncrypted)
* exportattributefilter
  * Exporting SAML attribute filter
* exportldap
  * Exports LDAP registrations data (custom format)
* exportmetadata
  * Exporting SAML metadata
* exportoidc
  * Exporting OIDC metadata in JSON format
* importattributefilter
  * Importing attributes from old attribute filter
* importmetadata
  * Importing metadata from file
* importstatistics
  * Importing statistics from external database
* nslookup
  * Checks that service URLs exist

### API
Almost everything is also available through REST API, using Token or Session authentication. Users can manage their
API tokens with browser UI.

API documentation is available in path swagger/ for authenticated users.

## Installation
### Requirements
* Django 2.2
* Python 3.6-3.8
* MySQL 5.6+ / MariaDB 10.1+
* Requires dev libraries for Python and MySQL/MariaDB for compiling python mysqlclient.

### Test environment
Vagrantfile with Ansible provisioning is provided for test environment.

Usage:
1. Install vagrant (https://www.vagrantup.com/)
1. run command "vagrant up" (and wait for it to set up )
1. Open https://localhost:8443/ in browser (browser complains about security risk as self-signed certificate is used)
1. Use local login with user admin, password RandomPass12

Shibboleth and attribute test service are not yet included.

### Installation

Example on 18.04 LTS

1. Install apt requirements: "sudo apt install python3 python3-venv python3-dev python3-pip mariadb-server
python-mysqldb libmariadbclient-dev libapache2-mod-wsgi-py3"
1. Clone source from git
1. Set up Python virtual environment "python3 -m venv /path/to/venv" and activate it "source /path/to/venv/bin/activate"
1. Install requirements "pip install -r requirements/[production|development].txt"
1. Set up database (MariaDB)
1. Copy settings/local_settings_example.py to settings/local_settings.py and modify as necessary
1. Modify manage.py to point django config file to production or development
1. Run db migrations: "./manage.py migrate"
1. Collect static files "./manage.py collectstatic"
1. Load fixtures: "./manage.py loaddata rr/fixtures/attribute.json rr/fixtures/nameidformat.json"
1. Set up apache, wsgi and shibd

### Shibboleth
Program uses following attributes:
* sn
* givenName
* mail
* eduPersonPrincipalName (or other unique ID for usernames)
* eduPersonAffiliation (staff and faculty groups are given permission to add new SPs)

Attributes are mapped in local_settings.py

Redirect Shibboleth SP errors to /error/

### Apache & WSGI
Example of Apache WSGI configuration
```
<VirtualHost _default_:443>
WSGIDaemonProcess sp-registry.example.org user=appuser group=appuser python-home=/path/to/venv python-path=/path/to/rr
WSGIProcessGroup sp-registry.example.org

WSGIScriptAlias / /path/to/rr/rr/wsgi.py process-group=sp-registry.example.org

Alias /static/ /path/to/rr/static/

<Directory /path/to/rr/static>
    Require all granted
</Directory>

<Directory /path/to/rr>
    <Files wsgi.py>
        Require all granted
    </Files>
</Directory>

<Location />
    AuthType shibboleth
    Require shibboleth
</Location>

<Location /Shibboleth.sso>
    SetHandler shib
</Location>
SSLOptions +StdEnvVars

</VirtualHost>
```

## Attribute test service
Attribute test service lists all user's attributes and validates them against the optional regex filters.

Attributes shown in the test service, validation regex and Shibboleth environment variable names are defined in
Attribute model objects.
Non public attributes are only listed if user has some value in the attribute.

This service can be made available in different Apache virtual host by pointing it to the wsgi_attributetest.py.
It should also have it's own Shibboleth ApplicationOverride, with all the attributes enabled.

## Tests

### Running tests
./manage.py test

For behaviour testing with browser automation:
./manage.py behave --settings=settings.development
Behaviour tests usually take 3-4 minutes to run.

### Requirements
Splinter is required for browser automation tests.
Install Firefox and geckodriver for headless tests: http://splinter.readthedocs.io/en/latest/drivers/firefox.html

## SAML test service
External SAML IdP may be used as a test service but configuration depends on the IdP solution and requires
that IdP can use SQL database for user and attribute queries.

* Metadata is reloaded with timed management script
* Users are checked from the TestUsers table
* Access to specific service is checked from the TestUser valid_for table
* Attributes are checked from the TestUserData table