"""Queue Routes"""


from fastapi import APIRouter
from .routes.drop import router as drop_router
from .routes.empty import router as empty_router

from .routes.get import router as get_router
from .routes.next import router as next_router

from .routes.create import router as create_router
from .routes.delete import router as delete_router

from .csv import linkedin as linkedin_import_router
from .routes.alter import router as alter_router
from .routes.rename_column import router as rename_router

router = APIRouter()
router.include_router(drop_router)
router.include_router(empty_router)
router.include_router(get_router)
router.include_router(next_router)
router.include_router(create_router)
router.include_router(delete_router)
router.include_router(linkedin_import_router.router)

# Register Apollo CSV import route
from .csv import apollo as apollo_import_router
router.include_router(apollo_import_router.router)
router.include_router(alter_router)
router.include_router(rename_router)