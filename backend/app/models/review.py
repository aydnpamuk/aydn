"""
Review and Product database models
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Product(Base):
    """Product information"""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    asin = Column(String(20), unique=True, nullable=False, index=True)
    marketplace = Column(String(10), nullable=False)  # us, de, uk, fr, etc.
    title = Column(String(500))
    url = Column(String(1000))
    average_rating = Column(Float)
    total_reviews = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(asin={self.asin}, marketplace={self.marketplace})>"


class Review(Base):
    """Customer review data"""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Review identifiers
    review_id = Column(String(50), unique=True, index=True)  # Amazon review ID
    asin = Column(String(20), nullable=False, index=True)

    # Review content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(500))
    text = Column(Text)
    verified_purchase = Column(Boolean, default=False)

    # Author info
    author_name = Column(String(200))
    author_id = Column(String(100))

    # Metadata
    review_date = Column(DateTime)
    helpful_votes = Column(Integer, default=0)
    marketplace = Column(String(10), nullable=False)

    # Processing
    sentiment_score = Column(Float)  # -1 to 1 (negative to positive)
    sentiment_label = Column(String(20))  # negative, neutral, positive
    is_negative = Column(Boolean, index=True)  # rating <= 4
    is_positive = Column(Boolean, index=True)  # rating >= 4

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="reviews")

    # Indexes for common queries
    __table_args__ = (
        Index("idx_rating_negative", "rating", "is_negative"),
        Index("idx_asin_rating", "asin", "rating"),
        Index("idx_marketplace_rating", "marketplace", "rating"),
    )

    def __repr__(self):
        return f"<Review(review_id={self.review_id}, rating={self.rating})>"
