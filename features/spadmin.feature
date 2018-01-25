Feature: Admins
	Inviting new admins for SP 

Scenario: Admin invitations
	Given test environment with logged in user exists
	And invite exists
	When clicking link with text "https://sp.example.org/sp"
	And clicking link with text "Admins"
	And filling invite form with email "tester@example.org"
	Then the result page will include text "tester@example.org"
	And there should be invitation in email
	When removing admin
	Then the result page will not include text "https://sp.example.org/sp"
	When I visit the "/invite/f5bc2a80eba67ca71df3dc740caf22a6eed7b2f3"
	Then the result page will include text "My program name"
