"""
Sentiment analysis utilities
Uses VADER for sentiment scoring
"""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Initialize VADER analyzer (singleton)
_analyzer = None


def get_analyzer():
    """Get or create VADER sentiment analyzer"""
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentIntensityAnalyzer()
    return _analyzer


def analyze_sentiment(text: Optional[str]) -> Dict[str, any]:
    """
    Analyze sentiment of review text

    Args:
        text: Review text to analyze

    Returns:
        Dictionary with sentiment_score (-1 to 1) and sentiment_label (negative/neutral/positive)
    """
    if not text or not text.strip():
        return {"sentiment_score": 0.0, "sentiment_label": "neutral"}

    try:
        analyzer = get_analyzer()
        scores = analyzer.polarity_scores(text)

        # Compound score ranges from -1 (most negative) to 1 (most positive)
        compound = scores["compound"]

        # Classify sentiment
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {"sentiment_score": round(compound, 4), "sentiment_label": label}

    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return {"sentiment_score": 0.0, "sentiment_label": "neutral"}


def batch_analyze_sentiment(texts: list) -> list:
    """
    Analyze sentiment for multiple texts

    Args:
        texts: List of text strings

    Returns:
        List of sentiment dictionaries
    """
    return [analyze_sentiment(text) for text in texts]
