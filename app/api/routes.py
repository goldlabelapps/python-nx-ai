"""API routes"""
from app import __version__
from fastapi import APIRouter

router = APIRouter()

from app.api.root import router as root_router
from app.api.health import router as health_router
from app.api.resend.resend import router as resend_router
from app.api.llm.llm import router as llm_router
from app.api.prospects.prospects import router as prospects_router
from app.api.prospects.flagged import router as flagged_router
from app.api.llm.llm import router as gemini_router

router.include_router(root_router)
router.include_router(resend_router)
router.include_router(health_router)
router.include_router(llm_router)
router.include_router(flagged_router)
router.include_router(prospects_router)
router.include_router(gemini_router)
