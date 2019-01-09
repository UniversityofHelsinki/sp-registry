Feature: Service provider
	Modifying service provider basic and techincal information and testing differences

Scenario: Basic information modifications and validation
	Given test environment with logged in user exists
	Then the result page will include text "https://sp.example.org/sp"
	When clicking link with text "https://sp.example.org/sp"
	Then the result page will include text "Details"
	When clicking visible link with text "Basic Information"
	And filling basic information form with invalid information
	When filling basic information form
	And clicking visible link with text "Summary"
	Then the result page will include text "My new program name"
	And the result page will include text "My program name"
	And message "0" in mailbox should have "[SP-Registry] Changes waiting for validation" in subject
	

Scenario: Technical information modifications
	Given test environment with logged in user exists
	Then the result page will include text "https://sp.example.org/sp"
	When clicking link with text "https://sp.example.org/sp"
	Then the result page will include text "Details"
	When clicking visible link with text "Technical Attributes"
	And filling technical information form with invalid information
	Then the result page will include text "Entity Id should be URI, please contact IdP admins if this is not possible."
	When filling technical information form
	And clicking visible link with text "Summary"
	Then the result page will include text "https://sp.example.org/sp"
	Then the result page will include text "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"

	
Scenario: Service provider creation
    Given test environment with logged in user exists
    When clicking object with text "Add a new service provider"
    Then the result page will include text "Adding a new service provider"
    When filling service creation form
    Then the result page will include text "Details"
    And the result page will include text "This service provider is currently not published to the production or the test IdPs. You may publish this SP in the Technical Attributes page."
    And message "0" in mailbox should have "[SP-Registry] New saml service added: https://new.example.org/sp" in subject
    When clicking visible link with text "View Metadata"
    Then the result page will include text "Could not find metadata"
    When clicking visible link with text "Show unvalidated"
    Then the result page will include text "EntityDescriptor"
    And the result page will include text "https://new.example.org/sp"
    