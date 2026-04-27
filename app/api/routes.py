"""Register API routes"""

from app import __version__
from fastapi import APIRouter

router = APIRouter()

from app.api.root import router as root_router
from app.utils.health import router as health_router
from app.utils.notify.resend import router as resend_router
from app.api.prompt.prompt import router as prompt_router
from app.api.prompt.empty import router as prompts_empty_router
from app.api.prospects.prospects import router as prospects_router
from app.api.orders.orders import router as orders_router
from app.api.queue import router as queue_router
from app.api.github import github_router

router.include_router(root_router)
router.include_router(resend_router)
router.include_router(health_router)
router.include_router(prompt_router)
router.include_router(prompts_empty_router)
router.include_router(prospects_router)
router.include_router(orders_router)
router.include_router(queue_router)
router.include_router(github_router)