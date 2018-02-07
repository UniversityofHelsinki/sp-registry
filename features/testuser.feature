Feature: Test users
	Creating test users to use with test IdP 

Scenario: Creating test users
	Given test environment with logged in user exists
	When clicking link with text "https://sp.example.org/sp"
	Then the result page will not include text "Test users"
	When clicking visible link with text "Basic Information"
	And setting publish to test servers
	Then the result page will include text "Test Users"
	When clicking visible link with text "Attributes"
	And filling attribute form
	And clicking visible link with text "Test Users"
	And filling test user form
	When clicking link with text "shholmes"
	Then the page will include form value "sherlock.holmes@example.org"
