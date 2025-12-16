"""
Core data models for Amazon Private Label product analysis.
"""

from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DecisionStatus(str, Enum):
    """Analysis decision status."""

    RED = "RED"  # Reject - Don't proceed
    YELLOW = "YELLOW"  # Caution - Needs deeper investigation
    GREEN = "GREEN"  # Approve - Good opportunity


class Marketplace(str, Enum):
    """Amazon marketplace regions."""

    US = "US"
    UK = "UK"
    DE = "DE"
    FR = "FR"
    IT = "IT"
    ES = "ES"
    CA = "CA"
    JP = "JP"


class ProductData(BaseModel):
    """Raw product data from various API sources."""

    model_config = ConfigDict(extra="allow")

    asin: str = Field(..., description="Amazon Standard Identification Number")
    title: str = Field(..., description="Product title")
    price: float = Field(..., description="Current price")
    marketplace: Marketplace = Field(default=Marketplace.US)

    # Helium 10 data
    h10_monthly_revenue: Optional[float] = None
    h10_monthly_sales: Optional[int] = None
    h10_review_count: Optional[int] = None
    h10_rating: Optional[float] = None
    h10_title_density: Optional[float] = None
    h10_cpr: Optional[int] = None  # Cerebro Product Rank

    # SellerSprite data
    ss_click_concentration: Optional[float] = None  # Top 3 click share
    ss_search_volume: Optional[int] = None  # Monthly search volume
    ss_organic_traffic_ratio: Optional[float] = None
    ss_sponsored_traffic_ratio: Optional[float] = None

    # Keepa data
    keepa_avg_price_30d: Optional[float] = None
    keepa_avg_price_90d: Optional[float] = None
    keepa_sales_rank: Optional[int] = None  # BSR
    keepa_bsr_drops_30d: Optional[int] = None
    keepa_seller_count: Optional[int] = None
    keepa_buy_box_owner: Optional[str] = None


class KeywordData(BaseModel):
    """Keyword analysis data."""

    keyword: str = Field(..., description="Target keyword")
    exact_search_volume: int = Field(..., description="Monthly exact search volume")
    broad_search_volume: Optional[int] = None
    phrase_search_volume: Optional[int] = None
    title_density: Optional[float] = None
    competing_products: Optional[int] = None
    cpc_estimate: Optional[float] = None  # Cost per click


class AnalysisRule(BaseModel):
    """Individual analysis rule result."""

    rule_name: str = Field(..., description="Name of the rule")
    status: DecisionStatus = Field(..., description="Rule evaluation result")
    score: float = Field(..., description="Numerical score (0-100)")
    reason: str = Field(..., description="Explanation of the decision")
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    metadata: dict = Field(default_factory=dict)


class ProductAnalysisResult(BaseModel):
    """Complete product analysis result."""

    model_config = ConfigDict(extra="allow")

    # Basic info
    asin: str
    analyzed_at: datetime = Field(default_factory=datetime.now)
    marketplace: Marketplace

    # Overall decision
    final_decision: DecisionStatus
    overall_score: float = Field(..., ge=0, le=100)

    # Individual rule results
    price_barrier_check: AnalysisRule
    brand_dominance_check: AnalysisRule
    keyword_volume_check: AnalysisRule
    review_velocity_check: Optional[AnalysisRule] = None
    title_density_check: Optional[AnalysisRule] = None
    click_concentration_check: Optional[AnalysisRule] = None
    triangulation_check: Optional[AnalysisRule] = None

    # Risk factors
    risk_factors: list[str] = Field(default_factory=list)
    opportunity_factors: list[str] = Field(default_factory=list)

    # Financial projections
    estimated_monthly_revenue: Optional[float] = None
    estimated_monthly_units: Optional[int] = None
    estimated_profit_margin: Optional[float] = None

    # Recommendations
    recommendation: str = Field(
        ..., description="Detailed recommendation text"
    )
    next_steps: list[str] = Field(default_factory=list)


class APIConfig(BaseModel):
    """API configuration for external services."""

    # Helium 10
    helium10_api_key: Optional[str] = None
    helium10_base_url: str = "https://developer.helium10.com/v1"

    # SellerSprite
    sellersprite_api_key: Optional[str] = None
    sellersprite_base_url: str = "https://api.sellersprite.com/v1"

    # Keepa
    keepa_api_key: Optional[str] = None
    keepa_base_url: str = "https://api.keepa.com"

    # General settings
    timeout: int = Field(default=30, description="API request timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
