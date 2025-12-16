"""
SellerSprite API client.

Provides access to SellerSprite market analysis tools.
"""

import logging
from typing import Optional, Any
from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class SellerSpriteClient(BaseAPIClient):
    """
    SellerSprite API client.

    Key features from research report:
    - Click Concentration: Top 3 products' click share (monopoly test)
    - Traffic Analysis: Organic vs sponsored traffic ratio
    - ABA Data: Amazon Brand Analytics integration
    - Market Analysis: 16-dimensional market evaluation
    """

    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        """
        Initialize SellerSprite client.

        Args:
            api_key: SellerSprite API key
            base_url: Base URL for SellerSprite API
            timeout: Request timeout in seconds
        """
        super().__init__(base_url=base_url, api_key=api_key, timeout=timeout)

    def get_market_analysis(
        self, keyword: str, marketplace: str = "US"
    ) -> dict[str, Any]:
        """
        Get comprehensive market analysis for a keyword.

        Includes 16-dimensional analysis metrics.

        Args:
            keyword: Target keyword
            marketplace: Amazon marketplace

        Returns:
            dict: Market analysis data
        """
        try:
            logger.info(f"Fetching SellerSprite market analysis: {keyword}")
            response = self.get(
                "/market/analysis",
                params={"keyword": keyword, "marketplace": marketplace},
            )
            return response
        except Exception as e:
            logger.error(f"Failed to fetch market analysis: {e}")
            return {}

    def get_click_concentration(
        self, keyword: str, marketplace: str = "US"
    ) -> Optional[float]:
        """
        Get Click Concentration metric (Top 3 click share).

        Interpretation:
        - 50-60%: Medium monopoly
        - 60-70%: High monopoly
        - 70%+: Very high monopoly (AVOID)

        Args:
            keyword: Target keyword
            marketplace: Amazon marketplace

        Returns:
            float: Click concentration percentage (0-1) or None
        """
        try:
            logger.info(f"Fetching click concentration for: {keyword}")
            response = self.get(
                "/market/click-concentration",
                params={"keyword": keyword, "marketplace": marketplace},
            )
            concentration = response.get("click_concentration")
            if concentration is not None:
                # Convert to decimal if returned as percentage
                if concentration > 1:
                    concentration = concentration / 100
            return concentration
        except Exception as e:
            logger.error(f"Failed to fetch click concentration: {e}")
            return None

    def get_traffic_analysis(
        self, asin: str, marketplace: str = "US"
    ) -> dict[str, Any]:
        """
        Get traffic analysis (organic vs sponsored).

        Ideal: Organic 60%+ (easier to rank with SEO)
        Warning: Sponsored heavy (high PPC cost risk)

        Args:
            asin: Amazon Standard Identification Number
            marketplace: Amazon marketplace

        Returns:
            dict: Traffic breakdown data
        """
        try:
            logger.info(f"Fetching traffic analysis for: {asin}")
            response = self.get(
                "/products/traffic-analysis",
                params={"asin": asin, "marketplace": marketplace},
            )
            return {
                "organic_ratio": response.get("organic_traffic_ratio"),
                "sponsored_ratio": response.get("sponsored_traffic_ratio"),
                "total_traffic": response.get("total_traffic"),
            }
        except Exception as e:
            logger.error(f"Failed to fetch traffic analysis: {e}")
            return {}

    def get_search_volume(
        self, keyword: str, marketplace: str = "US"
    ) -> Optional[int]:
        """
        Get monthly search volume for a keyword.

        Uses ABA (Amazon Brand Analytics) data when available.

        Args:
            keyword: Target keyword
            marketplace: Amazon marketplace

        Returns:
            int: Monthly search volume or None
        """
        try:
            logger.info(f"Fetching search volume for: {keyword}")
            response = self.get(
                "/keywords/search-volume",
                params={"keyword": keyword, "marketplace": marketplace},
            )
            return response.get("search_volume")
        except Exception as e:
            logger.error(f"Failed to fetch search volume: {e}")
            return None

    def get_keyword_trends(
        self, keyword: str, marketplace: str = "US", days: int = 90
    ) -> dict[str, Any]:
        """
        Get keyword trend data over time.

        Args:
            keyword: Target keyword
            marketplace: Amazon marketplace
            days: Number of days to analyze (default 90)

        Returns:
            dict: Trend data with historical search volumes
        """
        try:
            logger.info(f"Fetching keyword trends for: {keyword}")
            response = self.get(
                "/keywords/trends",
                params={
                    "keyword": keyword,
                    "marketplace": marketplace,
                    "days": days,
                },
            )
            return response
        except Exception as e:
            logger.error(f"Failed to fetch keyword trends: {e}")
            return {}

    def get_top_competitors(
        self, keyword: str, marketplace: str = "US", limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Get top competing products for a keyword.

        Args:
            keyword: Target keyword
            marketplace: Amazon marketplace
            limit: Number of competitors to return

        Returns:
            list: Top competing products
        """
        try:
            logger.info(f"Fetching top competitors for: {keyword}")
            response = self.get(
                "/keywords/competitors",
                params={
                    "keyword": keyword,
                    "marketplace": marketplace,
                    "limit": limit,
                },
            )
            return response.get("competitors", [])
        except Exception as e:
            logger.error(f"Failed to fetch competitors: {e}")
            return []

    def get_brand_analytics_data(
        self, keyword: str, marketplace: str = "US"
    ) -> dict[str, Any]:
        """
        Get Amazon Brand Analytics (ABA) data.

        Provides official Amazon data on:
        - Top clicked ASINs
        - Click share
        - Conversion share

        Args:
            keyword: Target keyword
            marketplace: Amazon marketplace

        Returns:
            dict: ABA data
        """
        try:
            logger.info(f"Fetching ABA data for: {keyword}")
            response = self.get(
                "/keywords/brand-analytics",
                params={"keyword": keyword, "marketplace": marketplace},
            )
            return response
        except Exception as e:
            logger.error(f"Failed to fetch ABA data: {e}")
            return {}
