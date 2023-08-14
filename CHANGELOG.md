# Changelog
## [2.2.0] - 2023-xx-xx
### Changes
* DB query optimizations using prefetch_related and select_related
* Requirements version updates
* Change yes/no icons to use django admin images

## [2.1.0] - 2023-07-06
### Changes
* Changed drf-yasg to drf-spectacular and support CoreAPI 3.0 
* Improved search and filter fields to TestUser API
* Improved properties, search and filters to admin views
* Filter out objects linked to deleted SPs in API
* Django's security update to 4.2.3

## [2.0.1] - 2023-06-29
### Changes
* Fix buttons in auth token and password reset templates
* Fix attribute test service urls and css
* Fix table name setting in importstatistics command

## [2.0.0] - 2023-06-28
### Changes
* Upgrade to Django 4.2
* Upgrade to Bootstrap 5
* Change formatting to use black and isort
* Other requirements version updates
* Update chart.js and change moment.js to date-fns
* Update logging settings to allow local config file
* Remove duplicate addresses from notification emails
* Add service name to admin notifications
* Remove test services from admin notifications, with option
* Fix group permissions to edit test users

### Updating notes
Django 4.2 requires Python 3.8 or newer and MySQL 8/MariaDb 10.4 or newer.
CDN has changed to jsdelivr.net from cloudflare.com, update CSP if needed.

## [1.10.0] - 2022-08-05
### Changes
* Requirements version updates
* Removed support for Python 3.6
* Added privacy policy URLs for organizations
* Added optional group where members have read access to every service
* Changed link to friendlyName in attribute admin list
* Changed attribute test to show validation regex only if value is not valid

### Updating notes
* Includes added database fields, run migrations

## [1.9.0] - 2021-10-04
### Changes
* Requirements version updates, including Django 3.2
* Added support for unique user statistics
* Added templates for SSO errors
* Added contacts to LDAP metadata
* Updated dev/test vagrant box to Ubuntu 20.04
* Refactored logging configuration
* Refactored UIInfo generation, use customized privacy URL if not given
* Various smaller fixes and updates

## [1.8.0] - 2021-02-16
### Changes
* Requirements version updates
* Translation updates
* Removed placeholder texts in attribute selection for clarity

## [1.7.0] - 2020-08-20
### Changes
* Added REST API
* Refactoring

### Updating notes
* Requires additional packages, install according to requirements
* Includes related name changes and new packages using database, run migrations

## [1.6.1] - 2020-08-20
### Changes
* Finnish translation updates

## [1.6.0] - 2020-06-17
### Changes
* Send notifications to admins only when production status or production
service is modified
* Setting values for defining who should receive validation messages for
services. Options: admins, technical contact, administrative contact
* Fix client secret decrypt decoding
* Version updates

## [1.5.0] - 2020-05-25
### Changes
* Added option to create multiple test users at once
* Prevent setting service to production if any required information is missing
* Added permissions by groups

### Updating notes
* Includes added database fields, run migrations

## [1.4.0] - 2020-01-09
### Changes
* Added option to use individual SAML metadata files for dynamic metadata
management
* Added jwks and jwks_uri parameters for OIDC 
* Added token_endpoint_auth_method parameter for OIDC
* Added missing table descriptions
* Fixed JSON sorting
* Fixed RedirectUri warning
* Updated requirements
* Code and test improvements

### Updating notes
* Includes added database fields, run migrations

## [1.3.0] - 2019-11-07
### Changes
* Improved responsiveness and mobile use
* Fixed xml attribute order (lxml 4.4 changes)
* Moved static urls from templates to translation files
* Moved attribute filter export to separate management command
* Using stdin/stdout as defaults in export/import management commands if files
are not given

## [1.2.1] - 2019-09-24
### Changes
* Fix error and warning messages in metadata git management

## [1.2.0] - 2019-09-20
### Changes
* Added statistics summary page for superusers
* Fixed date limit in cleandb script
* Fixed bootstrap css url in attribute test service
* Fixed endpoint parameter in nslookup script
* Fixed missing OIDC option in administation emails
* Code refactoring for reduced complexity

## [1.1.0] - 2019-09-03
### Changes
* Added login statistics
* Added scoped attribute check for test service
* Using git empty tree object for diff if HEAD is not found
* Limit SP default list for superusers to production changes
* Allow service removal when it does not affect production
* Load Bootstrap and jQuery from CDN

### Updating notes
* Includes added database fields and tables, run migrations

## [1.0.0] - 2019-06-26
Started keeping a changelog

### Changes
* Added support for OIDC services
* Added Django 2.2 support
* Dropped Python 3.4 support
* Changed entity_id validator for SAML entities from URL to URI
* Fixed typos in translations
* Fixed error message when git command fails
* Added missing migration for LDAPAuth field description
* Restructured fixtures
* Added missing unittests

### Updating notes
* Includes added database fields and tables, run migrations.
* Includes changes to local_settings.py, add to local version:
  * Added OIDC_CLIENT_SECRET_KEY
  * Added OIDC_GIT_REPOSITORIO
  * Added OIDC_METADATA_FILENAME

## [no version] - 2019-04-18
Version in the GitHub as of 18 Apr 2019.

