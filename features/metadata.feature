Feature: Metadata
	Import and export test metadata 

Scenario: Importing test metadata
	Given superuser "Myself" exists
	When loading test metadata
	When I visit the "/"
	Then the result page will include text "Login using SSO"
	When I login with "Myself" and "mysecretpassword"
	Then the result page will include text "https://sp.example.org/sp"
	When clicking link with text "https://sp.example.org/sp"
	When clicking visible link with text "View Metadata"
	Then the page will have same metadata
