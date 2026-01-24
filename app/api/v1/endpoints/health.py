"""Health check endpoints."""

from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DBSession

router = APIRouter()


@router.get("/")
async def health_check() -> dict[str, str]:
    """Basic health check."""
    return {"status": "healthy"}


@router.get("/db")
async def database_health_check(db: DBSession) -> dict[str, str]:
    """Database connectivity health check."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}