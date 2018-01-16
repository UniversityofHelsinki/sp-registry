Feature: Endpoints
	Adding endpoints to registry 

Scenario: Endpoint modifications
	Given test environment with logged in user exists
	When clicking link with text "https://sp.example.org/sp"
	And clicking link with text "SAML Endpoints"
	And filling endpoint form with url "https://sp.example.org/Shibboleth.sso/SAML2/POST"
	And filling endpoint form with url "https://sp.example.org/Shibboleth.sso/SAML2/POST/2"
	And filling endpoint form with url "https://sp.example.org/Shibboleth.sso/SAML2/POST"
	Then the result page will include text "Endpoint already exists"
	And count of tag "td" is "8"
	When removing first endpoint
	Then count of tag "td" is "4"
