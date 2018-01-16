Feature: Contacts
	Adding contacts to registry 

Scenario: Contact modifications
	Given test environment with logged in user exists
	When clicking link with text "https://sp.example.org/sp"
	And clicking link with text "Contacts"
	And filling contact form with email "tester@example.org"
	And filling contact form with email "tester.test@example.org"
	And filling contact form with email "tester@example.org"
	Then the result page will include text "Contact already exists"
	And count of tag "td" is "8"
	When removing first contact
	Then count of tag "td" is "4"
