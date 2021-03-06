Feature: User groups
	Adding userg roups to registry 

Scenario: User group modifications
	Given test environment with logged in user exists
	When clicking link with text "ldap-3"
	And clicking visible link with text "User Groups"
	And filling user group form with name "Teppo Testeri"
	And filling user group form with name "Maija Mehiläinen"
	And filling user group form with name "Teppo Testeri"
	Then the result page will include text "Group already added"
	And count of tag "td" is "2"
	When removing first user group
	Then count of tag "td" is "1"
