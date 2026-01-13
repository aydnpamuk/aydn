"""
Bulk review import endpoint for Chrome Extension
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel, Field

from ..database import get_db
from ..models import Product, Review
from ..utils.sentiment import analyze_sentiment
from datetime import datetime

router = APIRouter()


class BulkReview(BaseModel):
    """Single review from Chrome extension"""

    review_id: str
    rating: int = Field(..., ge=1, le=5)
    title: str | None = None
    text: str | None = None
    author_name: str | None = None
    review_date: str | None = None
    verified_purchase: bool = False
    helpful_votes: int = 0
    marketplace: str
    asin: str


class ProductInfo(BaseModel):
    """Product information from Chrome extension"""

    asin: str
    title: str | None = None
    average_rating: float | None = None
    total_reviews: int | None = None
    marketplace: str
    url: str


class BulkImportRequest(BaseModel):
    """Bulk import request from Chrome extension"""

    product: ProductInfo
    reviews: List[BulkReview]


@router.post("/bulk")
async def bulk_import_reviews(
    request: BulkImportRequest, db: Session = Depends(get_db)
):
    """
    Bulk import reviews from Chrome Extension

    This endpoint is specifically designed for the AYDN Chrome Extension
    to import reviews collected directly from Amazon pages.

    The extension runs in the user's browser, making this approach:
    - Fully compliant (user's own browsing)
    - Ethical (no automated scraping)
    - User-controlled (user initiates collection)

    Args:
        request: Product info and list of reviews
        db: Database session

    Returns:
        Summary of import operation
    """
    product_info = request.product
    reviews_data = request.reviews

    if not reviews_data:
        raise HTTPException(status_code=400, detail="No reviews provided")

    # Get or create product
    product = (
        db.query(Product)
        .filter(
            Product.asin == product_info.asin,
            Product.marketplace == product_info.marketplace,
        )
        .first()
    )

    if not product:
        product = Product(
            asin=product_info.asin,
            marketplace=product_info.marketplace,
            title=product_info.title,
            average_rating=product_info.average_rating,
            total_reviews=product_info.total_reviews,
            url=product_info.url,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
    else:
        # Update product info if provided
        if product_info.title:
            product.title = product_info.title
        if product_info.average_rating:
            product.average_rating = product_info.average_rating
        if product_info.total_reviews:
            product.total_reviews = product_info.total_reviews
        db.commit()

    # Import reviews
    saved_count = 0
    duplicate_count = 0
    error_count = 0

    for review_data in reviews_data:
        try:
            # Check if review already exists
            existing = (
                db.query(Review)
                .filter(Review.review_id == review_data.review_id)
                .first()
            )

            if existing:
                duplicate_count += 1
                continue

            # Analyze sentiment
            sentiment = analyze_sentiment(review_data.text)

            # Parse review date
            review_date = None
            if review_data.review_date:
                try:
                    review_date = datetime.fromisoformat(
                        review_data.review_date
                    ).date()
                except:
                    pass

            # Create review
            review = Review(
                product_id=product.id,
                review_id=review_data.review_id,
                asin=product_info.asin,
                rating=review_data.rating,
                title=review_data.title,
                text=review_data.text,
                verified_purchase=review_data.verified_purchase,
                author_name=review_data.author_name,
                review_date=review_date,
                helpful_votes=review_data.helpful_votes,
                marketplace=product_info.marketplace,
                sentiment_score=sentiment["sentiment_score"],
                sentiment_label=sentiment["sentiment_label"],
                is_negative=(review_data.rating <= 4),
                is_positive=(review_data.rating >= 4),
            )

            db.add(review)
            saved_count += 1

        except Exception as e:
            error_count += 1
            continue

    # Commit all reviews
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}"
        )

    return {
        "status": "success",
        "message": f"Imported {saved_count} reviews",
        "saved": saved_count,
        "duplicates": duplicate_count,
        "errors": error_count,
        "product": {
            "asin": product.asin,
            "title": product.title,
            "marketplace": product.marketplace,
        },
    }


@router.get("/stats")
async def get_extension_stats(db: Session = Depends(get_db)):
    """
    Get statistics for Chrome Extension

    Returns:
        Statistics about imported products and reviews
    """
    total_products = db.query(Product).count()
    total_reviews = db.query(Review).count()
    negative_reviews = db.query(Review).filter(Review.is_negative == True).count()
    positive_reviews = db.query(Review).filter(Review.is_positive == True).count()

    # Get recent products
    recent_products = (
        db.query(Product).order_by(Product.created_at.desc()).limit(5).all()
    )

    return {
        "total_products": total_products,
        "total_reviews": total_reviews,
        "negative_reviews": negative_reviews,
        "positive_reviews": positive_reviews,
        "recent_products": [
            {
                "asin": p.asin,
                "title": p.title,
                "marketplace": p.marketplace,
                "average_rating": p.average_rating,
            }
            for p in recent_products
        ],
    }
