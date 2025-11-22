from fastapi import APIRouter

email_router = APIRouter()


@email_router.get("/", status_code=200)
async def get_emails():
    return {"message": "List of emails"}


@email_router.get("/{email_id}", status_code=200)
async def get_email(email_id: int):
    return {"message": f"Details of email {email_id}"}


@email_router.post("/send", status_code=201)
async def create_email(email: dict):
    return {"message": "Email created successfully"}


@email_router.put("/update/{email_id}", status_code=200)
async def list_emails(id: int, email: dict):
    return {"message": "Listing all emails"}


@email_router.delete("/emails/{email_id}", status_code=200)
async def list_all_emails(id: int):
    return {"message": "Listing all emails"}