"""
Product ingest and scraping endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTask
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from ..database import get_db
from ..schemas import ScrapeJobCreate, ScrapeJobResponse
from ..models import ScrapeJob, JobStatus
from ..workers.scraper import scrape_reviews_task
from ..utils.parser import AmazonReviewParser

router = APIRouter()


@router.post("/", response_model=ScrapeJobResponse, status_code=202)
async def create_scrape_job(
    job_request: ScrapeJobCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new scrape job for Amazon product reviews

    This endpoint creates a scraping job that will be processed asynchronously.
    The job will scrape reviews from the specified products and store them in the database.

    **Important Notes:**
    - Scraping is done respectfully with delays between requests
    - Limited to max 10 products per job
    - Maximum 10 pages per product (for safety and compliance)
    - Runs in non-headless browser mode for transparency
    - User should monitor and control the scraping process

    Returns:
        ScrapeJobResponse: Job details including job_id for status tracking
    """
    # Parse ASINs from URLs
    parser = AmazonReviewParser(job_request.marketplace)
    asins = []

    for url in job_request.product_urls:
        asin = parser.extract_asin_from_url(url)
        if not asin:
            raise HTTPException(status_code=400, detail=f"Could not extract ASIN from: {url}")
        asins.append(asin)

    # Create job record
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    job = ScrapeJob(
        job_id=job_id,
        asins=asins,
        marketplace=job_request.marketplace,
        rating_filter=job_request.rating_filter.value,
        status=JobStatus.PENDING,
        total_products=len(asins),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Dispatch Celery task
    scrape_reviews_task.delay(job_id)

    return job


@router.get("/status/{job_id}", response_model=ScrapeJobResponse)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get the status of a scrape job

    Args:
        job_id: The job ID returned from the create endpoint

    Returns:
        ScrapeJobResponse: Current job status and progress
    """
    job = db.query(ScrapeJob).filter(ScrapeJob.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return job


@router.get("/jobs", response_model=List[ScrapeJobResponse])
async def list_jobs(
    status: str = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    List all scrape jobs

    Args:
        status: Filter by status (pending, processing, completed, failed)
        limit: Maximum number of jobs to return
        offset: Number of jobs to skip

    Returns:
        List of scrape jobs
    """
    query = db.query(ScrapeJob)

    if status:
        try:
            status_enum = JobStatus(status)
            query = query.filter(ScrapeJob.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    query = query.order_by(ScrapeJob.created_at.desc())
    jobs = query.offset(offset).limit(limit).all()

    return jobs


@router.delete("/jobs/{job_id}", status_code=204)
async def cancel_job(job_id: str, db: Session = Depends(get_db)):
    """
    Cancel a pending or processing job

    Args:
        job_id: The job ID to cancel

    Note: This only marks the job as cancelled in the database.
    The actual Celery task may need manual termination if already running.
    """
    job = db.query(ScrapeJob).filter(ScrapeJob.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
        raise HTTPException(
            status_code=400, detail=f"Cannot cancel job with status: {job.status.value}"
        )

    job.status = JobStatus.CANCELLED
    db.commit()

    return None
