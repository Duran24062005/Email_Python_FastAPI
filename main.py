from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from config.config import app_config
from routes.email_routes import email_router
from middlewares.cors import app_cors

app = FastAPI(
    title=app_config["APP_NAME"],
    version=app_config["VERSION"],
    description=app_config["DESCRIPTION"],
    contact={
        "name": app_config["CONTACT_NAME"]
    }
)

app_cors(app)

app.mount("/public", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

app.include_router(email_router, prefix="/emails")