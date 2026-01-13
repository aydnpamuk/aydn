"""API schemas"""
from .review import (
    ReviewBase,
    ReviewCreate,
    ReviewResponse,
    ProductBase,
    ProductResponse,
    ReviewListResponse,
)
from .job import (
    ScrapeJobCreate,
    ScrapeJobResponse,
    JobStatus,
    UploadRequest,
)

__all__ = [
    "ReviewBase",
    "ReviewCreate",
    "ReviewResponse",
    "ProductBase",
    "ProductResponse",
    "ReviewListResponse",
    "ScrapeJobCreate",
    "ScrapeJobResponse",
    "JobStatus",
    "UploadRequest",
]
