"""
Scraping job tracking model
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum as SQLEnum
from datetime import datetime
from enum import Enum
from ..database import Base


class JobStatus(str, Enum):
    """Job status enumeration"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScrapeJob(Base):
    """Track scraping job status and progress"""

    __tablename__ = "scrape_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, nullable=False, index=True)

    # Job configuration
    asins = Column(JSON, nullable=False)  # List of ASINs
    marketplace = Column(String(10), nullable=False)
    rating_filter = Column(String(20))  # "negative" (<=4), "positive" (>=4), "all"

    # Job status
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    progress = Column(Integer, default=0)  # 0-100%
    total_products = Column(Integer, default=0)
    processed_products = Column(Integer, default=0)
    total_reviews = Column(Integer, default=0)

    # Error handling
    error_message = Column(String(1000))
    retry_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ScrapeJob(job_id={self.job_id}, status={self.status})>"
