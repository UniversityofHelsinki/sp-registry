Feature: Attributes
	Adding attributes to registry 

Scenario: Attribute modifications
	Given test environment with logged in user exists
	When clicking link with text "https://sp.example.org/sp"
	And clicking visible link with text "Attributes"
	And filling attribute form
	When clicking visible link with text "Summary"
	Then the result page will include text "schacPersonalUniqueCode"
	And the result page will include text "Need this for authentication"
	And the result page will include text "Basic contact address"
	When clicking visible link with text "Attributes"
	And removing attribute reason
	And clicking visible link with text "Summary"
	Then the result page code include text "table-danger"
	And the result page will include text "Basic contact address"

Scenario: Attribute list with superuser
	Given test environment with logged in superuser exists
	When clicking link with text "https://sp.example.org/sp"
	And clicking visible link with text "Attributes"
	Then the result page will include text "schacPersonalUniqueCode"
	