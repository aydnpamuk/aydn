"""
Manual upload endpoints for HTML/CSV content
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import csv
from io import StringIO

from ..database import get_db
from ..schemas import UploadRequest
from ..models import Product, Review
from ..utils.parser import AmazonReviewParser
from ..utils.sentiment import analyze_sentiment

router = APIRouter()


@router.post("/html")
async def upload_html(
    asin: str = Form(...),
    marketplace: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload Amazon review page HTML for parsing

    This is the SAFE and COMPLIANT way to import reviews:
    1. User manually opens Amazon review page in browser
    2. User saves the page as HTML (Ctrl+S / Cmd+S)
    3. User uploads the HTML file here

    This method:
    ✅ Fully compliant with Amazon ToS
    ✅ No automated scraping
    ✅ User-controlled data collection
    ✅ Transparent and ethical

    Args:
        asin: Product ASIN
        marketplace: Marketplace code (us, de, uk, etc.)
        file: HTML file from saved Amazon review page

    Returns:
        Summary of parsed reviews
    """
    # Validate file type
    if not file.filename.endswith(".html") and not file.filename.endswith(".htm"):
        raise HTTPException(status_code=400, detail="File must be HTML format")

    # Read file content
    try:
        content = await file.read()
        html_content = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    # Parse HTML
    parser = AmazonReviewParser(marketplace)
    reviews = parser.parse_html(html_content, asin)

    if not reviews:
        raise HTTPException(
            status_code=400,
            detail="No reviews found in HTML. Make sure you uploaded the full review page.",
        )

    # Get or create product
    product = (
        db.query(Product)
        .filter(Product.asin == asin, Product.marketplace == marketplace)
        .first()
    )

    if not product:
        # Extract product info from HTML
        product_info = parser.extract_product_info(html_content, asin)
        product = Product(
            asin=asin,
            marketplace=marketplace,
            title=product_info.get("title"),
            average_rating=product_info.get("average_rating"),
            total_reviews=product_info.get("total_reviews"),
            url=f"https://{parser.domain_map.get(marketplace, 'amazon.com')}/dp/{asin}",
        )
        db.add(product)
        db.commit()
        db.refresh(product)

    # Save reviews
    saved_count = 0
    duplicate_count = 0

    for review_data in reviews:
        # Check if review already exists
        existing = (
            db.query(Review).filter(Review.review_id == review_data["review_id"]).first()
        )

        if existing:
            duplicate_count += 1
            continue

        # Analyze sentiment
        sentiment = analyze_sentiment(review_data.get("text"))

        # Create review
        review = Review(
            product_id=product.id,
            review_id=review_data["review_id"],
            asin=asin,
            rating=review_data["rating"],
            title=review_data.get("title"),
            text=review_data.get("text"),
            verified_purchase=review_data.get("verified_purchase", False),
            author_name=review_data.get("author_name"),
            review_date=review_data.get("review_date"),
            helpful_votes=review_data.get("helpful_votes", 0),
            marketplace=marketplace,
            sentiment_score=sentiment["sentiment_score"],
            sentiment_label=sentiment["sentiment_label"],
            is_negative=(review_data["rating"] <= 4),
            is_positive=(review_data["rating"] >= 4),
        )

        db.add(review)
        saved_count += 1

    db.commit()

    return {
        "status": "success",
        "message": f"Parsed {len(reviews)} reviews from HTML",
        "saved": saved_count,
        "duplicates": duplicate_count,
        "asin": asin,
        "marketplace": marketplace,
    }


@router.post("/csv")
async def upload_csv(
    marketplace: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload reviews from CSV file

    Expected CSV format:
    asin,review_id,rating,title,text,author_name,review_date,verified_purchase,helpful_votes

    Args:
        marketplace: Marketplace code (us, de, uk, etc.)
        file: CSV file with review data

    Returns:
        Summary of imported reviews
    """
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be CSV format")

    # Read and parse CSV
    try:
        content = await file.read()
        csv_content = content.decode("utf-8")
        csv_reader = csv.DictReader(StringIO(csv_content))

        reviews_by_asin = {}

        for row in csv_reader:
            asin = row.get("asin", "").strip()
            if not asin:
                continue

            if asin not in reviews_by_asin:
                reviews_by_asin[asin] = []

            reviews_by_asin[asin].append(row)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")

    if not reviews_by_asin:
        raise HTTPException(status_code=400, detail="No valid reviews found in CSV")

    # Process each ASIN
    total_saved = 0
    total_duplicates = 0

    for asin, reviews in reviews_by_asin.items():
        # Get or create product
        product = (
            db.query(Product)
            .filter(Product.asin == asin, Product.marketplace == marketplace)
            .first()
        )

        if not product:
            product = Product(
                asin=asin,
                marketplace=marketplace,
                url=f"https://amazon.com/dp/{asin}",
            )
            db.add(product)
            db.commit()
            db.refresh(product)

        # Save reviews
        for review_data in reviews:
            try:
                review_id = review_data.get("review_id", "").strip()
                if not review_id:
                    continue

                # Check if exists
                existing = db.query(Review).filter(Review.review_id == review_id).first()
                if existing:
                    total_duplicates += 1
                    continue

                # Parse rating
                rating = int(review_data.get("rating", 0))
                if rating < 1 or rating > 5:
                    continue

                # Analyze sentiment
                sentiment = analyze_sentiment(review_data.get("text"))

                # Create review
                review = Review(
                    product_id=product.id,
                    review_id=review_id,
                    asin=asin,
                    rating=rating,
                    title=review_data.get("title", "").strip() or None,
                    text=review_data.get("text", "").strip() or None,
                    verified_purchase=review_data.get("verified_purchase", "").lower()
                    == "true",
                    author_name=review_data.get("author_name", "").strip() or None,
                    helpful_votes=int(review_data.get("helpful_votes", 0)),
                    marketplace=marketplace,
                    sentiment_score=sentiment["sentiment_score"],
                    sentiment_label=sentiment["sentiment_label"],
                    is_negative=(rating <= 4),
                    is_positive=(rating >= 4),
                )

                db.add(review)
                total_saved += 1

            except Exception as e:
                continue

    db.commit()

    return {
        "status": "success",
        "message": f"Imported reviews from CSV",
        "products": len(reviews_by_asin),
        "saved": total_saved,
        "duplicates": total_duplicates,
        "marketplace": marketplace,
    }
