Feature: Test users
	Creating test users to use with test IdP 

Scenario: Admin invitations
	Given test environment with logged in user exists
	When clicking link with text "https://sp.example.org/sp"
	Then the result page will not include text "Test users"
	When clicking link with text "Basic Information"
	And setting publish to test servers
	Then the result page will include text "Test users"
	When clicking link with text "Attributes"
	And filling attribute form
	And clicking link with text "Test users"
	And filling test user form
	When clicking link with text "shholmes"
	Then the page will include form value "sherlock.holmes@example.org"
