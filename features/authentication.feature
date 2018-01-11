Feature: authentication
	Trying to log in

Scenario: Trying to access page without authentication
	When I visit the "/"
	Then the result page will include "Login using SSO" 