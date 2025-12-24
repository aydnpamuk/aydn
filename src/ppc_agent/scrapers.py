"""Amazon PPC Vaka Avcısı - Web Scraping Modülleri."""

import os
import re
from datetime import datetime, timedelta
from typing import Optional

import praw
import requests
from bs4 import BeautifulSoup

from .models import CaseCandidate, Category, CaseType, Market, Platform


class RedditScraper:
    """Reddit scraper - PPC vakalarını bul."""

    def __init__(self):
        """Reddit API başlatıcı."""
        self.reddit = None
        self._init_reddit()

    def _init_reddit(self) -> None:
        """Reddit API'yi başlat (çevre değişkenlerinden)."""
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "AmazonPPCCaseHunter/1.0")

        if client_id and client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent,
                )
            except Exception as e:
                print(f"Reddit API başlatılamadı: {e}")
                print("REDDIT_CLIENT_ID ve REDDIT_CLIENT_SECRET ayarlayın.")

    def search_ppc_cases(
        self, subreddits: list[str], days_back: int = 7, limit: int = 50
    ) -> list[dict]:
        """
        Reddit'te PPC vakalarını ara.

        Args:
            subreddits: Aranacak subreddit listesi
            days_back: Kaç gün geriye git
            limit: Maksimum sonuç sayısı

        Returns:
            Bulunan gönderilerin listesi
        """
        if not self.reddit:
            print("Reddit API kullanılamıyor. Çevre değişkenlerini kontrol edin.")
            return []

        results = []
        search_queries = [
            "amazon ppc case study",
            "amazon ads acos",
            "amazon ppc before after",
            "sponsored products results",
            "amazon advertising case",
        ]

        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)

                for query in search_queries:
                    for submission in subreddit.search(
                        query, time_filter="week", limit=limit
                    ):
                        # Tarih kontrolü
                        post_time = datetime.fromtimestamp(submission.created_utc)
                        if datetime.now() - post_time > timedelta(days=days_back):
                            continue

                        results.append(
                            {
                                "title": submission.title,
                                "url": submission.url,
                                "selftext": submission.selftext,
                                "score": submission.score,
                                "created_utc": post_time,
                                "subreddit": subreddit_name,
                                "author": str(submission.author),
                                "num_comments": submission.num_comments,
                            }
                        )

            except Exception as e:
                print(f"Subreddit {subreddit_name} taranırken hata: {e}")
                continue

        return results


class BlogScraper:
    """Blog ve web sitesi scraper."""

    def __init__(self):
        """Blog scraper başlatıcı."""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def fetch_blog_posts(self, blog_urls: list[str]) -> list[dict]:
        """
        Blog URL'lerinden içerik çek.

        Args:
            blog_urls: Taranacak blog URL listesi

        Returns:
            Bulunan içerikler
        """
        results = []

        for url in blog_urls:
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")

                # Blog gönderilerini bul (genel selektörler)
                articles = soup.find_all(["article", "div"], class_=re.compile("post|article|blog"))

                for article in articles[:10]:  # İlk 10 makale
                    title_elem = article.find(["h1", "h2", "h3"])
                    link_elem = article.find("a")

                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        link = link_elem.get("href", "")

                        # Göreceli URL'leri düzelt
                        if link.startswith("/"):
                            from urllib.parse import urljoin
                            link = urljoin(url, link)

                        # PPC ile ilgili mi kontrol et
                        if self._is_ppc_related(title):
                            results.append(
                                {
                                    "title": title,
                                    "url": link,
                                    "source": url,
                                    "scraped_at": datetime.now(),
                                }
                            )

            except Exception as e:
                print(f"Blog {url} taranırken hata: {e}")
                continue

        return results

    def _is_ppc_related(self, text: str) -> bool:
        """
        Metnin PPC ile ilgili olup olmadığını kontrol et.

        Args:
            text: Kontrol edilecek metin

        Returns:
            PPC ile ilgili mi?
        """
        ppc_keywords = [
            "ppc",
            "amazon ads",
            "sponsored products",
            "acos",
            "tacos",
            "case study",
            "advertising",
            "sponsored brands",
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in ppc_keywords)

    def extract_metrics_from_text(self, text: str) -> list[str]:
        """
        Metinden PPC metriklerini çıkar.

        Args:
            text: Analiz edilecek metin

        Returns:
            Bulunan metrikler
        """
        metrics = []
        metric_patterns = {
            "ACoS": r"acos[:\s]+(\d+\.?\d*%?)",
            "TACoS": r"tacos[:\s]+(\d+\.?\d*%?)",
            "CPC": r"cpc[:\s]+\$?(\d+\.?\d*)",
            "CTR": r"ctr[:\s]+(\d+\.?\d*%?)",
            "CVR": r"cvr[:\s]+(\d+\.?\d*%?)",
            "ROAS": r"roas[:\s]+(\d+\.?\d*)",
            "Spend": r"spend[:\s]+\$?(\d+\.?\d*)",
            "Sales": r"sales[:\s]+\$?(\d+\.?\d*)",
        }

        text_lower = text.lower()

        for metric_name, pattern in metric_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                metrics.append(metric_name)

        return metrics

    def has_before_after(self, text: str) -> bool:
        """
        Metinde önce/sonra bilgisi var mı kontrol et.

        Args:
            text: Kontrol edilecek metin

        Returns:
            Önce/sonra var mı?
        """
        before_after_patterns = [
            r"before.*after",
            r"önce.*sonra",
            r"from.*to",
            r"reduced.*from.*to",
            r"increased.*from.*to",
        ]

        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in before_after_patterns)


