"""API routes"""
from app import __version__
from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from app.utils.db import get_db_connection
from app.api.schemas import EchoRequest, EchoResponse

router = APIRouter()

from app.api.root import router as root_router
from app.api.health import router as health_router
from app.api.resend.resend import router as resend_router
from app.api.llm.llm import router as llm_router
from app.api.prospects.prospects import router as prospects_router
from app.api.prospects.search import router as prospects_search_router
from app.api.llm.llm import router as gemini_router

router.include_router(root_router)
router.include_router(resend_router)
router.include_router(health_router)
router.include_router(llm_router)
router.include_router(prospects_search_router)
router.include_router(prospects_router)
router.include_router(gemini_router)
