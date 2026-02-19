from fastapi import APIRouter


auth_roter = APIRouter()


# Public routes
@auth_roter.get('/register', status_code=200)
def register():
    """
    Crea un nuevo usuario.
    args: Datos del usuario.
    ruturn: mensaje de exito en caso de concretar el registro o error sino.
    """
    pass

@auth_roter.get('/login', status_code=200)
def login():
    """
    login: permite al los usuarios registrados y activos acceder al sistema.
    Args: email y password.
    Return: User with access token.
    """
    pass


# Private routes
@auth_roter.get('/me', status_code=200)
def me():
    """
    Me: permite al los usuarios registrados y activos acceder a sus datos de usuario en el sistema.
    Args: Berear token.
    Return: Todos los datos del usuario.
    """
    pass

@auth_roter.get('/logout', status_code=200)
def logout():
    """
    login: permite al los usuarios registrados y activos acceder al sistema
    """
    pass

@auth_roter.get('/change-password', status_code=200)
def change_password():
    """
    login: permite al los usuarios registrados y activos acceder al sistema
    """
    pass