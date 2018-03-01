Feature: Superuser features
	Modifying service provider basic and testing validation

Scenario: Basic information modifications and validation
	Given test environment with logged in superuser exists
	Then the result page will include text "https://sp.example.org/sp"
	Then the result page will include text "https://sp.example.com/sp"
	When clicking link with text "https://sp.example.org/sp"
	Then the result page will include text "Details"
	When clicking visible link with text "Basic Information"
	And filling basic information form with invalid information
	When filling basic information form
	And clicking visible link with text "Summary"
	Then the result page will include text "My new program name"
	And the result page will include text "My program name"
	And message "0" in mailbox should have "[SP-Registry] Changes waiting for validation" in subject
	When clicking object with name "validate_changes"
	Then the result page will include text "My new program name"
	And message "1" in mailbox should have "[SP-Registry] Changes to your service have been validated" in subject

Scenario: Endpoint modifications and validation
	Given test environment with logged in superuser exists
	When clicking link with text "https://sp.example.com/sp"
	And clicking visible link with text "SAML Endpoints"
	And filling endpoint form with url "https://sp.example.org/Shibboleth.sso/SAML2/POST"
	And filling endpoint form with url "https://sp.example.org/Shibboleth.sso/SAML2/POST/2"
	And clicking visible link with text "Summary"
	Then the result page will include text "https://sp.example.org/Shibboleth.sso/SAML2/POST/2"
	And message "0" in mailbox should have "[SP-Registry] Changes waiting for validation" in subject
	When checking "no_email"
	And clicking object with name "validate_changes"
	Then mailbox size should be "1"
	