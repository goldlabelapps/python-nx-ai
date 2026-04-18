"""Register API routes"""

from app import __version__
from fastapi import APIRouter

router = APIRouter()

from app.api.root import router as root_router
from app.utils.health import router as health_router
from app.utils.notify.resend import router as resend_router
from app.api.prompt.prompt import router as prompt_router
from app.api.prompt.linkedin import router as linkedin_router
from app.api.prompt.drop import router as drop_router
from app.api.prospects.prospects import router as prospects_router
from app.api.orders.orders import router as orders_router
from app.api.queue.queue import router as queue_router

router.include_router(root_router)
router.include_router(resend_router)
router.include_router(health_router)
router.include_router(prompt_router)
router.include_router(linkedin_router)
router.include_router(drop_router)
router.include_router(prospects_router)
router.include_router(orders_router)
router.include_router(queue_router)