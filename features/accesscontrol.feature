Feature: Accesscontrol
	Testing accesscontrol with normal and superuser 

Scenario: Access pages with normal user, you should not ahve access for SP number 2
	Given test environment with logged in user exists
	Then the result page will include text "https://sp.example.org/sp"
	Then the result page will not include text "https://sp.example.com/sp"
	When I visit the "/summary/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/summary/2"
	Then the result page will include text "Page not found"
	When I visit the "/summary/3"
	Then the result page will include text "ldap.example.com ldap3.example.com"
	When I visit the "/serviceprovider/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/serviceprovider/2"
	Then the result page will include text "Page not found"
	When I visit the "/serviceprovider/3"
	Then the result page will include text "ldap.example.com ldap3.example.com"
	When I visit the "/technical/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/technical/2"
	Then the result page will include text "Page not found"
	When I visit the "/technical/3"
	Then the result page will include text "Page not found"
	When I visit the "/ldap/1"
	Then the result page will include text "Page not found"
	When I visit the "/ldap/3"
	Then the result page will include text "ldap.example.com ldap3.example.com"
	When I visit the "/ldap/4"
	Then the result page will include text "Page not found"
	When I visit the "/attribute/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/attribute/2"
	Then the result page will include text "Page not found"
	When I visit the "/attribute/3"
	Then the result page will include text "ldap.example.com ldap3.example.com"
	When I visit the "/certificate/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/certificate/2"
	Then the result page will include text "Page not found"
	When I visit the "/certificate/3"
	Then the result page will include text "Page not found"
	When I visit the "/endpoint/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/endpoint/2"
	Then the result page will include text "Page not found"
	When I visit the "/endpoint/3"
	Then the result page will include text "Page not found"
	When I visit the "/contact/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/contact/2"
	Then the result page will include text "Page not found"
	When I visit the "/contact/3"
	Then the result page will include text "ldap.example.com ldap3.example.com"
	When I visit the "/admin/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/admin/2"
	Then the result page will include text "Page not found"
	When I visit the "/admin/3"
	Then the result page will include text "ldap.example.com ldap3.example.com"
	When I visit the "/metadata/1"
	Then the result page will include text "https://sp.example.org/sp"
	When I visit the "/metadata/2"
	Then the result page will include text "Page not found"
	When I visit the "/metadata/3"
	Then the result page will include text "Page not found"
	When I visit the "/usergroup/1"
	Then the result page will include text "Page not found"
	When I visit the "/usergroup/3"
	Then the result page will include text "ldap.example.com ldap3.example.com"
	When I visit the "/usergroup/4"
	Then the result page will include text "Page not found"
	When I visit the "/attribute/list/"
	Then the result page will include text "Permission denied"
	When I visit the "/certificate/list/"
	Then the result page will include text "Permission denied"
	When I visit the "/sign_encrypt_list/"
	Then the result page will include text "Permission denied"
	When I visit the "/metadata/manage/"
	Then the result page will include text "Permission denied"
	When I visit the "/admin_django/"
	Then the result page will include text "but are not authorized to access this page"

	
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
	When I visit the "/sign_encrypt_list/"
	Then the result page will include text "Service Provider Signing and Encryption"
	When I visit the "/admin_django/"
	Then the result page will include text "Site administration"
	