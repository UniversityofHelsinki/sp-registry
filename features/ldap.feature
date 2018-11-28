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


Scenario: Adding a new LDAP connection
    Given test environment with logged in user exists
    When clicking object with text "Add a new LDAP connection"
    Then the result page will include text "This form is used to add new LDAP connection request"
    When filling ldap creation form
    Then the result page will include text "Details"
    And message "0" in mailbox should have "[SP-Registry] New ldap service added: mynewtestservice" in subject