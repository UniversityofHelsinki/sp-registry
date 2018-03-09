Feature: Metadata
	Import and export test metadata 
#
#Scenario: Importing test metadata
#	Given superuser "Myself" exists
#	When loading test metadata
#	When I visit the "/"
#	Then the result page will include text "Login using SSO"
#	When I login with "Myself" and "mysecretpassword"
#	Then the result page will include text "https://sp.example.org/sp"
#	When clicking link with text "https://sp.example.org/sp"
#	When clicking visible link with text "View Metadata"
#	Then the page will have same metadata


Scenario: Metadata validation
	Given test environment with logged in superuser exists
	When I visit the "/certificate/1"
	And filling certificate form with valid certificate
	And I visit the "/attribute/1"
	And filling attribute form
	And I visit the "/endpoint/1"
	And filling endpoint form with url "https://sp.example.org/Shibboleth.sso/SAML2/POST"
	And filling endpoint form with url "https://sp.example.org/Shibboleth.sso/SAML2/POST/2"
	And I visit the "/contact/1"
	And filling contact form with email "tester@example.org"
	And I visit the "/metadata/1"
	Then the page will have default metadata
	When clicking visible link with text "Show unvalidated"
	Then the page will have metadata 1
	When I visit the "/summary/1"
	And clicking object with name "validate_changes"
	And I visit the "/metadata/1"
	Then the page will have metadata 1
	When I visit the "/certificate/1"
	And removing first certificate
	And I visit the "/attribute/1"
	And removing attribute reason
	And I visit the "/metadata/1"
	Then the page will have metadata 1
	When I visit the "/summary/1"
	And clicking object with name "validate_changes"
	And I visit the "/metadata/1"
	Then the page will have metadata 2