"""
Configuration management for the application.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from .models import APIConfig


# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings and configuration."""

    def __init__(self):
        """Initialize settings from environment variables."""
        self.api_config = APIConfig(
            helium10_api_key=os.getenv("HELIUM10_API_KEY"),
            helium10_base_url=os.getenv(
                "HELIUM10_BASE_URL", "https://developer.helium10.com/v1"
            ),
            sellersprite_api_key=os.getenv("SELLERSPRITE_API_KEY"),
            sellersprite_base_url=os.getenv(
                "SELLERSPRITE_BASE_URL", "https://api.sellersprite.com/v1"
            ),
            keepa_api_key=os.getenv("KEEPA_API_KEY"),
            keepa_base_url=os.getenv("KEEPA_BASE_URL", "https://api.keepa.com"),
            timeout=int(os.getenv("API_TIMEOUT", "30")),
            retry_attempts=int(os.getenv("API_RETRY_ATTEMPTS", "3")),
            cache_ttl=int(os.getenv("CACHE_TTL", "3600")),
        )

        # Analysis thresholds (based on the research report)
        self.price_barrier_usd = float(os.getenv("PRICE_BARRIER_USD", "39.0"))
        self.price_barrier_eur = float(os.getenv("PRICE_BARRIER_EUR", "39.0"))
        self.brand_dominance_threshold = float(
            os.getenv("BRAND_DOMINANCE_THRESHOLD", "0.50")
        )  # 50%
        self.min_keyword_volume = int(os.getenv("MIN_KEYWORD_VOLUME", "3000"))
        self.click_concentration_threshold = float(
            os.getenv("CLICK_CONCENTRATION_THRESHOLD", "0.60")
        )  # 60%
        self.title_density_threshold = float(
            os.getenv("TITLE_DENSITY_THRESHOLD", "5.0")
        )

        # Scoring weights
        self.weight_price_barrier = float(os.getenv("WEIGHT_PRICE_BARRIER", "0.25"))
        self.weight_brand_dominance = float(
            os.getenv("WEIGHT_BRAND_DOMINANCE", "0.25")
        )
        self.weight_keyword_volume = float(os.getenv("WEIGHT_KEYWORD_VOLUME", "0.20"))
        self.weight_review_velocity = float(os.getenv("WEIGHT_REVIEW_VELOCITY", "0.10"))
        self.weight_title_density = float(os.getenv("WEIGHT_TITLE_DENSITY", "0.10"))
        self.weight_triangulation = float(os.getenv("WEIGHT_TRIANGULATION", "0.10"))

        # Decision thresholds
        self.green_threshold = float(
            os.getenv("GREEN_THRESHOLD", "70.0")
        )  # >= 70 = GREEN
        self.yellow_threshold = float(
            os.getenv("YELLOW_THRESHOLD", "40.0")
        )  # 40-70 = YELLOW
        # < 40 = RED

        # Output settings
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./reports"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "amazon_analysis.log")

    def validate_api_keys(self) -> dict[str, bool]:
        """
        Validate that required API keys are present.

        Returns:
            dict: Validation status for each API service
        """
        return {
            "helium10": bool(self.api_config.helium10_api_key),
            "sellersprite": bool(self.api_config.sellersprite_api_key),
            "keepa": bool(self.api_config.keepa_api_key),
        }


# Global settings instance
settings = Settings()
