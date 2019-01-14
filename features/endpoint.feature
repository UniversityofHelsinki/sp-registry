Feature: Endpoints
	Adding endpoints to registry 

Scenario: Endpoint modifications
	Given test environment with logged in user exists
	When clicking link with text "https://sp.example.org/sp"
	And clicking visible link with text "SAML Endpoints"
	And filling endpoint form with location "https://sp.example.org/Shibboleth.sso/SAML2/POST"
	And filling endpoint form with location "https://sp.example.org/Shibboleth.sso/SAML2/POST/2"
	Then the result page will include text "https://sp.example.org/Shibboleth.sso/SAML2/POST"	
	And the result page will include text "https://sp.example.org/Shibboleth.sso/SAML2/POST/2"	
	When filling endpoint form with location "https://sp.example.org/Shibboleth.sso/SAML2/POST"
	Then the result page will include text "Endpoint already exists"
	And count of tag "td" is "8"
	When removing first endpoint
	Then count of tag "td" is "4"
