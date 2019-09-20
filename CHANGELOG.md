# Changelog

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

