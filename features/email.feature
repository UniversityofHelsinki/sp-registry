Feature: Email sending
	Testing template based email sending for admins 

Scenario: Admin invitations
	Given test environment with logged in superuser exists
	And email template exists
	When clicking visible link with text "Emails"
	And filling email form
	Then the result page will include text "superuser@example.org"
	When sending email form
	Then the result page will include text "Emails have been sent."
	And message "0" in mailbox should have "This is my message to SP admins." in body
