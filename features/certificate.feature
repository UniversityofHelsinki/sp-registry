Feature: Certificates
	Adding certificates to registry 

Scenario: Certificate additions
	Given test environment with logged in user exists
	When clicking link with text "https://sp.example.org/sp"
	And clicking visible link with text "Certificates"
	And filling certificate form with invalid certificate
	Then the result page will include text "Unable to load certificate"
	When filling certificate form with valid certificate
	Then the result page will include text "Jan. 14, 2028,"
	And the result page will include text "4096"
	When filling certificate form with valid certificate
	Then the result page will include text "Certificate already exists"
	And count of tag "td" is "6"
	When clicking visible link with text "sp.example.org"
	Then the result page will include text "11789430449918610071"
	Then the result page will include text "ff94c5f27e1255c714533e7078b33fce21fe00935e375e66dc79ff07eb5d88f6"
	Then the result page will include text "sp.example.org"
	When clicking visible link with text "Certificates"
	When removing first certificate
	Then count of tag "td" is "0"
	