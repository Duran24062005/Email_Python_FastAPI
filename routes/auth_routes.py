from fastapi import APIRouter


auth_roter = APIRouter()


# Public routes
@auth_roter.get('/register', status_code=200)
def register():
    pass

@auth_roter.get('/login', status_code=200)
def login():
    pass


# Private routes
@auth_roter.get('/me', status_code=200)
def me():
    pass

@auth_roter.get('/logout', status_code=200)
def logout():
    pass

@auth_roter.get('/change-password', status_code=200)
def change_password():
    pass