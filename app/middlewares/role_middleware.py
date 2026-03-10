from fastapi import Depends, HTTPException, status
from middlewares.auth_middleware import get_current_active_user
from models.user_models import User, UserRole


async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency que verifica que el usuario autenticado tiene rol ADMIN.
    Úsala en rutas de administración con: Depends(require_admin)
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: se requiere rol de administrador"
        )
    return current_user