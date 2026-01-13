"""
Review query and analytics endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from typing import Optional, List
import math

from ..database import get_db
from ..schemas import ReviewResponse, ReviewListResponse, ProductResponse
from ..models import Review, Product

router = APIRouter()


@router.get("/", response_model=ReviewListResponse)
async def get_reviews(
    asin: Optional[str] = Query(None, description="Filter by ASIN"),
    marketplace: Optional[str] = Query(None, description="Filter by marketplace"),
    rating_min: Optional[int] = Query(None, ge=1, le=5, description="Minimum rating"),
    rating_max: Optional[int] = Query(None, ge=1, le=5, description="Maximum rating"),
    sentiment: Optional[str] = Query(
        None, description="Filter by sentiment (negative, neutral, positive)"
    ),
    verified_only: bool = Query(False, description="Only verified purchases"),
    sort_by: str = Query("review_date", description="Sort field (review_date, rating, helpful_votes)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Get reviews with filtering and pagination

    This endpoint supports comprehensive filtering:
    - By ASIN and marketplace
    - By rating range (e.g., rating_max=4 for negative reviews)
    - By sentiment (negative/neutral/positive)
    - Verified purchases only
    - Sorting by date, rating, or helpfulness

    Example queries:
    - Negative reviews: `?rating_max=4`
    - Positive reviews: `?rating_min=4`
    - Latest negative reviews: `?rating_max=4&sort_by=review_date`
    """
    # Build query
    query = db.query(Review)

    # Apply filters
    if asin:
        query = query.filter(Review.asin == asin)

    if marketplace:
        query = query.filter(Review.marketplace == marketplace)

    if rating_min:
        query = query.filter(Review.rating >= rating_min)

    if rating_max:
        query = query.filter(Review.rating <= rating_max)

    if sentiment:
        query = query.filter(Review.sentiment_label == sentiment)

    if verified_only:
        query = query.filter(Review.verified_purchase == True)

    # Get total count
    total = query.count()

    # Apply sorting
    sort_column = {
        "review_date": Review.review_date,
        "rating": Review.rating,
        "helpful_votes": Review.helpful_votes,
    }.get(sort_by, Review.review_date)

    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # Apply pagination
    offset = (page - 1) * page_size
    reviews = query.offset(offset).limit(page_size).all()

    # Calculate pagination metadata
    total_pages = math.ceil(total / page_size)

    return ReviewListResponse(
        items=reviews,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=(page < total_pages),
        has_prev=(page > 1),
    )


@router.get("/stats")
async def get_review_stats(
    asin: Optional[str] = Query(None),
    marketplace: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get review statistics

    Returns aggregated statistics including:
    - Total reviews
    - Average rating
    - Rating distribution (1-5 stars)
    - Sentiment distribution
    - Verified purchase percentage

    Can be filtered by ASIN and marketplace for product-specific stats.
    """
    # Build base query
    query = db.query(Review)

    if asin:
        query = query.filter(Review.asin == asin)

    if marketplace:
        query = query.filter(Review.marketplace == marketplace)

    # Total reviews
    total_reviews = query.count()

    if total_reviews == 0:
        return {
            "total_reviews": 0,
            "average_rating": None,
            "rating_distribution": {},
            "sentiment_distribution": {},
            "verified_percentage": 0,
        }

    # Average rating
    avg_rating = db.query(func.avg(Review.rating)).filter(
        Review.id.in_(query.with_entities(Review.id))
    ).scalar()

    # Rating distribution
    rating_dist = (
        query.with_entities(Review.rating, func.count(Review.id))
        .group_by(Review.rating)
        .all()
    )
    rating_distribution = {str(rating): count for rating, count in rating_dist}

    # Sentiment distribution
    sentiment_dist = (
        query.with_entities(Review.sentiment_label, func.count(Review.id))
        .group_by(Review.sentiment_label)
        .all()
    )
    sentiment_distribution = {label: count for label, count in sentiment_dist if label}

    # Verified purchase percentage
    verified_count = query.filter(Review.verified_purchase == True).count()
    verified_percentage = (verified_count / total_reviews * 100) if total_reviews > 0 else 0

    return {
        "total_reviews": total_reviews,
        "average_rating": round(float(avg_rating), 2) if avg_rating else None,
        "rating_distribution": rating_distribution,
        "sentiment_distribution": sentiment_distribution,
        "verified_percentage": round(verified_percentage, 2),
    }


@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    marketplace: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get all products with reviews

    Returns a list of products that have been scraped/uploaded.
    Useful for building product selection dropdowns in the UI.
    """
    query = db.query(Product)

    if marketplace:
        query = query.filter(Product.marketplace == marketplace)

    products = query.order_by(desc(Product.updated_at)).limit(limit).all()

    return products


@router.get("/compare")
async def compare_products(
    asins: str = Query(..., description="Comma-separated list of ASINs to compare"),
    marketplace: str = Query(..., description="Marketplace code"),
    db: Session = Depends(get_db),
):
    """
    Compare multiple products

    Compare review statistics for multiple products side-by-side.
    Useful for competitor analysis.

    Args:
        asins: Comma-separated ASINs (e.g., "B08N5WRWNW,B07XQK7H3P")
        marketplace: Marketplace code

    Returns:
        Comparison data for each product
    """
    asin_list = [a.strip() for a in asins.split(",") if a.strip()]

    if len(asin_list) < 2:
        raise HTTPException(
            status_code=400, detail="At least 2 ASINs required for comparison"
        )

    if len(asin_list) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 ASINs allowed")

    comparison_data = []

    for asin in asin_list:
        # Get product
        product = (
            db.query(Product)
            .filter(Product.asin == asin, Product.marketplace == marketplace)
            .first()
        )

        if not product:
            comparison_data.append(
                {"asin": asin, "error": "Product not found", "stats": None}
            )
            continue

        # Get review query
        review_query = db.query(Review).filter(
            Review.asin == asin, Review.marketplace == marketplace
        )

        # Calculate stats
        total_reviews = review_query.count()
        avg_rating = (
            db.query(func.avg(Review.rating))
            .filter(Review.asin == asin, Review.marketplace == marketplace)
            .scalar()
        )

        # Negative vs positive
        negative_count = review_query.filter(Review.rating <= 4).count()
        positive_count = review_query.filter(Review.rating >= 4).count()

        # Top negative themes (most common words in negative reviews)
        negative_reviews = (
            review_query.filter(Review.rating <= 4)
            .order_by(desc(Review.helpful_votes))
            .limit(5)
            .all()
        )

        comparison_data.append(
            {
                "asin": asin,
                "title": product.title,
                "stats": {
                    "total_reviews": total_reviews,
                    "average_rating": round(float(avg_rating), 2) if avg_rating else None,
                    "negative_count": negative_count,
                    "positive_count": positive_count,
                    "negative_percentage": round(negative_count / total_reviews * 100, 2)
                    if total_reviews > 0
                    else 0,
                },
                "sample_negative_reviews": [
                    {"rating": r.rating, "title": r.title, "text": r.text[:200]}
                    for r in negative_reviews
                ],
            }
        )

    return {"marketplace": marketplace, "products": comparison_data}


@router.delete("/{review_id}", status_code=204)
async def delete_review(review_id: str, db: Session = Depends(get_db)):
    """
    Delete a review

    Args:
        review_id: Amazon review ID to delete
    """
    review = db.query(Review).filter(Review.review_id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    db.delete(review)
    db.commit()

    return None
