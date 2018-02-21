Feature: Certificates
	Adding certificates to registry 

Scenario: Certificate additions
	Given test environment with logged in user exists
	When clicking link with text "https://sp.example.org/sp"
	And clicking visible link with text "Certificates"
	And filling certificate form with invalid certificate
	Then the result page will include text "Unable to load certificate"
	When filling certificate form with another invalid certificate
	Then the result page will include text "Unable to load certificate"
	When filling certificate form with valid certificate
	Then the result page will include text "Jan. 14, 2028,"
	And the result page will include text "4096"
	When filling certificate form with valid certificate
	Then the result page will include text "Certificate already exists"
	And count of tag "td" is "6"
	When removing first certificate
	Then count of tag "td" is "0"
