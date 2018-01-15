Feature: authentication
	Trying to log in

Scenario: Trying to access page without authentication
	Given user "Myself" exists
	And sp "https://example.com/Shibboleth" exists
	And user "Myself" is "https://example.com/Shibboleth" admin
	When I visit the "/"
	Then the result page will include text "Login using SSO"
	When I login with "Myself" and "mysecretpassword"
	Then the result page will include text "Service Provider Registry"
	Then the result page will include text "https://example.com/Shibboleth"
