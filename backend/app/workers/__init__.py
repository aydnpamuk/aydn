"""Worker tasks"""
from .celery_app import celery_app
from .scraper import scrape_reviews_task

__all__ = ["celery_app", "scrape_reviews_task"]
