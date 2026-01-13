"""
Job tracking schemas
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RatingFilter(str, Enum):
    """Rating filter options"""

    NEGATIVE = "negative"  # <= 4 stars
    POSITIVE = "positive"  # >= 4 stars
    ALL = "all"


class ScrapeJobCreate(BaseModel):
    """Schema for creating a scrape job"""

    product_urls: List[str] = Field(
        ..., min_items=1, max_items=10, description="List of Amazon product URLs or ASINs"
    )
    marketplace: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="Amazon marketplace (us, de, uk, fr, it, es, ca, jp)",
    )
    rating_filter: RatingFilter = Field(
        RatingFilter.NEGATIVE, description="Filter reviews by rating"
    )
    max_reviews_per_product: Optional[int] = Field(
        None, ge=10, le=5000, description="Maximum reviews to scrape per product"
    )

    @validator("product_urls")
    def validate_urls(cls, v):
        """Validate product URLs or ASINs"""
        validated = []
        for url in v:
            url = url.strip()
            if not url:
                continue

            # Check if it's an ASIN (alphanumeric, 10 chars)
            if len(url) == 10 and url.isalnum():
                validated.append(url)
            # Check if it's a valid Amazon URL
            elif "amazon." in url and ("/dp/" in url or "/product/" in url):
                validated.append(url)
            else:
                raise ValueError(f"Invalid product URL or ASIN: {url}")

        if not validated:
            raise ValueError("At least one valid product URL or ASIN required")

        return validated

    @validator("marketplace")
    def validate_marketplace(cls, v):
        """Validate marketplace code"""
        valid_marketplaces = ["us", "de", "uk", "fr", "it", "es", "ca", "jp"]
        if v.lower() not in valid_marketplaces:
            raise ValueError(
                f"Invalid marketplace. Must be one of: {', '.join(valid_marketplaces)}"
            )
        return v.lower()


class ScrapeJobResponse(BaseModel):
    """Scrape job response schema"""

    id: int
    job_id: str
    asins: List[str]
    marketplace: str
    rating_filter: str
    status: JobStatus
    progress: int
    total_products: int
    processed_products: int
    total_reviews: int
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class UploadRequest(BaseModel):
    """Schema for manual HTML/CSV upload"""

    asin: str = Field(..., min_length=10, max_length=20)
    marketplace: str = Field(..., min_length=2, max_length=10)
    content_type: str = Field(..., pattern="^(html|csv)$")
    content: str = Field(..., min_length=10, description="HTML or CSV content")

    @validator("marketplace")
    def validate_marketplace(cls, v):
        """Validate marketplace code"""
        valid_marketplaces = ["us", "de", "uk", "fr", "it", "es", "ca", "jp"]
        if v.lower() not in valid_marketplaces:
            raise ValueError(
                f"Invalid marketplace. Must be one of: {', '.join(valid_marketplaces)}"
            )
        return v.lower()
