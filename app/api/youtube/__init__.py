"""YouTube Routes"""

from fastapi import APIRouter

from .youtube import router as _youtube_router
from .sql.create_tables import router as _create_tables_router
from .sql.empty_tables import router as _empty_tables_router
from .sql.sync import router as _sync_router

youtube_router = APIRouter()
youtube_router.include_router(_youtube_router)
youtube_router.include_router(_create_tables_router)
youtube_router.include_router(_empty_tables_router)
youtube_router.include_router(_sync_router)
