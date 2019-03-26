# SP Resource Registry
Used for maintaining information about services connected to SAML and LDAP.

Allows registration of new services by the users and validation of information by IdP admins, before transferring
metadata to production.

## Project structure
* auth : Shibboleth authentication backend for Django
* features : Tests using behave
* log : log directory
* requirements : requirements files for development and production
* rr : main SP Resource Registry program
  * fixtures : json fixtures for models
  * forms : forms
  * locale : Finnish translations
  * management : command line tools
  * migrations : database migration history
  * models : database models
  * static : static files
  * templates : templates
  * templatetags : template functions
  * testdata : generated data for tests
  * tests : unit tests
  * utils : generic functions, i.e. metadata generation and parsing
  * views : views
* settings : settings for development and production

## Documentation
Project uses Django admin docs for development documentation:
https://docs.djangoproject.com/en/1.11/ref/contrib/admin/admindocs/

## Usage
### Users
Users log with SSO. Staff and faculty will get automatic activation, you will have to activate others through Django admin backend.

You may add local accounts with Django admin backend

Create a superuser with
"./manage.py createsuperuser" command

### Menu structure
#### If you have logged in
* Service Providers
  * Lists all user's services, everything for site admins
  * Click the entityID for more information
  * Anyone who has access to site, may create a new SP

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
* Contacts
  * Technical, administrative and support contacts for the service
* Admins
  * SP admins who can access and modify this SP in the registy
  * New admins may be invited by email, invitations are valid for 30 days
* Test Users
  * Custom test users for test services
* View Metadata
  * Shows SP metadata. You may choose between validated and unvalidated metadata

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
* Emails
  * Sending email to server admins. Templates are managed in django admin
* Manage SAML metadata
  * Saves updated SAML metadata to git repository
* Manage LDAP metadata
  * Saves updated LDAP metadata to git repository
* Database Admin
  * Django Admin backend

### Command line commands
For more information run "./manage.py <command> -h"
* cleandb
  * Cleans old services or personal information from the db
* exportldap
  * Exports LDAP registrations data (custom format)
* exportmetadata
  * Exporting metadata or attribute filter
* importattributefilter
  * Importing attributes from old attribute filter
* importmetadata
  * Importing metadata from file
* nslookup
  * Checks that service URLs exist

## Installation
### Requirements
Currently uses Django 1.11 (LTS version, support until Apr 2020)
* Python 3.4-3.6
* MySQL/MariaDB 5.5+
* Requires dev libraries for Python and MySQL/MariaDB for compiling python mysqlclient.

### Ubuntu installation

Tested on 16.04 LTS

1. Install apt requirements: "sudo apt install python3.5 python3.5-venv python3.5-dev mariadb-server python-mysqldb libmariadb-client-lgpl-dev libmysqlclient-dev libapache2-mod-wsgi-py3"
1. Clone source from git
1. Set up Python virtual environment "pyvenv3.5 /path/to/venv" and activate it "source /path/to/venv/bin/activate"
1. Install requirements "pip install -r requirements/[production|development].txt"
1. Set up database (Mysql)
1. Copy settings/local_settings_example.py to settings/local_settings.py and modify
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

Attributes shown in the test service, validation regex and Shibboleth environment variable names are defined in Attribute model objects.
Non public attributes are only listed if user has some value in the attribute.

This service can be made available in different Apache virtual host by pointing it to the wsgi_attributetest.py.
It should also have it's own Shibboleth ApplicationOverride, with all the attributes enabled.

## Tests

### Running tests
./manage.py test

For behaviour testing with browser automation:
./manage.py behave --settings=settings.development
Behaviour tests have better coverage but usually take 3-4 minutes to run.

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

