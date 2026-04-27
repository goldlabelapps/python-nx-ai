"""GitHub Routes"""

from fastapi import APIRouter
from .github import router as _github_router
from .sql.create_tables import router as _create_tables_router
from .sql.sync import router as _sync_router
from .sql.empty_tables import router as _empty_tables_router

github_router = APIRouter()
github_router.include_router(_github_router)
github_router.include_router(_create_tables_router)
github_router.include_router(_sync_router)
github_router.include_router(_empty_tables_router)
