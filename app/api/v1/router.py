"""API v1 main router."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, emails, health, users
from app.api.v1.endpoints.routes.email_routes import email_router

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(emails.router, prefix="/confirm-emails", tags=["Confirm Emails"])
api_router.include_router(email_router, prefix="/emails", tags=["Emails Domain Routes"])