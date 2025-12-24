"""Amazon PPC Vaka Avcısı - Cuma Derin Analiz Ajanı."""

import re
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .models import (
    Actions,
    CampaignType,
    CaseStudy,
    CaseType,
    Category,
    Confidence,
    ConfidenceScore,
    Funnel,
    Lever,
    Market,
    Metrics,
    Outcome,
    Platform,
)
from .storage import CaseLibrary, get_current_week_id


class FridayAnalyzer:
    """Cuma derin analiz ajanı - Top 2-3 vakayı detaylı incele."""

    def __init__(self, library: CaseLibrary):
        """
        Analiz ajanı başlatıcı.

        Args:
            library: Vaka kütüphanesi
        """
        self.library = library
        self.console = Console()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def analyze_case(self, url: str, title: Optional[str] = None) -> Optional[CaseStudy]:
        """
        Tek bir vakayı derin analiz et.

        Args:
            url: Vaka URL'i
            title: Vaka başlığı (opsiyonel)

        Returns:
            Derin analiz vakası veya None
        """
        self.console.print(f"\n[bold blue]🔬 Derin Analiz Başlıyor[/bold blue]\n")
        self.console.print(f"URL: {url}\n")

        try:
            # İçeriği çek
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            text_content = soup.get_text(separator=" ", strip=True)

            # Vaka ID oluştur
            week_id = get_current_week_id()
            case_count = len(self.library.load_case_studies(week_id=week_id)) + 1
            case_id = f"{week_id}-{case_count:03d}"

            # Başlık
            if not title:
                title_elem = soup.find(["h1", "title"])
                title = title_elem.get_text(strip=True) if title_elem else "Başlık Bulunamadı"

            # Metrikleri çıkar
            before_metrics, after_metrics = self._extract_metrics(text_content)

            # Platform belirle
            platform = self._determine_platform(url)

            # Pazar belirle
            market = self._determine_market(text_content)

            # Kategori belirle
            category = self._determine_category(text_content)

            # Hamleleri çıkar
            actions = self._extract_actions(text_content)

            # Hipotez oluştur
            hypothesis = self._generate_hypothesis(before_metrics, after_metrics, actions)

            # Dersler çıkar
            lessons = self._extract_lessons(text_content, before_metrics, after_metrics)

            # Güven puanı hesapla
            confidence_score = self._calculate_confidence_score(
                before_metrics, after_metrics, text_content, url
            )

            # Etiketler belirle
            tags = self._determine_tags(
                text_content, before_metrics, after_metrics, market, confidence_score
            )

            # CaseStudy oluştur
            case = CaseStudy(
                case_id=case_id,
                title=title,
                url=url,
                published_date=datetime.now(),  # VAR SAYIM - gerçek tarih parse edilebilir
                author_organization="BULUNAMADI",  # Manuel giriş gerekebilir
                platform=platform,
                market=market,
                product_category=category,
                brand_status="Belirsiz",  # Manuel giriş gerekebilir
                initial_problem=self._extract_problem(text_content),
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                actions=actions,
                hypothesis=hypothesis,
                alternative_explanations=self._find_alternative_explanations(text_content),
                actionable_lessons=lessons,
                risks_misleading_points=self._identify_risks(text_content, url),
                confidence_score=confidence_score,
                tags_market=tags["market"],
                tags_funnel=tags["funnel"],
                tags_campaign=tags["campaign"],
                tags_lever=tags["lever"],
                tags_outcome=tags["outcome"],
                tags_confidence=tags["confidence"],
            )

            # Kütüphaneye kaydet
            self.library.save_case_study(case)

            # Rapor göster
            self._display_case_report(case)

            return case

        except Exception as e:
            self.console.print(f"[bold red]❌ Analiz hatası: {e}[/bold red]")
            return None

    def _extract_metrics(self, text: str) -> tuple[Metrics, Metrics]:
        """
        Metinden önce/sonra metriklerini çıkar.

        Args:
            text: Analiz edilecek metin

        Returns:
            (önce_metrikleri, sonra_metrikleri)
        """
        # Basit regex tabanlı çıkarma (geliştirilmeli)
        before = Metrics()
        after = Metrics()

        # ACoS
        acos_match = re.search(r"acos.*?(\d+\.?\d*)%?.*?to.*?(\d+\.?\d*)%?", text, re.IGNORECASE)
        if acos_match:
            before.acos = float(acos_match.group(1))
            after.acos = float(acos_match.group(2))

        # ROAS
        roas_match = re.search(r"roas.*?(\d+\.?\d*).*?to.*?(\d+\.?\d*)", text, re.IGNORECASE)
        if roas_match:
            before.roas = float(roas_match.group(1))
            after.roas = float(roas_match.group(2))

        # CPC
        cpc_match = re.search(r"cpc.*?\$?(\d+\.?\d*).*?to.*?\$?(\d+\.?\d*)", text, re.IGNORECASE)
        if cpc_match:
            before.cpc = float(cpc_match.group(1))
            after.cpc = float(cpc_match.group(2))

        return before, after

    def _determine_platform(self, url: str) -> Platform:
        """URL'den platformu belirle."""
        if "reddit.com" in url:
            return Platform.REDDIT
        elif "linkedin.com" in url:
            return Platform.LINKEDIN
        elif "amazon.com" in url or "advertising.amazon" in url:
            return Platform.AMAZON_ADS
        else:
            return Platform.BLOG

    def _determine_market(self, text: str) -> Market:
        """Metinden pazarı belirle."""
        text_lower = text.lower()

        if "amazon.de" in text_lower or "germany" in text_lower:
            return Market.DE
        elif "amazon.co.uk" in text_lower or "uk marketplace" in text_lower:
            return Market.UK
        elif "amazon.fr" in text_lower or "france" in text_lower:
            return Market.FR
        elif "amazon.it" in text_lower or "italy" in text_lower:
            return Market.IT
        elif "amazon.es" in text_lower or "spain" in text_lower:
            return Market.ES
        elif "amazon.com" in text_lower or "us marketplace" in text_lower:
            return Market.US
        elif any(market in text_lower for market in ["europe", "eu marketplace"]):
            return Market.EU
        else:
            return Market.UNKNOWN

    def _determine_category(self, text: str) -> Category:
        """Metinden kategoriyi belirle."""
        text_lower = text.lower()

        if any(word in text_lower for word in ["home", "kitchen", "furniture"]):
            return Category.HOME_KITCHEN
        elif any(word in text_lower for word in ["tools", "hardware"]):
            return Category.TOOLS
        elif any(word in text_lower for word in ["beauty", "cosmetics", "skincare"]):
            return Category.BEAUTY
        elif any(word in text_lower for word in ["sports", "outdoor", "fitness"]):
            return Category.SPORTS_OUTDOORS
        else:
            return Category.OTHER

    def _extract_actions(self, text: str) -> Actions:
        """Metinden yapılan hamleleri çıkar."""
        actions = Actions()

        # Keyword stratejisi
        if re.search(r"keyword.*strateg|broad.*exact|phrase match", text, re.IGNORECASE):
            actions.match_keyword_strategy = "Keyword stratejisi değiştirildi (detay metinde)"

        # Negatif keyword
        if re.search(r"negative.*keyword|excluded.*search", text, re.IGNORECASE):
            actions.negative_strategy = "Negatif keyword stratejisi uygulandı"

        # Bidding
        if re.search(r"bid.*adjust|bidding.*strateg|increased.*bid", text, re.IGNORECASE):
            actions.bidding_approach = "Teklif stratejisi değiştirildi"

        # Placement
        if re.search(r"placement.*adjust|top of search", text, re.IGNORECASE):
            actions.placement_settings = "Placement ayarları optimize edildi"

        return actions

    def _generate_hypothesis(
        self, before: Metrics, after: Metrics, actions: Actions
    ) -> str:
        """Sonuçların olası nedenini hipotez olarak oluştur."""
        changes = []

        if before.acos and after.acos and after.acos < before.acos:
            changes.append("ACoS azalması")

        if actions.match_keyword_strategy:
            changes.append("keyword stratejisi değişikliği")

        if actions.bidding_approach:
            changes.append("teklif optimizasyonu")

        if changes:
            return f"En olası neden: {', '.join(changes)}. VAR SAYIM: Daha detaylı analiz gerekli."
        else:
            return "BULUNAMADI - Yeterli veri yok"

    def _extract_lessons(
        self, text: str, before: Metrics, after: Metrics
    ) -> list[str]:
        """Metinden uygulanabilir dersler çıkar."""
        lessons = []

        # Basit IF-THEN dersler
        if before.acos and after.acos and after.acos < before.acos:
            lessons.append(
                f"IF: ACoS yüksekse → THEN: Keyword ve teklif stratejisini gözden geçir"
            )

        if "negative keyword" in text.lower():
            lessons.append(
                "IF: İlgisiz tıklamalar varsa → THEN: Negatif keyword stratejisi uygula"
            )

        if "bid adjustment" in text.lower():
            lessons.append(
                "IF: Dönüşüm düşükse → THEN: Teklif ayarlarını optimize et"
            )

        # Varsayılan dersler
        if not lessons:
            lessons.append("VAR SAYIM: Manuel analiz gerekli - otomatik ders çıkarılamadı")

        return lessons[:10]  # Maksimum 10 ders

    def _calculate_confidence_score(
        self, before: Metrics, after: Metrics, text: str, url: str
    ) -> ConfidenceScore:
        """Güven puanı hesapla (rubrik tabanlı)."""
        # 1. Metrik şeffaflığı (0-25)
        metric_count = before.count_available_metrics() + after.count_available_metrics()
        metric_transparency = min(metric_count * 2, 25)

        # 2. İlk elden anlatım (0-20)
        first_hand_keywords = ["we implemented", "our campaign", "i tested", "my strategy"]
        first_hand_score = 15 if any(kw in text.lower() for kw in first_hand_keywords) else 5

        # 3. Yöntem açıklığı (0-20)
        method_keywords = ["step by step", "first we", "then we", "process", "how we"]
        method_clarity = 15 if any(kw in text.lower() for kw in method_keywords) else 8

        # 4. Çarpıtma riski (0-15, ters puanlama)
        agency_keywords = ["our agency", "client success", "case study"]
        bias_risk = 5 if any(kw in text.lower() for kw in agency_keywords) else 15

        # 5. Genellenebilirlik (0-20)
        generalizable_keywords = ["similar", "can apply", "works for", "strategy"]
        generalizability = 15 if any(kw in text.lower() for kw in generalizable_keywords) else 10

        score = ConfidenceScore(
            metric_transparency=metric_transparency,
            first_hand_verification=first_hand_score,
            method_clarity=method_clarity,
            bias_risk=bias_risk,
            generalizability=generalizability,
            total=metric_transparency + first_hand_score + method_clarity + bias_risk + generalizability,
        )

        return score

    def _determine_tags(
        self, text: str, before: Metrics, after: Metrics, market: Market, confidence: ConfidenceScore
    ) -> dict:
        """Vaka etiketlerini belirle."""
        # Funnel
        funnel = Funnel.LAUNCH
        if "launch" in text.lower():
            funnel = Funnel.LAUNCH
        elif "scale" in text.lower() or "growth" in text.lower():
            funnel = Funnel.SCALE
        elif "recover" in text.lower() or "fix" in text.lower():
            funnel = Funnel.RECOVER

        # Campaign types
        campaign_types = []
        if "sponsored products" in text.lower() or "sp" in text.lower():
            campaign_types.append(CampaignType.SP)
        if "sponsored brands" in text.lower() or "sb" in text.lower():
            campaign_types.append(CampaignType.SB)
        if "sponsored display" in text.lower() or "sd" in text.lower():
            campaign_types.append(CampaignType.SD)

        if not campaign_types:
            campaign_types.append(CampaignType.SP)  # Varsayılan

        # Levers
        levers = []
        if "bid" in text.lower():
            levers.append(Lever.BIDDING)
        if "keyword" in text.lower():
            levers.append(Lever.KEYWORD)
        if "negative" in text.lower():
            levers.append(Lever.NEGATIVE)

        if not levers:
            levers.append(Lever.STRUCTURE)  # Varsayılan

        # Outcomes
        outcomes = []
        if before.acos and after.acos and after.acos < before.acos:
            outcomes.append(Outcome.ACOS_DOWN)
        if before.sales and after.sales and after.sales > before.sales:
            outcomes.append(Outcome.SALES_UP)

        if not outcomes:
            outcomes.append(Outcome.ACOS_DOWN)  # Varsayılan

        # Confidence level
        if confidence.total >= 75:
            conf_level = Confidence.HIGH
        elif confidence.total >= 50:
            conf_level = Confidence.MED
        else:
            conf_level = Confidence.LOW

        return {
            "market": market,
            "funnel": funnel,
            "campaign": campaign_types,
            "lever": levers,
            "outcome": outcomes,
            "confidence": conf_level,
        }

    def _extract_problem(self, text: str) -> str:
        """Başlangıç problemini çıkar."""
        problem_keywords = [
            "high acos",
            "low conversion",
            "poor performance",
            "struggling",
            "problem",
        ]

        text_lower = text.lower()
        for keyword in problem_keywords:
            if keyword in text_lower:
                return f"Problem tespit edildi: {keyword}"

        return "BULUNAMADI - Manuel giriş gerekli"

    def _find_alternative_explanations(self, text: str) -> Optional[str]:
        """Alternatif açıklamaları bul."""
        alt_keywords = ["seasonal", "price change", "promotion", "competitor", "external"]

        text_lower = text.lower()
        found = [kw for kw in alt_keywords if kw in text_lower]

        if found:
            return f"Olası alternatif faktörler: {', '.join(found)}"

        return None

    def _identify_risks(self, text: str, url: str) -> str:
        """Riskler ve yanıltıcı noktaları tespit et."""
        risks = []

        if "agency" in url.lower() or "agency" in text.lower():
            risks.append("Ajans pazarlaması riski - objektiflik sorunu olabilir")

        if "case study" in text.lower() and "result" not in text.lower():
            risks.append("Metrik eksikliği - 'case study' başlıklı ama sonuç verisi zayıf")

        if len(text) < 500:
            risks.append("Kısa içerik - detay eksikliği")

        if risks:
            return " | ".join(risks)
        else:
            return "Belirgin risk tespit edilmedi"

    def _display_case_report(self, case: CaseStudy) -> None:
        """Vaka raporunu güzel formatta göster."""
        report = f"""
# 📊 VAKA ANALİZ RAPORU

**Vaka ID:** {case.case_id}
**Başlık:** {case.title}
**Pazar:** {case.market.value} | **Kategori:** {case.product_category.value}

---

## 📈 METRİKLER

### Önce
- ACoS: {case.before_metrics.acos or 'BULUNAMADI'}
- ROAS: {case.before_metrics.roas or 'BULUNAMADI'}
- CPC: ${case.before_metrics.cpc or 'BULUNAMADI'}

### Sonra
- ACoS: {case.after_metrics.acos or 'BULUNAMADI'}
- ROAS: {case.after_metrics.roas or 'BULUNAMADI'}
- CPC: ${case.after_metrics.cpc or 'BULUNAMADI'}

---

## 🎯 GÜVEN PUANI: {case.confidence_score.total}/100

- Metrik Şeffaflığı: {case.confidence_score.metric_transparency}/25
- İlk Elden Doğrulama: {case.confidence_score.first_hand_verification}/20
- Yöntem Açıklığı: {case.confidence_score.method_clarity}/20
- Çarpıtma Riski: {case.confidence_score.bias_risk}/15
- Genellenebilirlik: {case.confidence_score.generalizability}/20

**Güven Seviyesi:** {case.tags_confidence.value}

---

## 💡 UYGULANABILIR DERSLER

{chr(10).join(f'{i}. {lesson}' for i, lesson in enumerate(case.actionable_lessons, 1))}

---

## ⚠️ RİSKLER

{case.risks_misleading_points}

---

## 🏷️ ETİKETLER

- Pazar: {case.tags_market.value}
- Hunisi: {case.tags_funnel.value}
- Kampanya: {', '.join(c.value for c in case.tags_campaign)}
- Kaldıraç: {', '.join(l.value for l in case.tags_lever)}
- Sonuç: {', '.join(o.value for o in case.tags_outcome)}
        """

        md = Markdown(report.strip())
        self.console.print(Panel(md, title="Derin Analiz Raporu", border_style="green"))
