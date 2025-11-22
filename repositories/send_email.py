class SendEmailRepository:
    def __init__(self, email_service):
        self.email_service = email_service

    def send(self, recipient, subject, body):
        self.email_service.send_email(recipient, subject, body)