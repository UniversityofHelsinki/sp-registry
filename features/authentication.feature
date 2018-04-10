Feature: Authentication
	Trying to log in

Scenario: Authenticating to system
	Given user "Myself" exists
	And sp "https://sp.example.org/sp" exists
	And user "Myself" is "https://sp.example.org/sp" admin
	When I visit the "/"
	Then the result page will include text "Login using Single Sign-On"
	When I login with "Myself" and "mysecretpassword"
	Then the result page will include text "Service Providers"
	And the result page will include text "https://sp.example.org/sp"
