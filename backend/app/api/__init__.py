"""API routes"""
from fastapi import APIRouter
# from .ingest import router as ingest_router  # Disabled for dev mode (requires Celery)
from .upload import router as upload_router
from .reviews import router as reviews_router

# Main API router
api_router = APIRouter()

# Include sub-routers
# api_router.include_router(ingest_router, prefix="/ingest", tags=["ingest"])  # Disabled for dev
api_router.include_router(upload_router, prefix="/upload", tags=["upload"])
api_router.include_router(reviews_router, prefix="/reviews", tags=["reviews"])

__all__ = ["api_router"]
