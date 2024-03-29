Feature: Accesscontrol
	Testing access control with superuser

Scenario: Access pages with superuser
	Given test environment with logged in superuser exists
	Then the result page will include text "https://sp.example.org/sp"
	Then the result page will include text "https://sp.example.com/sp"
	When I visit the "/summary/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/summary/2"
	Then the result page will include text "https://sp.example.com/sp"
	When I visit the "/serviceprovider/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/serviceprovider/2"
	Then the result page will include text "https://sp.example.com/sp"
	When I visit the "/technical/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/technical/2"
	Then the result page will include text "https://sp.example.com/sp"
	When I visit the "/attribute/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/attribute/2"
	Then the result page will include text "https://sp.example.com/sp"
	When I visit the "/certificate/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/certificate/2"
	Then the result page will include text "https://sp.example.com/sp"
	When I visit the "/endpoint/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/endpoint/2"
	Then the result page will include text "https://sp.example.com/sp"
	When I visit the "/contact/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/contact/2"
	Then the result page will include text "https://sp.example.com/sp"
	When I visit the "/admin/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/admin/2"
	Then the result page will include text "https://sp.example.com/sp"
	When I visit the "/metadata/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/metadata/2"
	Then the result page will include text "https://sp.example.com/sp"
	When I visit the "/attribute/list/"
	Then the result page will include text "Listing all attributes included in this system."
	When I visit the "/certificate/list/"
	Then the result page will include text "Certificate administration"
	When I visit the "/saml_admin_list/"
	Then the result page will include text "Special configurations"
	When I visit the "/admin_django/"
	Then the result page will include text "Site administration"
