"""Email API endpoints."""

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentActiveUser, DBSession
from app.core.exceptions import NotFoundError, ValidationError, http_bad_request, http_not_found
from app.schemas.email_schema import EmailCreate, EmailResponse
from app.repositories.email_repository import EmailRepository
from app.utils.smtp_email_sender import SMTPEmailSender

router = APIRouter()


@router.post(
    "/send",
    response_model=EmailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send email",
    description="Send an email to a recipient.",
)
async def send_email(
    email_data: EmailCreate,
    current_user: CurrentActiveUser,
    db: DBSession,
) -> EmailResponse:
    """Send an email as the current authenticated user."""
    try:
        email_repo = EmailRepository(db)
        
        # Create email with user_id
        from app.models.email_model import Email, EmailStatus
        email = Email(
            user_id=current_user.id,
            recipient=email_data.recipient,
            subject=email_data.subject,
            body=email_data.body,
            html_body=email_data.html_body,
            status=EmailStatus.PENDING,
        )
        
        db.add(email)
        await db.commit()
        await db.refresh(email)
        
        return EmailResponse.model_validate(email)
    except ValidationError as e:
        raise http_bad_request(e.message)


@router.get(
    "",
    response_model=list[EmailResponse],
    status_code=status.HTTP_200_OK,
    summary="List emails",
    description="Get paginated list of emails sent by current user.",
)
async def list_emails(
    current_user: CurrentActiveUser,
    db: DBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> list[EmailResponse]:
    """Get list of emails sent by current user."""
    try:
        email_repo = EmailRepository(db)
        
        # Get emails for current user (filtered by user_id)
        emails = await email_repo.get_all(skip=skip, limit=limit)
        # Filter by current user
        user_emails = [e for e in emails if e.user_id == current_user.id]
        return [EmailResponse.model_validate(email) for email in user_emails]
    except ValidationError as e:
        raise http_bad_request(e.message)


@router.get(
    "/{email_id}",
    response_model=EmailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get email",
    description="Get details of a specific email.",
)
async def get_email(
    email_id: int,
    current_user: CurrentActiveUser,
    db: DBSession,
) -> EmailResponse:
    """Get email details."""
    try:
        email_repo = EmailRepository(db)
        
        email = await email_repo.get_by_id(email_id)
        if email is None:
            raise NotFoundError("Email", email_id)
        
        # Verify ownership
        if email.user_id != current_user.id:
            raise NotFoundError("Email", email_id)
        
        return EmailResponse.model_validate(email)
    except NotFoundError as e:
        raise http_not_found(e.message)
