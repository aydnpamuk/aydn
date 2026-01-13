"""
Amazon review scraper worker tasks
"""
import time
import logging
from typing import List, Dict
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from tenacity import retry, stop_after_attempt, wait_exponential
from sqlalchemy.orm import Session
import random

from .celery_app import celery_app
from ..database import SessionLocal
from ..models import Review, Product, ScrapeJob, JobStatus
from ..utils.parser import AmazonReviewParser
from ..utils.sentiment import analyze_sentiment
from ..config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="scrape_reviews_task")
def scrape_reviews_task(self, job_id: str):
    """
    Celery task to scrape Amazon reviews

    Args:
        job_id: Scrape job ID to process
    """
    db = SessionLocal()
    try:
        # Get job from database
        job = db.query(ScrapeJob).filter(ScrapeJob.job_id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return {"status": "error", "message": "Job not found"}

        # Update job status
        job.status = JobStatus.PROCESSING
        job.total_products = len(job.asins)
        db.commit()

        # Initialize scraper
        scraper = AmazonReviewScraper(
            marketplace=job.marketplace,
            rating_filter=job.rating_filter,
            db_session=db,
        )

        # Process each ASIN
        for idx, asin in enumerate(job.asins):
            try:
                logger.info(f"Processing ASIN {idx + 1}/{len(job.asins)}: {asin}")

                # Scrape reviews
                review_count = scraper.scrape_product_reviews(asin)

                # Update progress
                job.processed_products = idx + 1
                job.total_reviews += review_count
                job.progress = int((idx + 1) / len(job.asins) * 100)
                db.commit()

                # Update task state for progress tracking
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": idx + 1,
                        "total": len(job.asins),
                        "status": f"Processed {asin}",
                    },
                )

            except Exception as e:
                logger.error(f"Error processing ASIN {asin}: {e}")
                job.error_message = f"Error on {asin}: {str(e)}"
                db.commit()
                continue

        # Mark job as completed
        job.status = JobStatus.COMPLETED
        db.commit()

        return {
            "status": "completed",
            "total_reviews": job.total_reviews,
            "processed_products": job.processed_products,
        }

    except Exception as e:
        logger.error(f"Fatal error in job {job_id}: {e}")
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.commit()
        return {"status": "failed", "error": str(e)}

    finally:
        db.close()


