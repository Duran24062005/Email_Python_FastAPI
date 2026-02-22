from fastapi import APIRouter, Depends, Query
from controllers.user_controller import UserController
from schemas.user_schemas import UserResponse, UserUpdate, UserList, ChangeStatusRequest, SaveEmailKeyRequest
from schemas.email_schema import EmailList, EmailResponse, SendWithTemplateRequest
from middlewares.auth_middleware import get_current_active_user
from middlewares.role_middleware import require_admin
from models.user_models import User
from dependencies import get_user_controller

user_router = APIRouter()


# ═══════════════════════════════════════════════════════════
# RUTAS PÚBLICAS
# ═══════════════════════════════════════════════════════════

@user_router.get("/verify-email", status_code=200)
async def verify_email(
    token: str = Query(..., description="Token de verificación recibido por email"),
    controller: UserController = Depends(get_user_controller)
):
    """
    Verifica el email del usuario con el token recibido.

    El token se envía automáticamente al registrarse.
    Una vez verificado, `email_verify` pasa a `true`.

    ⚠️ El token expira en 24 horas.
    """
    return await controller.verify_email(token)


# ═══════════════════════════════════════════════════════════
# RUTAS DE USUARIO GENERAL (requieren auth)
# ═══════════════════════════════════════════════════════════

@user_router.get("/me", status_code=200, response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    controller: UserController = Depends(get_user_controller)
):
    """
    Obtiene el perfil del usuario autenticado.

    🔒 Requiere Bearer token válido.
    """
    return await controller.get_my_profile(current_user)


@user_router.get("/me/inbox", status_code=200, response_model=EmailList)
async def get_my_inbox(
    page: int = Query(default=1, ge=1, description="Número de página"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items por página"),
    current_user: User = Depends(get_current_active_user),
    controller: UserController = Depends(get_user_controller)
):
    """
    Bandeja de salida del usuario autenticado.

    Retorna todos los emails que el usuario ha enviado, paginados.

    🔒 Requiere Bearer token válido.
    """
    return await controller.get_my_inbox(current_user, page, page_size)


@user_router.post("/me/inbox/{email_id}/resend", status_code=201, response_model=EmailResponse)
async def resend_email(
    email_id: int,
    current_user: User = Depends(get_current_active_user),
    controller: UserController = Depends(get_user_controller)
):
    """
    Reenvía un email previamente enviado.

    Crea un nuevo registro con el mismo contenido y lo reenvía al mismo destinatario.

    🔒 Solo puedes reenviar tus propios emails.
    """
    return await controller.resend_email(current_user, email_id)


@user_router.post("/me/send-template", status_code=201, response_model=EmailResponse)
async def send_with_template(
    data: SendWithTemplateRequest,
    current_user: User = Depends(get_current_active_user),
    controller: UserController = Depends(get_user_controller)
):
    """
    Envía un email usando una plantilla HTML.

    ### Plantillas disponibles:
    - `welcome.html` → Bienvenida genérica
    - `welcome_educonnect.html` → Bienvenida EduConnect
    - `account_approved.html` → Cuenta aprobada

    ### Variables requeridas por plantilla:
    - **welcome.html**: `nombre`, `empresa`, `mensaje_adicional` (opcional)
    - **account_approved.html**: `nombre`, `empresa`, `role`, `login_link`

    🔒 Requiere Bearer token válido.
    """
    return await controller.send_with_template(current_user, data)


@user_router.put("/me/email-key", status_code=200)
async def save_email_key(
    data: SaveEmailKeyRequest,
    current_user: User = Depends(get_current_active_user),
    controller: UserController = Depends(get_user_controller)
):
    """
    Guarda la contraseña de aplicación SMTP del usuario.

    Permite al usuario enviar emails desde su propio correo en lugar del correo del sistema.

    ### Para Gmail:
    1. Activa la verificación en 2 pasos en tu cuenta Google
    2. Ve a Cuenta → Seguridad → Contraseñas de aplicaciones
    3. Genera una contraseña para "Correo"
    4. Pégala aquí

    ⚠️ Esta clave se almacena en tu perfil y se usará al enviar emails.

    🔒 Requiere Bearer token válido.
    """
    return await controller.save_email_key(current_user, data.email_key)


# ═══════════════════════════════════════════════════════════
# RUTAS DE ADMINISTRADOR
# ═══════════════════════════════════════════════════════════

@user_router.get("/admin/all", status_code=200, response_model=UserList)
async def get_all_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(require_admin),
    controller: UserController = Depends(get_user_controller)
):
    """
    Lista todos los usuarios del sistema (paginado).

    🔒 Solo administradores.
    """
    return await controller.get_all_users(page, page_size)


@user_router.get("/admin/pending", status_code=200, response_model=UserList)
async def get_pending_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(require_admin),
    controller: UserController = Depends(get_user_controller)
):
    """
    Lista usuarios con estado PENDING que esperan aprobación.

    🔒 Solo administradores.
    """
    return await controller.get_pending_users(page, page_size)


@user_router.get("/admin/stats", status_code=200)
async def get_stats(
    current_user: User = Depends(require_admin),
    controller: UserController = Depends(get_user_controller)
):
    """
    Estadísticas generales de usuarios del sistema.

    Retorna: total, pendientes, activos.

    🔒 Solo administradores.
    """
    return await controller.get_stats()


@user_router.get("/admin/{user_id}", status_code=200, response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(require_admin),
    controller: UserController = Depends(get_user_controller)
):
    """
    Obtiene un usuario específico por ID.

    🔒 Solo administradores.
    """
    return await controller.get_user_by_id(user_id)


@user_router.post("/admin/{user_id}/approve", status_code=200)
async def approve_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    controller: UserController = Depends(get_user_controller)
):
    """
    Aprueba un usuario cambiando su estado a ACTIVE.

    Envía un email de notificación automático al usuario aprobado.

    🔒 Solo administradores.
    """
    return await controller.approve_user(user_id)


@user_router.patch("/admin/{user_id}/status", status_code=200)
async def change_user_status(
    user_id: int,
    data: ChangeStatusRequest,
    current_user: User = Depends(require_admin),
    controller: UserController = Depends(get_user_controller)
):
    """
    Cambia el estado de un usuario.

    ### Estados disponibles:
    - `active` → Usuario activo, puede iniciar sesión
    - `pending` → Esperando aprobación del admin
    - `blocked` → Bloqueado, no puede iniciar sesión
    - `deleted` → Eliminado lógicamente

    🔒 Solo administradores.
    """
    return await controller.change_user_status(user_id, data)


@user_router.put("/admin/{user_id}", status_code=200, response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    current_user: User = Depends(require_admin),
    controller: UserController = Depends(get_user_controller)
):
    """
    Actualiza los datos de un usuario (nombre, email, rol, etc.).

    🔒 Solo administradores.
    """
    return await controller.update_user(user_id, data)


@user_router.delete("/admin/{user_id}", status_code=200)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    controller: UserController = Depends(get_user_controller)
):
    """
    Elimina un usuario del sistema.

    🔒 Solo administradores.
    """
    return await controller.delete_user(user_id)