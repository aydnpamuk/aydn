"""
Helium 10 API client.

Provides access to Helium 10 tools like Black Box, Xray, Cerebro, and Magnet.
"""

import logging
from typing import Optional, Any
from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class Helium10Client(BaseAPIClient):
    """
    Helium 10 API client.

    Key features from research report:
    - Black Box: Product discovery with filters
    - Xray: Real-time market analysis
    - Cerebro: Keyword research and Title Density
    - Magnet: Keyword discovery
    - CPR: Cerebro Product Rank (8-day giveaway estimate)
    """

    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        """
        Initialize Helium 10 client.

        Args:
            api_key: Helium 10 API key
            base_url: Base URL for Helium 10 API
            timeout: Request timeout in seconds
        """
        super().__init__(base_url=base_url, api_key=api_key, timeout=timeout)

    def _get_headers(self) -> dict[str, str]:
        """Override to use Helium 10's authentication format."""
        headers = super()._get_headers()
        if self.api_key:
            # Helium 10 uses X-API-Key header
            headers.pop("Authorization", None)
            headers["X-API-Key"] = self.api_key
        return headers

    def get_product_data(
        self, asin: str, marketplace: str = "US"
    ) -> dict[str, Any]:
        """
        Get comprehensive product data using Xray.

        Args:
            asin: Amazon Standard Identification Number
            marketplace: Amazon marketplace (US, UK, DE, etc.)

        Returns:
            dict: Product data including sales, revenue, reviews
        """
        try:
            logger.info(f"Fetching Helium 10 data for ASIN: {asin}")
            response = self.get(
                "/products/asin",
                params={"asin": asin, "marketplace": marketplace},
            )
            return response
        except Exception as e:
            logger.error(f"Failed to fetch Helium 10 product data: {e}")
            return {}

    def get_keyword_data(
        self, keyword: str, marketplace: str = "US"
    ) -> dict[str, Any]:
        """
        Get keyword data using Magnet/Cerebro.

        Args:
            keyword: Target keyword
            marketplace: Amazon marketplace

        Returns:
            dict: Keyword data including search volume, competition
        """
        try:
            logger.info(f"Fetching Helium 10 keyword data: {keyword}")
            response = self.get(
                "/keywords/search-volume",
                params={"keyword": keyword, "marketplace": marketplace},
            )
            return response
        except Exception as e:
            logger.error(f"Failed to fetch Helium 10 keyword data: {e}")
            return {}

    def get_title_density(
        self, keyword: str, marketplace: str = "US"
    ) -> Optional[float]:
        """
        Get Title Density metric for a keyword.

        Title Density < 5 is ideal (low competition opportunity).

        Args:
            keyword: Target keyword
            marketplace: Amazon marketplace

        Returns:
            float: Title density score or None
        """
        try:
            logger.info(f"Fetching Title Density for: {keyword}")
            response = self.get(
                "/keywords/title-density",
                params={"keyword": keyword, "marketplace": marketplace},
            )
            return response.get("title_density")
        except Exception as e:
            logger.error(f"Failed to fetch title density: {e}")
            return None

    def get_cpr(
        self, keyword: str, marketplace: str = "US"
    ) -> Optional[int]:
        """
        Get CPR (Cerebro Product Rank) - 8-day giveaway estimate.

        Estimates number of sales needed over 8 days to rank on page 1.

        Args:
            keyword: Target keyword
            marketplace: Amazon marketplace

        Returns:
            int: Number of units for 8-day giveaway or None
        """
        try:
            logger.info(f"Fetching CPR for: {keyword}")
            response = self.get(
                "/keywords/cpr",
                params={"keyword": keyword, "marketplace": marketplace},
            )
            return response.get("cpr")
        except Exception as e:
            logger.error(f"Failed to fetch CPR: {e}")
            return None

    def black_box_search(
        self,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_revenue: Optional[float] = None,
        max_revenue: Optional[float] = None,
        min_reviews: Optional[int] = None,
        max_reviews: Optional[int] = None,
        marketplace: str = "US",
        **kwargs,
    ) -> list[dict[str, Any]]:
        """
        Search for products using Black Box with filters.

        Args:
            min_price: Minimum product price
            max_price: Maximum product price
            min_revenue: Minimum monthly revenue
            max_revenue: Maximum monthly revenue
            min_reviews: Minimum review count
            max_reviews: Maximum review count
            marketplace: Amazon marketplace
            **kwargs: Additional filter parameters

        Returns:
            list: List of matching products
        """
        try:
            params = {"marketplace": marketplace}

            if min_price:
                params["min_price"] = min_price
            if max_price:
                params["max_price"] = max_price
            if min_revenue:
                params["min_revenue"] = min_revenue
            if max_revenue:
                params["max_revenue"] = max_revenue
            if min_reviews:
                params["min_reviews"] = min_reviews
            if max_reviews:
                params["max_reviews"] = max_reviews

            params.update(kwargs)

            logger.info(f"Running Black Box search with filters: {params}")
            response = self.get("/products/search", params=params)
            return response.get("products", [])

        except Exception as e:
            logger.error(f"Black Box search failed: {e}")
            return []

    def get_review_velocity(
        self, asin: str, marketplace: str = "US"
    ) -> Optional[float]:
        """
        Get review velocity (reviews per month).

        Args:
            asin: Amazon Standard Identification Number
            marketplace: Amazon marketplace

        Returns:
            float: Average reviews per month or None
        """
        try:
            logger.info(f"Fetching review velocity for: {asin}")
            response = self.get(
                "/products/review-velocity",
                params={"asin": asin, "marketplace": marketplace},
            )
            return response.get("reviews_per_month")
        except Exception as e:
            logger.error(f"Failed to fetch review velocity: {e}")
            return None
