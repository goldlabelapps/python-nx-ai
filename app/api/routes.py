from app import __version__
"""API routes"""

from dotenv import load_dotenv

from fastapi import APIRouter, Depends

from app.utils.db import get_db_connection
from app.api.schemas import EchoRequest, EchoResponse

router = APIRouter()

from app.api.root import router as root_router
from app.api.health import router as health_router

from app.api.prospects.prospects import router as prospects_router

from app.api.prospects.seed import router as prospects_seed_router
from app.api.prospects.empty import router as prospects_empty_router

router.include_router(root_router)
router.include_router(health_router)
router.include_router(prospects_router)
router.include_router(prospects_seed_router)
router.include_router(prospects_empty_router)