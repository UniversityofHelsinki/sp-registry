# SP Resource Registy
Used for maintaining of SAML Service Provicer information. Similar to HAKA rr.
SP administrators can add new SPs and update information.

SP metadata can be updated to test IdPs automatically.
Includes validation of attributes for production use.

## Installation
### Requirements
Currently uses Django 1.11 (LTS version until Apr 2020)
* Python 3.4-3.6
* MySQL/MariaDB 5.5+
* Requires dev libraries for Python and MySQL/MariaDB for compiling python mysqlclient.
**Ubuntu installation**

    apt install python3.6 python3.6-venv python3.6-dev mariadb-server python-mysqldb libmariadb-client-lgpl-dev libmysqlclient-dev

1. Clone from git
1. Set up Python virtual environment 
1. Install requirements "pip install -r requirements.txt"
1. Set up database
1. Copy rr/local_settings_example.py to rr/local_settings.py and modify
1. Run migrations "./manage.py migrate"
1. Set up apache, wsgi and shibd