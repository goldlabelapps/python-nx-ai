"""Queue Routes"""


from fastapi import APIRouter
from .routes.drop import router as drop_router
from .routes.empty import router as empty_router
from .routes.get import router as get_router

from .routes.create import router as create_router

from .routes.import_linkedin import router as import_linkedin_router
from .routes.alter import router as alter_router

router = APIRouter()
router.include_router(drop_router)
router.include_router(empty_router)
router.include_router(get_router)
router.include_router(create_router)
router.include_router(import_linkedin_router)
router.include_router(alter_router)