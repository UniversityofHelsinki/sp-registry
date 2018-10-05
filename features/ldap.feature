Feature: LDAP service provider
	Modifying LDAP service provider information
	

Scenario: LDAP information modifications
	Given test environment with LDAP service and logged in user exists
	Then the result page will include text "ldap-1"
	When clicking link with text "ldap-1"
	Then the result page will include text "Details"
	When clicking visible link with text "Technical Attributes"
	And filling ldap technical information form with invalid information
	Then the result page will include text "Invalid list of server names."
	When filling ldap technical information form
	And clicking visible link with text "Summary"
	Then the result page will include text "ldap-1"
	And the result page will include text "ldap-modified.example.org"
	