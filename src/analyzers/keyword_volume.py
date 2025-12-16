"""
Keyword Volume Analyzer

Implements the 3,000 minimum exact search volume rule.
Keywords below this threshold typically lack sufficient demand.
"""

import logging
from typing import Optional
from ..core.models import AnalysisRule, DecisionStatus, KeywordData
from ..core.config import settings
from ..api import Helium10Client, SellerSpriteClient

logger = logging.getLogger(__name__)


class KeywordVolumeAnalyzer:
    """
    Analyzes keyword search volume and demand.

    Research basis:
    - Low volume = low demand = limited sales potential
    - 3,000+ monthly searches recommended for sustainable business
    - However: High volume ≠ always good (consider competition)
    - Long-tail strategy can work with 1,000-3,000 range
    """

    def __init__(
        self,
        min_volume: Optional[int] = None,
        h10_client: Optional[Helium10Client] = None,
        ss_client: Optional[SellerSpriteClient] = None,
    ):
        """
        Initialize keyword volume analyzer.

        Args:
            min_volume: Minimum acceptable search volume (default from config)
            h10_client: Helium 10 API client
            ss_client: SellerSprite API client
        """
        self.min_volume = min_volume or settings.min_keyword_volume
        self.h10_client = h10_client
        self.ss_client = ss_client

    def analyze(self, keyword_data: KeywordData) -> AnalysisRule:
        """
        Analyze keyword search volume.

        Args:
            keyword_data: Keyword data with search volumes

        Returns:
            AnalysisRule: Analysis result
        """
        volume = keyword_data.exact_search_volume
        keyword = keyword_data.keyword

        logger.info(
            f"Analyzing keyword volume for '{keyword}': "
            f"{volume} searches/month (threshold: {self.min_volume})"
        )

        # Calculate volume ratio
        volume_ratio = volume / self.min_volume if self.min_volume > 0 else 0

        # Scoring and decision
        if volume < self.min_volume * 0.3:
            # Extremely low volume
            score = 0.0
            status = DecisionStatus.RED
            reason = (
                f"Search volume ({volume:,}/month) is critically low. "
                f"Less than 30% of minimum threshold ({self.min_volume:,}). "
                f"Insufficient demand to sustain profitable business. "
                f"Consider broader keywords or different niche."
            )

        elif volume < self.min_volume:
            # Below threshold but might work with long-tail strategy
            score = (volume / self.min_volume) * 50  # 0-50 range
            status = DecisionStatus.YELLOW
            reason = (
                f"Search volume ({volume:,}/month) is below recommended threshold "
                f"({self.min_volume:,}). Limited demand detected. "
                f"Consider as part of long-tail keyword strategy if competition is low. "
                f"May work for micro-niche with high conversion rate."
            )

        elif volume < self.min_volume * 2:
            # Good range - above threshold
            score = 50 + ((volume - self.min_volume) / self.min_volume) * 30  # 50-80
            status = DecisionStatus.GREEN
            reason = (
                f"Search volume ({volume:,}/month) meets threshold requirements. "
                f"Adequate demand for sustainable sales. "
                f"Good balance of demand and competition potential."
            )

        elif volume < self.min_volume * 5:
            # High volume - excellent demand
            score = 80 + min(
                15, ((volume - self.min_volume * 2) / (self.min_volume * 3)) * 15
            )
            status = DecisionStatus.GREEN
            reason = (
                f"High search volume ({volume:,}/month). "
                f"Strong market demand detected. "
                f"Significant sales potential. Verify competition levels."
            )

        else:
            # Very high volume - check for over-competition
            score = 90.0
            status = DecisionStatus.GREEN
            reason = (
                f"Very high search volume ({volume:,}/month). "
                f"Massive market demand. "
                f"⚠️ WARNING: Verify competition and click concentration. "
                f"High-volume keywords often have established players."
            )

        return AnalysisRule(
            rule_name="keyword_volume",
            status=status,
            score=score,
            reason=reason,
            threshold_value=float(self.min_volume),
            actual_value=float(volume),
            metadata={
                "keyword": keyword,
                "volume_ratio": volume_ratio,
                "broad_volume": keyword_data.broad_search_volume,
                "phrase_volume": keyword_data.phrase_search_volume,
            },
        )

    def analyze_keyword_opportunity(
        self, keyword: str, marketplace: str = "US"
    ) -> dict:
        """
        Comprehensive keyword opportunity analysis.

        Combines volume data from multiple sources for triangulation.

        Args:
            keyword: Target keyword
            marketplace: Amazon marketplace

        Returns:
            dict: Comprehensive keyword analysis
        """
        # Get volume from multiple sources
        h10_volume = None
        ss_volume = None

        if self.h10_client:
            h10_data = self.h10_client.get_keyword_data(keyword, marketplace)
            h10_volume = h10_data.get("search_volume")

        if self.ss_client:
            ss_volume = self.ss_client.get_search_volume(keyword, marketplace)

        # Triangulate (average if both available)
        volumes = [v for v in [h10_volume, ss_volume] if v is not None]
        avg_volume = sum(volumes) / len(volumes) if volumes else 0

        # Get trends if available
        trends = {}
        if self.ss_client:
            trend_data = self.ss_client.get_keyword_trends(keyword, marketplace)
            trends = {
                "is_growing": trend_data.get("is_growing", False),
                "growth_rate": trend_data.get("growth_rate"),
                "seasonality_score": trend_data.get("seasonality_score"),
            }

        return {
            "keyword": keyword,
            "h10_volume": h10_volume,
            "ss_volume": ss_volume,
            "triangulated_volume": int(avg_volume),
            "data_sources": len(volumes),
            "volume_variance": (
                max(volumes) - min(volumes) if len(volumes) > 1 else 0
            ),
            "trends": trends,
            "meets_threshold": avg_volume >= self.min_volume,
        }

    def suggest_related_keywords(
        self, keyword: str, marketplace: str = "US", min_volume: Optional[int] = None
    ) -> list[dict]:
        """
        Suggest related keywords that meet volume requirements.

        Args:
            keyword: Seed keyword
            marketplace: Amazon marketplace
            min_volume: Minimum volume override

        Returns:
            list: Related keywords with volumes
        """
        min_vol = min_volume or self.min_volume

        suggestions = []

        if self.h10_client:
            # Use Helium 10's Magnet for keyword discovery
            h10_data = self.h10_client.get_keyword_data(keyword, marketplace)
            related = h10_data.get("related_keywords", [])

            for kw in related:
                if kw.get("search_volume", 0) >= min_vol:
                    suggestions.append(
                        {
                            "keyword": kw.get("keyword"),
                            "volume": kw.get("search_volume"),
                            "competition": kw.get("competition"),
                            "source": "helium10",
                        }
                    )

        return sorted(suggestions, key=lambda x: x["volume"], reverse=True)
