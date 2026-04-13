from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.config.config import app_config
from app.middlewares.cors import app_cors
from app.routes.email_routes import email_router
from app.routes.auth_routes import auth_router
from app.routes.user_routes import user_router

app = FastAPI(
    title=app_config["APP_NAME"],
    version=app_config["VERSION"],
    description=app_config["DESCRIPTION"],
    contact={
        "name": app_config["CONTACT_NAME"]
    },
    docs_url="/docs",
)

app_cors(app)

@app.get("/")
async def root():
    """
    Ruta raíz que redirige a la documentación interactiva.
    """
    return RedirectResponse(url="/docs")


@app.get("/health")
async def healthcheck():
    """
    Endpoint simple para healthchecks de Docker/orquestadores.
    """
    return {
        "status": "ok",
        "app": app_config["APP_NAME"],
        "version": app_config["VERSION"],
    }

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(email_router, prefix="/emails", tags=["Emails"])
