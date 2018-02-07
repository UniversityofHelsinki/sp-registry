Feature: Basic information
	Modifying basic information and testing differences

Scenario: Basic information modifications
	Given test environment with logged in user exists
	Then the result page will include text "https://sp.example.org/sp"
	When clicking link with text "https://sp.example.org/sp"
	Then the result page will include text "Details"
	When clicking visible link with text "Basic Information"
	And filling basic information form with invalid information
	Then the result page will include text "Entity Id should be URI, please contact IdP admins if this is not possible."
	When filling basic information form
	And clicking visible link with text "Summary"
	Then the result page will include text "My new program name"
	And the result page will include text "My program name"
	And the result page will include text "https://privacy.example.org/sp.pdf"