class AmazonReviewScraper:
    """
    Amazon review scraper using Playwright

    IMPORTANT: This scraper is designed for:
    - User-controlled, manual execution
    - Limited, respectful scraping
    - Research and analysis purposes
    - Compliance with rate limits

    NOT for:
    - Aggressive automated scraping
    - Commercial data resale
    - Bypassing Amazon's terms of service
    """

    def __init__(self, marketplace: str, rating_filter: str, db_session: Session):
        self.marketplace = marketplace
        self.rating_filter = rating_filter
        self.db = db_session
        self.parser = AmazonReviewParser(marketplace)
        self.domain = settings.AMAZON_MARKETPLACES.get(marketplace, "amazon.com")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=30),
        reraise=True,
    )
    def scrape_product_reviews(self, asin: str, max_pages: int = 10) -> int:
        """
        Scrape reviews for a single product

        Args:
            asin: Product ASIN
            max_pages: Maximum review pages to scrape (default 10 for safety)

        Returns:
            Number of reviews scraped
        """
        review_count = 0

        with sync_playwright() as p:
            # Launch browser in non-headless mode for transparency
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent=settings.SCRAPER_USER_AGENT,
                viewport={"width": 1920, "height": 1080},
            )
            page = context.new_page()

            try:
                # Get or create product
                product = self._get_or_create_product(asin)

                # Build review URL
                review_url = f"https://{self.domain}/product-reviews/{asin}"
                logger.info(f"Navigating to: {review_url}")

                # Navigate to reviews page
                page.goto(review_url, wait_until="domcontentloaded", timeout=30000)

                # Wait for reviews to load
                time.sleep(random.uniform(2, 4))

                # Apply rating filter if needed
                if self.rating_filter != "all":
                    self._apply_rating_filter(page)
                    time.sleep(random.uniform(2, 3))

                # Scrape first page
                page_html = page.content()
                reviews = self.parser.parse_html(page_html, asin)
                review_count += self._save_reviews(reviews, product.id)

                # Scrape additional pages (limited for safety)
                for page_num in range(2, min(max_pages + 1, 11)):
                    try:
                        # Find and click "Next page" button
                        next_button = page.query_selector('li.a-last a')
                        if not next_button:
                            logger.info(f"No more pages for ASIN {asin}")
                            break

                        # Respectful delay between pages
                        delay = random.uniform(
                            settings.SCRAPER_DELAY_MIN, settings.SCRAPER_DELAY_MAX
                        )
                        logger.info(f"Waiting {delay:.1f}s before next page...")
                        time.sleep(delay)

                        # Click next page
                        next_button.click()
                        time.sleep(random.uniform(2, 4))

                        # Parse reviews from current page
                        page_html = page.content()
                        reviews = self.parser.parse_html(page_html, asin)
                        review_count += self._save_reviews(reviews, product.id)

                        logger.info(f"Scraped page {page_num} for ASIN {asin}")

                    except PlaywrightTimeout:
                        logger.warning(f"Timeout on page {page_num} for ASIN {asin}")
                        break
                    except Exception as e:
                        logger.error(f"Error on page {page_num}: {e}")
                        break

            finally:
                browser.close()

        logger.info(f"Scraped {review_count} reviews for ASIN {asin}")
        return review_count

    def _apply_rating_filter(self, page):
        """Apply rating filter on review page"""
        try:
            if self.rating_filter == "negative":
                # Click on critical/negative stars (1-4 stars)
                # Try different selectors for star filters
                selectors = [
                    'a[aria-label*="star"]',
                    'div[data-reftag*="cm_cr_arp_d_viewopt_sr"] a',
                ]

                for selector in selectors:
                    elements = page.query_selector_all(selector)
                    if elements:
                        # Click on 1-4 star filters
                        for elem in elements[:4]:  # First 4 are usually 1-4 stars
                            try:
                                elem.click()
                                break
                            except:
                                continue
                        break

            elif self.rating_filter == "positive":
                # Click on positive stars (4-5 stars)
                selectors = [
                    'a[aria-label*="5 star"]',
                    'a[aria-label*="4 star"]',
                ]

                for selector in selectors:
                    elem = page.query_selector(selector)
                    if elem:
                        elem.click()
                        break

        except Exception as e:
            logger.warning(f"Could not apply rating filter: {e}")

    def _get_or_create_product(self, asin: str) -> Product:
        """Get existing product or create new one"""
        product = (
            self.db.query(Product)
            .filter(Product.asin == asin, Product.marketplace == self.marketplace)
            .first()
        )

        if not product:
            product = Product(
                asin=asin,
                marketplace=self.marketplace,
                url=f"https://{self.domain}/dp/{asin}",
            )
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)

        return product

    def _save_reviews(self, reviews: List[Dict], product_id: int) -> int:
        """Save parsed reviews to database"""
        saved_count = 0

        for review_data in reviews:
            try:
                # Check if review already exists
                existing = (
                    self.db.query(Review)
                    .filter(Review.review_id == review_data["review_id"])
                    .first()
                )

                if existing:
                    continue

                # Analyze sentiment
                sentiment = analyze_sentiment(review_data.get("text"))

                # Create review object
                review = Review(
                    product_id=product_id,
                    review_id=review_data["review_id"],
                    asin=review_data["asin"],
                    rating=review_data["rating"],
                    title=review_data.get("title"),
                    text=review_data.get("text"),
                    verified_purchase=review_data.get("verified_purchase", False),
                    author_name=review_data.get("author_name"),
                    review_date=review_data.get("review_date"),
                    helpful_votes=review_data.get("helpful_votes", 0),
                    marketplace=review_data["marketplace"],
                    sentiment_score=sentiment["sentiment_score"],
                    sentiment_label=sentiment["sentiment_label"],
                    is_negative=(review_data["rating"] <= 4),
                    is_positive=(review_data["rating"] >= 4),
                )

                self.db.add(review)
                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving review: {e}")
                continue

        # Commit batch
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error committing reviews: {e}")
            self.db.rollback()
            saved_count = 0

        return saved_count
