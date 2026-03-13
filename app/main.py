from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path
from app.config.config import app_config
from app.middlewares.cors import app_cors
from app.config.database.connection import init_db
from app.routes.email_routes import email_router
from app.routes.auth_routes import auth_router
from app.routes.user_routes import user_router

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title=app_config["APP_NAME"],
    version=app_config["VERSION"],
    description=app_config["DESCRIPTION"],
    contact={
        "name": app_config["CONTACT_NAME"]
    },
    docs_url="/docs",
)

# Inicializar base de datos al arrancar
@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    init_db()
    print("✅ Database initialized successfully")

app_cors(app)

app.mount("/public", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def root():
    """
    Ruta raíz que redirige a la documentación interactiva.
    """
    return RedirectResponse(url="/docs")

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(email_router, prefix="/emails", tags=["Emails"])
