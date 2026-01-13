"""
Amazon review HTML parser
Extracts review data from Amazon review pages
"""
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class AmazonReviewParser:
    """Parser for Amazon customer review pages"""

    def __init__(self, marketplace: str = "us"):
        self.marketplace = marketplace
        self.domain_map = {
            "us": "amazon.com",
            "de": "amazon.de",
            "uk": "amazon.co.uk",
            "fr": "amazon.fr",
            "it": "amazon.it",
            "es": "amazon.es",
            "ca": "amazon.ca",
            "jp": "amazon.co.jp",
        }

    def parse_html(self, html_content: str, asin: str) -> List[Dict]:
        """
        Parse Amazon review page HTML and extract review data

        Args:
            html_content: HTML content of the review page
            asin: Product ASIN

        Returns:
            List of review dictionaries
        """
        soup = BeautifulSoup(html_content, "lxml")
        reviews = []

        # Find all review containers
        review_divs = soup.find_all("div", {"data-hook": "review"})

        if not review_divs:
            logger.warning(f"No reviews found in HTML for ASIN: {asin}")
            return reviews

        for review_div in review_divs:
            try:
                review_data = self._parse_review_div(review_div, asin)
                if review_data:
                    reviews.append(review_data)
            except Exception as e:
                logger.error(f"Error parsing review: {e}")
                continue

        logger.info(f"Parsed {len(reviews)} reviews for ASIN: {asin}")
        return reviews

    def _parse_review_div(self, review_div, asin: str) -> Optional[Dict]:
        """Parse individual review div element"""

        # Review ID
        review_id = review_div.get("id", "").replace("customer_review-", "")
        if not review_id:
            return None

        # Rating (extract from star rating class)
        rating_elem = review_div.find("i", {"data-hook": "review-star-rating"})
        rating = None
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            match = re.search(r"(\d+\.?\d*)", rating_text)
            if match:
                rating = int(float(match.group(1)))

        # Title
        title_elem = review_div.find("a", {"data-hook": "review-title"})
        title = None
        if title_elem:
            title = title_elem.get_text(strip=True)
            # Remove "5.0 out of 5 stars" prefix if present
            title = re.sub(r"^\d+\.?\d*\s+out of \d+ stars\s*", "", title)

        # Review text
        text_elem = review_div.find("span", {"data-hook": "review-body"})
        text = text_elem.get_text(strip=True) if text_elem else None

        # Author name
        author_elem = review_div.find("span", {"class": "a-profile-name"})
        author_name = author_elem.get_text(strip=True) if author_elem else None

        # Review date
        date_elem = review_div.find("span", {"data-hook": "review-date"})
        review_date = None
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            review_date = self._parse_date(date_text)

        # Verified purchase
        verified_elem = review_div.find("span", {"data-hook": "avp-badge"})
        verified_purchase = verified_elem is not None

        # Helpful votes
        helpful_elem = review_div.find("span", {"data-hook": "helpful-vote-statement"})
        helpful_votes = 0
        if helpful_elem:
            helpful_text = helpful_elem.get_text(strip=True)
            match = re.search(r"(\d+)", helpful_text)
            if match:
                helpful_votes = int(match.group(1))

        return {
            "review_id": review_id,
            "asin": asin,
            "marketplace": self.marketplace,
            "rating": rating,
            "title": title,
            "text": text,
            "author_name": author_name,
            "review_date": review_date,
            "verified_purchase": verified_purchase,
            "helpful_votes": helpful_votes,
        }

    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse review date from text"""
        try:
            # Remove "Reviewed in [Country] on " prefix
            date_text = re.sub(r"^.*?\bon\s+", "", date_text)

            # Common date formats
            date_formats = [
                "%B %d, %Y",  # January 15, 2024
                "%d %B %Y",  # 15 January 2024 (EU format)
                "%Y年%m月%d日",  # Japanese format
            ]

            for fmt in date_formats:
                try:
                    return datetime.strptime(date_text.strip(), fmt)
                except ValueError:
                    continue

            logger.warning(f"Could not parse date: {date_text}")
            return None

        except Exception as e:
            logger.error(f"Error parsing date '{date_text}': {e}")
            return None

    def extract_asin_from_url(self, url: str) -> Optional[str]:
        """Extract ASIN from Amazon product URL"""
        # Pattern: /dp/ASIN or /product/ASIN
        match = re.search(r"/(dp|product)/([A-Z0-9]{10})", url)
        if match:
            return match.group(2)

        # Check if it's already an ASIN
        if len(url) == 10 and url.isalnum():
            return url.upper()

        return None

    def extract_product_info(self, html_content: str, asin: str) -> Dict:
        """Extract product metadata from review page"""
        soup = BeautifulSoup(html_content, "lxml")

        # Product title
        title_elem = soup.find("h1", {"data-hook": "product-link"})
        title = title_elem.get_text(strip=True) if title_elem else None

        # Average rating
        avg_rating_elem = soup.find("span", {"data-hook": "rating-out-of-text"})
        avg_rating = None
        if avg_rating_elem:
            match = re.search(r"(\d+\.?\d*)", avg_rating_elem.get_text())
            if match:
                avg_rating = float(match.group(1))

        # Total reviews
        total_reviews_elem = soup.find("div", {"data-hook": "total-review-count"})
        total_reviews = None
        if total_reviews_elem:
            match = re.search(r"([\d,]+)", total_reviews_elem.get_text())
            if match:
                total_reviews = int(match.group(1).replace(",", ""))

        return {
            "asin": asin,
            "title": title,
            "average_rating": avg_rating,
            "total_reviews": total_reviews,
        }
