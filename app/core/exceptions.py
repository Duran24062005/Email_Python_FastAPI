"""Custom exceptions for the application."""

from fastapi import HTTPException, status


class MUBEError(Exception):
    """Base exception for MUBE application."""

    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(MUBEError):
    """Raised when a resource is not found."""

    def __init__(self, resource: str = "Resource", identifier: str | int | None = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(message)


class AlreadyExistsError(MUBEError):
    """Raised when trying to create a resource that already exists."""

    def __init__(self, resource: str = "Resource", field: str = "id", value: str = ""):
        message = f"{resource} with {field} '{value}' already exists"
        super().__init__(message)


class UnauthorizedError(MUBEError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message)


class ForbiddenError(MUBEError):
    """Raised when user lacks permission."""

    def __init__(self, message: str = "You don't have permission to perform this action"):
        super().__init__(message)


class ValidationError(MUBEError):
    """Raised when data validation fails."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message)


# HTTP Exception helpers
def http_not_found(detail: str = "Resource not found") -> HTTPException:
    """Create a 404 Not Found HTTP exception."""
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def http_unauthorized(detail: str = "Invalid credentials") -> HTTPException:
    """Create a 401 Unauthorized HTTP exception."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def http_forbidden(detail: str = "Access forbidden") -> HTTPException:
    """Create a 403 Forbidden HTTP exception."""
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def http_bad_request(detail: str = "Bad request") -> HTTPException:
    """Create a 400 Bad Request HTTP exception."""
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def http_conflict(detail: str = "Resource already exists") -> HTTPException:
    """Create a 409 Conflict HTTP exception."""
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)