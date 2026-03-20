from app import __version__
"""API route definitions for NX AI."""

import os
import time

import psycopg2
from dotenv import load_dotenv

from fastapi import APIRouter, Depends

from app.api.db import get_db_connection
from app.api.schemas import EchoRequest, EchoResponse

router = APIRouter()

from app.api.root import router as root_router
from app.api.health import router as health_router
from app.api.echo import router as echo_router
from app.api.import_csv import router as import_csv_router

router.include_router(root_router)
router.include_router(health_router)
router.include_router(echo_router)
router.include_router(import_csv_router)

