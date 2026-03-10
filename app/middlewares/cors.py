from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def app_cors(app: FastAPI):
    # allowed = ["http://127.0.0.1:5500", "http://localhost:3000/"]
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=["http://localhost:3000/"],
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    