class CaseAnalyzer:
    """Vaka analiz ve değerlendirme araçları."""

    @staticmethod
    def create_candidate_from_reddit(post: dict) -> Optional[CaseCandidate]:
        """
        Reddit gönderisinden aday vaka oluştur.

        Args:
            post: Reddit gönderi verisi

        Returns:
            Aday vaka veya None
        """
        try:
            scraper = BlogScraper()
            text = f"{post['title']} {post['selftext']}"

            # Metrikleri çıkar
            metrics = scraper.extract_metrics_from_text(text)

            # Önce/sonra var mı?
            has_before_after = scraper.has_before_after(text)

            # Ön güven puanı hesapla
            confidence = CaseAnalyzer._calculate_preliminary_confidence(
                metrics, has_before_after, post.get("score", 0)
            )

            # Özet oluştur
            summary = post["title"][:150]

            return CaseCandidate(
                title=post["title"],
                url=post["url"],
                date=post["created_utc"],
                platform=Platform.REDDIT,
                market=Market.UNKNOWN,
                category=Category.OTHER,
                case_type=CaseType.OTHER,
                visible_metrics=metrics,
                has_before_after=has_before_after,
                summary=summary,
                preliminary_confidence=confidence,
                confidence_reason=f"{len(metrics)} metrik, {'önce/sonra var' if has_before_after else 'önce/sonra yok'}, score: {post.get('score', 0)}",
            )

        except Exception as e:
            print(f"Reddit gönderisinden aday oluşturulurken hata: {e}")
            return None

    @staticmethod
    def create_candidate_from_blog(post: dict) -> Optional[CaseCandidate]:
        """
        Blog gönderisinden aday vaka oluştur.

        Args:
            post: Blog gönderi verisi

        Returns:
            Aday vaka veya None
        """
        try:
            return CaseCandidate(
                title=post["title"],
                url=post["url"],
                date=post.get("scraped_at", datetime.now()),
                platform=Platform.BLOG,
                market=Market.UNKNOWN,
                category=Category.OTHER,
                case_type=CaseType.OTHER,
                visible_metrics=[],
                has_before_after=False,
                summary=post["title"][:150],
                preliminary_confidence=50,
                confidence_reason="Blog gönderisi, detaylı analiz gerekli",
            )

        except Exception as e:
            print(f"Blog gönderisinden aday oluşturulurken hata: {e}")
            return None

    @staticmethod
    def _calculate_preliminary_confidence(
        metrics: list[str], has_before_after: bool, score: int
    ) -> int:
        """
        Ön güven puanı hesapla.

        Args:
            metrics: Bulunan metrikler
            has_before_after: Önce/sonra var mı?
            score: Reddit puanı

        Returns:
            Güven puanı (0-100)
        """
        base_score = 30

        # Metrik sayısına göre puan
        metric_score = min(len(metrics) * 10, 40)

        # Önce/sonra varsa bonus
        before_after_bonus = 20 if has_before_after else 0

        # Reddit puanına göre bonus
        score_bonus = min(score // 10, 10)

        total = base_score + metric_score + before_after_bonus + score_bonus

        return min(total, 100)
