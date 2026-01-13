"""
Review and Product API schemas
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List


class ProductBase(BaseModel):
    """Base product schema"""

    asin: str = Field(..., min_length=10, max_length=20)
    marketplace: str = Field(..., min_length=2, max_length=10)
    title: Optional[str] = None
    url: Optional[str] = None
    average_rating: Optional[float] = Field(None, ge=0, le=5)
    total_reviews: Optional[int] = Field(None, ge=0)


class ProductResponse(ProductBase):
    """Product response schema"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewBase(BaseModel):
    """Base review schema"""

    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=500)
    text: Optional[str] = None
    verified_purchase: bool = False
    author_name: Optional[str] = Field(None, max_length=200)
    review_date: Optional[datetime] = None
    helpful_votes: int = Field(0, ge=0)


class ReviewCreate(ReviewBase):
    """Schema for creating a review"""

    review_id: str = Field(..., max_length=50)
    asin: str = Field(..., min_length=10, max_length=20)
    marketplace: str = Field(..., min_length=2, max_length=10)
    author_id: Optional[str] = None


class ReviewResponse(ReviewBase):
    """Review response schema"""

    id: int
    review_id: str
    asin: str
    marketplace: str
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    is_negative: bool
    is_positive: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewFilter(BaseModel):
    """Review filter parameters"""

    asin: Optional[str] = None
    marketplace: Optional[str] = None
    rating_min: Optional[int] = Field(None, ge=1, le=5)
    rating_max: Optional[int] = Field(None, ge=1, le=5)
    sentiment: Optional[str] = None  # negative, neutral, positive
    verified_only: bool = False
    sort_by: str = Field("review_date", pattern="^(review_date|rating|helpful_votes)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


class ReviewListResponse(BaseModel):
    """Paginated review list response"""

    items: List[ReviewResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
