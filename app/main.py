from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.config.config import app_config
from app.api.v1.router import api_router
from app.middlewares.cors import app_cors
from app.config.database.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager para eventos de inicio y cierre de la aplicación"""
    # Startup
    await init_db()
    print("✅ Database initialized successfully")
    yield
    # Shutdown (si es necesario en el futuro)
    # Aquí se pueden agregar tareas de limpieza


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title=app_config["APP_NAME"],
    version=app_config["VERSION"],
    description=app_config["DESCRIPTION"],
    contact={
        "name": app_config["CONTACT_NAME"]
    },
    docs_url="/",
    lifespan=lifespan,
)

app_cors(app)

app.mount("/public", StaticFiles(directory=BASE_DIR / "static"), name="static")

@app.get("/")
async def root():
    """
    Ruta raíz que sirve el archivo index.html
    
    Nota: No  es necesario para la documentación de la API
    """
    return FileResponse("static/index.html")

app.include_router(api_router, prefix="/api/v1")