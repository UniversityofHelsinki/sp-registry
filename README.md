# SP Resource Registy
Used for maintaining of SAML Service Provicer information. Similar to HAKA rr.
SP administrators can add new SPs and update information.

SP metadata can be updated to test IdPs automatically.
Includes validation of attributes for production use.

## Project structure
* auth : Shibboleth authentication backend for Django
* features : Tests using behave
* log : log directory
* requirements : requirements files for development and production
* rr : main SP Resource Registry program
  * fixtures : json fixtures for models
  * forms : forms
  * management : command line tools
  * migrations : database migration history
  * models : database models
  * static : static files
  * templates : templates
  * templatetags : template functions
  * utils : generic functions, i.e. metadata generation and parsing
  * views : views
* settings : settings for development and production
* testdata : generated data for tests

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
1. Modify manage.py config file setting
1. Run migrations: "./manage.py migrate"
1. Collect statistics: "./manage.py collectstatic"
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

<Directory /path/to/rr/rr>
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

## Tests
### Requirements
Splinter is used for automated browser tests.
Install Firefox and geckodriver for headless tests: http://splinter.readthedocs.io/en/latest/drivers/firefox.html

### Running tests
./manage.py behave
