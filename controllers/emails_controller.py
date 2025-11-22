class EmailController:
    async def get_emails(self):
        return {"message": "List of emails"}

    async def get_email(self, email_id: int):
        return {"message": f"Details of email {email_id}"}

    async def create_email(self, email: dict):
        return {"message": "Email created successfully"}

    async def update_email(self, email_id: int, email: dict):
        return {"message": f"Email {email_id} updated successfully"}

    async def delete_email(self, email_id: int):
        return {"message": f"Email {email_id} deleted successfully"}