"""Flickr Routes"""

from fastapi import APIRouter

from .flickr import router as _flickr_router
from .sql.create_tables import router as _create_tables_router
from .sql.empty_tables import router as _empty_tables_router
from .sql.sync import router as _sync_router

flickr_router = APIRouter()
flickr_router.include_router(_flickr_router)
flickr_router.include_router(_create_tables_router)
flickr_router.include_router(_empty_tables_router)
flickr_router.include_router(_sync_router)
