Feature: Test users
	Creating test users to use with test IdP 

Scenario: Creating test users
	Given test environment with logged in user exists
	And additional SP with admin exists
	When clicking link with text "https://sp.example.org/sp"
	Then the result page will not include text "Test users"
	When clicking visible link with text "Technical Attributes"
	And setting publish to test servers
	Then the result page will include text "Test Users"
	When clicking visible link with text "Attributes"
	And filling attribute form
	And clicking visible link with text "Test Users"
	And filling test user form
	When clicking link with text "shholmes"
	Then the page will include form value "sherlock.holmes@example.org"
    And the result page will include text "https://sp.example.org/sp"
    And the result page will include text "https://sp.example.net/sp"
    And the result page will not include text "https://sp.example.com/sp"
    When I visit the "/"
    And clicking link with text "https://sp.example.net/sp"
	And clicking visible link with text "Test Users"
	Then the result page will include text "External test users"
	And the result page will include text "shholmes"
	When removing external test user
	Then the result page will include text "External test user removed: shholmes"
	When filling test user form
    Then the result page will include text "Username already exists"
    And the result page will not include text "shholmes"
