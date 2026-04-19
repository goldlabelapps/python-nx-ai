from app import __version__
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.utils.make_meta import make_meta
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.api.routes import router

app = FastAPI(
    title="Python°",
    description="FastAPI, Postgres, tsvector",
    version=__version__,
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:1999", 
        "http://localhost:2027",
        "http://localhost:2020",
        "http://localhost:2000",
        "https://goldlabel.pro",
        "https://nx-admin.goldlabel.pro",
        "https://free.goldlabel.pro",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Global validation error handler for make_meta pattern
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    msg = exc.errors()[0]['msg'] if exc.errors() else str(exc)
    return JSONResponse(status_code=422, content={"meta": make_meta("error", msg)})

app.include_router(router)

# Mount static directory
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Favicon route
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(os.path.dirname(__file__), "static", "favicon.ico")
    return FileResponse(favicon_path)
