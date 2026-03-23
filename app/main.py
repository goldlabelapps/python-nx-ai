from app import __version__
"""NX-AI Open Source, production ready Python FastAPI/Postgres app for NX"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app import __version__
from app.api.routes import router

app = FastAPI(
    title="NX-AI",
    description="Production-ready Python FastAPI app for NX",
    version=__version__,
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:1999", 
        "https://goldlabel.pro",
        "https://soho.goldlabel.pro",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router)

# Mount static directory
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Favicon route
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(os.path.dirname(__file__), "static", "favicon.ico")
    return FileResponse(favicon_path)
