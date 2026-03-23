from app import __version__
"""API routes"""

from dotenv import load_dotenv

from fastapi import APIRouter, Depends

from app.api.db import get_db_connection
from app.api.schemas import EchoRequest, EchoResponse

router = APIRouter()

from app.api.root import router as root_router
from app.api.health import router as health_router
from app.api.products.products import router as products_router
from app.api.products.reset import router as reset_router

router.include_router(root_router)
router.include_router(health_router)
router.include_router(products_router)
router.include_router(reset_router)
