"""
Keepa API client.

Provides access to Keepa price tracking and sales rank data.
"""

import logging
from typing import Optional, Any
from datetime import datetime, timedelta
from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class KeepaClient(BaseAPIClient):
    """
    Keepa API client.

    Key features from research report:
    - Price History: Historical price charts
    - BSR Tracking: Sales rank changes (BSR drops = sales)
    - Buy Box Analysis: Buy Box ownership tracking
    - Race to the Bottom: Price war detection
    - Seller Count: Number of active sellers
    """

    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        """
        Initialize Keepa client.

        Args:
            api_key: Keepa API key
            base_url: Base URL for Keepa API
            timeout: Request timeout in seconds
        """
        super().__init__(base_url=base_url, api_key=api_key, timeout=timeout)

    def _get_headers(self) -> dict[str, str]:
        """Override to use Keepa's authentication format."""
        headers = super()._get_headers()
        # Keepa uses 'key' parameter in URL instead of headers
        headers.pop("Authorization", None)
        return headers

    def get_product(
        self, asin: str, domain: int = 1, stats: int = 90
    ) -> dict[str, Any]:
        """
        Get comprehensive product data.

        Args:
            asin: Amazon Standard Identification Number
            domain: Amazon domain (1=US, 2=UK, 3=DE, etc.)
            stats: Days of statistical data to include

        Returns:
            dict: Complete product data
        """
        try:
            logger.info(f"Fetching Keepa data for ASIN: {asin}")
            response = self.get(
                "/product",
                params={
                    "key": self.api_key,
                    "asin": asin,
                    "domain": domain,
                    "stats": stats,
                },
            )
            return response
        except Exception as e:
            logger.error(f"Failed to fetch Keepa product data: {e}")
            return {}

    def get_price_history(
        self, asin: str, domain: int = 1, days: int = 90
    ) -> dict[str, Any]:
        """
        Get price history for a product.

        Returns data for:
        - Amazon price (orange)
        - New 3P price (pink)
        - Buy Box price (pink)
        - Used price (grey)

        Args:
            asin: Amazon Standard Identification Number
            domain: Amazon domain
            days: Number of days of history

        Returns:
            dict: Price history data
        """
        try:
            product_data = self.get_product(asin, domain, stats=days)
            if not product_data:
                return {}

            csv = product_data.get("products", [{}])[0].get("csv", [])

            return {
                "amazon_price": csv[0] if len(csv) > 0 else None,
                "new_price": csv[1] if len(csv) > 1 else None,
                "buy_box_price": csv[18] if len(csv) > 18 else None,
                "used_price": csv[2] if len(csv) > 2 else None,
            }
        except Exception as e:
            logger.error(f"Failed to parse price history: {e}")
            return {}

    def get_sales_rank_drops(
        self, asin: str, domain: int = 1, days: int = 30
    ) -> Optional[int]:
        """
        Get number of BSR (Best Sellers Rank) drops.

        BSR drops indicate sales events. More drops = more sales.

        Args:
            asin: Amazon Standard Identification Number
            domain: Amazon domain
            days: Period to analyze

        Returns:
            int: Number of BSR drops (sales) or None
        """
        try:
            product_data = self.get_product(asin, domain, stats=days)
            if not product_data:
                return None

            product = product_data.get("products", [{}])[0]
            stats = product.get("stats", {})

            # Keepa provides avg, current, and drops in stats
            drops = stats.get("salesRankDrops30", 0)
            if days != 30:
                # Approximate for different time periods
                drops = stats.get(f"salesRankDrops{days}", drops)

            return drops

        except Exception as e:
            logger.error(f"Failed to get BSR drops: {e}")
            return None

    def get_average_price(
        self, asin: str, domain: int = 1, days: int = 30
    ) -> Optional[float]:
        """
        Get average price over a period.

        Args:
            asin: Amazon Standard Identification Number
            domain: Amazon domain
            days: Period to analyze

        Returns:
            float: Average price or None
        """
        try:
            product_data = self.get_product(asin, domain, stats=days)
            if not product_data:
                return None

            product = product_data.get("products", [{}])[0]
            stats = product.get("stats", {})

            # Get average from stats
            avg_price = stats.get(f"avg{days}", {}).get("AMAZON", 0)

            # Keepa prices are in cents
            return avg_price / 100 if avg_price else None

        except Exception as e:
            logger.error(f"Failed to get average price: {e}")
            return None

    def get_buy_box_stats(
        self, asin: str, domain: int = 1, days: int = 30
    ) -> dict[str, Any]:
        """
        Get Buy Box statistics.

        Detects:
        - Buy Box suppression (gaps in pink line)
        - Buy Box owner
        - Buy Box percentage

        Args:
            asin: Amazon Standard Identification Number
            domain: Amazon domain
            days: Period to analyze

        Returns:
            dict: Buy Box statistics
        """
        try:
            product_data = self.get_product(asin, domain, stats=days)
            if not product_data:
                return {}

            product = product_data.get("products", [{}])[0]
            stats = product.get("stats", {})
            buy_box = stats.get("buyBoxStats", {})

            return {
                "current_owner": buy_box.get("currentSeller"),
                "amazon_percentage": buy_box.get("amazonPercentage", 0),
                "fba_percentage": buy_box.get("fbaPercentage", 0),
                "fbm_percentage": buy_box.get("fbmPercentage", 0),
                "has_suppression": buy_box.get("hasSuppression", False),
            }

        except Exception as e:
            logger.error(f"Failed to get Buy Box stats: {e}")
            return {}

    def detect_race_to_bottom(
        self, asin: str, domain: int = 1, days: int = 90
    ) -> dict[str, Any]:
        """
        Detect "race to the bottom" price wars.

        Indicators:
        - Continuous price decline
        - High price volatility
        - Many seller changes

        Args:
            asin: Amazon Standard Identification Number
            domain: Amazon domain
            days: Period to analyze

        Returns:
            dict: Price war detection results
        """
        try:
            product_data = self.get_product(asin, domain, stats=days)
            if not product_data:
                return {"detected": False}

            product = product_data.get("products", [{}])[0]
            stats = product.get("stats", {})

            current_price = product.get("stats", {}).get("current", [0, 0])[0] / 100
            avg_90d = stats.get("avg90", {}).get("AMAZON", 0) / 100

            # Calculate price decline
            price_decline = 0
            if avg_90d > 0:
                price_decline = ((avg_90d - current_price) / avg_90d) * 100

            # Check for warning signs
            detected = False
            reasons = []

            if price_decline > 20:
                detected = True
                reasons.append(f"Price declined {price_decline:.1f}% in {days} days")

            seller_count = product.get("offersCount", 0)
            if seller_count > 20:
                detected = True
                reasons.append(f"High seller count: {seller_count}")

            return {
                "detected": detected,
                "price_decline_percent": price_decline,
                "current_price": current_price,
                "avg_price_90d": avg_90d,
                "seller_count": seller_count,
                "reasons": reasons,
            }

        except Exception as e:
            logger.error(f"Failed to detect race to bottom: {e}")
            return {"detected": False, "error": str(e)}

    def get_seller_count(
        self, asin: str, domain: int = 1
    ) -> Optional[int]:
        """
        Get current number of sellers.

        Args:
            asin: Amazon Standard Identification Number
            domain: Amazon domain

        Returns:
            int: Number of sellers or None
        """
        try:
            product_data = self.get_product(asin, domain)
            if not product_data:
                return None

            product = product_data.get("products", [{}])[0]
            return product.get("offersCount", 0)

        except Exception as e:
            logger.error(f"Failed to get seller count: {e}")
            return None
