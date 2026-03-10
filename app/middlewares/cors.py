from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.config import app_config

def app_cors(app: FastAPI):
    allowed_origins = app_config["CORS_ORIGINS"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
