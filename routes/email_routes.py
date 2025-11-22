from fastapi import APIRouter

email_router = APIRouter()


@email_router.get("/")
async def get_emails():
    return {"message": "List of emails"}


@email_router.get("/{email_id}")
async def get_email(email_id: int):
    return {"message": f"Details of email {email_id}"}


@email_router.post("/send")
async def create_email():
    return {"message": "Email created successfully"}


@email_router.put("/update/{email_id}")
async def list_emails():
    return {"message": "Listing all emails"}


@email_router.delete("/emails/{email_id}")
async def list_all_emails():
    return {"message": "Listing all emails"}