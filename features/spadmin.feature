Feature: Service Provider Admins
	Inviting new admins for SP 

Scenario: Admin invitations
	Given test environment with logged in user exists
	And invite exists
	When clicking link with text "https://sp.example.org/sp"
	And clicking visible link with text "Admins"
	And filling invite form with email "tester@example.org"
	Then the result page will include text "tester@example.org"
	And message "0" in mailbox should have "Teemu Testeri has added you" in body
	When removing admin
	Then the result page will not include text "https://sp.example.org/sp"
	When I visit the "/invite/?key=f5bc2a80eba67ca71df3dc740caf22a6eed7b2f3"
	Then the result page will include text "My program name"

Scenario: Admin groups
	Given test environment with logged in user exists
	When clicking link with text "https://sp.example.org/sp"
	And clicking visible link with text "Admins"
	Then the result page will include text "No admin groups"
	When filling group form with name "test-group-a"
	Then the result page will not include text "No admin groups"
	Then the result page will include text "test-group-a"
	When removing admin group
	Then the result page will include text "No admin groups"

