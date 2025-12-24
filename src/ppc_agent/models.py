"""Amazon PPC Vaka Avcısı - Veri Modelleri."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class Market(str, Enum):
    """Amazon pazarları."""

    US = "US"
    EU = "EU"
    DE = "DE"
    UK = "UK"
    FR = "FR"
    IT = "IT"
    ES = "ES"
    UNKNOWN = "Belirsiz"


class Platform(str, Enum):
    """Kaynak platformlar."""

    REDDIT = "Reddit"
    LINKEDIN = "LinkedIn"
    BLOG = "Blog"
    AMAZON_ADS = "Amazon Ads"
    OTHER = "Diğer"


class Category(str, Enum):
    """Ürün kategorileri."""

    HOME_KITCHEN = "Home&Kitchen"
    TOOLS = "Tools"
    BEAUTY = "Beauty"
    SPORTS_OUTDOORS = "Sports&Outdoors"
    OTHER = "Diğer"


class CaseType(str, Enum):
    """Vaka tipleri."""

    LAUNCH = "Launch"
    RESTRUCTURE = "Restructure"
    KEYWORD = "Keyword"
    BIDDING = "Bidding"
    CREATIVE = "Creative"
    DSP = "DSP"
    BRAND = "Brand"
    SB = "SB"
    SD = "SD"
    OTHER = "Diğer"


class Funnel(str, Enum):
    """Kampanya hunisi aşamaları."""

    LAUNCH = "Launch"
    SCALE = "Scale"
    RECOVER = "Recover"


class CampaignType(str, Enum):
    """Kampanya tipleri."""

    SP = "SP"
    SB = "SB"
    SD = "SD"
    DSP = "DSP"


class Lever(str, Enum):
    """Uygulanan değişiklik türleri."""

    BIDDING = "Bidding"
    STRUCTURE = "Structure"
    KEYWORD = "Keyword"
    NEGATIVE = "Negative"
    CREATIVE = "Creative"
    LISTING = "Listing"
    PRICING = "Pricing"
    PROMO = "Promo"


class Outcome(str, Enum):
    """Sonuç metrikleri."""

    ACOS_DOWN = "ACoS↓"
    TACOS_DOWN = "TACoS↓"
    SALES_UP = "Sales↑"
    CVR_UP = "CVR↑"
    CPC_DOWN = "CPC↓"
    CTR_UP = "CTR↑"


class Confidence(str, Enum):
    """Güven seviyesi."""

    LOW = "Low"
    MED = "Med"
    HIGH = "High"


class Metrics(BaseModel):
    """PPC Metrikleri (Önce/Sonra)."""

    spend: Optional[float] = Field(None, description="Harcama ($)")
    sales: Optional[float] = Field(None, description="Satış ($)")
    acos: Optional[float] = Field(None, description="ACoS (%)")
    tacos: Optional[float] = Field(None, description="TACoS (%)")
    roas: Optional[float] = Field(None, description="ROAS")
    cpc: Optional[float] = Field(None, description="CPC ($)")
    ctr: Optional[float] = Field(None, description="CTR (%)")
    cvr: Optional[float] = Field(None, description="CVR (%)")
    impressions: Optional[int] = Field(None, description="Gösterimler")
    clicks: Optional[int] = Field(None, description="Tıklamalar")

    def count_available_metrics(self) -> int:
        """Mevcut metrik sayısını döndür."""
        return sum(
            1
            for field in [
                self.spend,
                self.sales,
                self.acos,
                self.tacos,
                self.roas,
                self.cpc,
                self.ctr,
                self.cvr,
                self.impressions,
                self.clicks,
            ]
            if field is not None
        )


class CaseCandidate(BaseModel):
    """Pazartesi taramasında bulunan aday vaka."""

    title: str = Field(..., description="Vaka başlığı")
    url: HttpUrl = Field(..., description="Vaka URL'i")
    date: datetime = Field(..., description="Yayın tarihi")
    platform: Platform = Field(..., description="Platform")
    market: Market = Field(Market.UNKNOWN, description="Pazar yeri")
    category: Category = Field(Category.OTHER, description="Ürün kategorisi")
    case_type: CaseType = Field(CaseType.OTHER, description="Vaka tipi")
    visible_metrics: list[str] = Field(
        default_factory=list, description="Görülen metrikler"
    )
    has_before_after: bool = Field(False, description="Önce/sonra var mı?")
    summary: str = Field(..., description="1 cümlelik özet")
    preliminary_confidence: int = Field(
        ..., ge=0, le=100, description="Ön güven puanı (0-100)"
    )
    confidence_reason: str = Field(..., description="Güven puanı nedeni")
    scraped_at: datetime = Field(
        default_factory=datetime.now, description="Tarama zamanı"
    )


class Actions(BaseModel):
    """Vakada yapılan hamleler."""

    campaign_structure: Optional[str] = Field(None, description="Kampanya yapısı değişikliği")
    match_keyword_strategy: Optional[str] = Field(
        None, description="Match type/keyword stratejisi"
    )
    negative_strategy: Optional[str] = Field(None, description="Negatif stratejisi")
    bidding_approach: Optional[str] = Field(None, description="Teklif yaklaşımı")
    placement_settings: Optional[str] = Field(None, description="Placement ayarları")
    sb_sd_dsp_usage: Optional[str] = Field(None, description="SB/SD/DSP kullanımı")
    creative_listing: Optional[str] = Field(None, description="Kreatif/liste iyileştirmesi")
    timeline: Optional[str] = Field(None, description="Zaman çizelgesi")


class ConfidenceScore(BaseModel):
    """Güven puanı detayları."""

    metric_transparency: int = Field(..., ge=0, le=25, description="Metrik şeffaflığı")
    first_hand_verification: int = Field(
        ..., ge=0, le=20, description="İlk elden anlatım"
    )
    method_clarity: int = Field(..., ge=0, le=20, description="Yöntem açıklığı")
    bias_risk: int = Field(..., ge=0, le=15, description="Çarpıtma riski (ters)")
    generalizability: int = Field(..., ge=0, le=20, description="Genellenebilirlik")
    total: int = Field(..., ge=0, le=100, description="Toplam puan")

    def calculate_total(self) -> int:
        """Toplam puanı hesapla."""
        return (
            self.metric_transparency
            + self.first_hand_verification
            + self.method_clarity
            + self.bias_risk
            + self.generalizability
        )


class CaseStudy(BaseModel):
    """Derin analiz edilmiş tam vaka çalışması."""

    # A) Kimlik ve Bağlam
    case_id: str = Field(..., description="Vaka ID (YYYY-WW-### formatı)")
    title: str = Field(..., description="Vaka başlığı")
    url: HttpUrl = Field(..., description="Vaka URL'i")
    published_date: datetime = Field(..., description="Yayın tarihi")
    author_organization: str = Field(..., description="Yazar/Kurum")
    platform: Platform = Field(..., description="Platform")
    market: Market = Field(..., description="Pazar yeri")
    product_category: Category = Field(..., description="Ürün kategorisi")
    brand_status: str = Field(..., description="Marka durumu")
    initial_problem: str = Field(..., description="Başlangıç problemi")

    # B) Metrikler
    before_metrics: Metrics = Field(..., description="Önce metrikleri")
    after_metrics: Metrics = Field(..., description="Sonra metrikleri")

    # C) Hamleler
    actions: Actions = Field(..., description="Yapılan hamleler")

    # D) Analiz
    hypothesis: str = Field(..., description="Sonuçların olası nedeni")
    alternative_explanations: Optional[str] = Field(
        None, description="Alternatif açıklamalar"
    )

    # E) Dersler
    actionable_lessons: list[str] = Field(
        ..., description="Uygulanabilir dersler (IF → THEN)"
    )

    # F) Riskler
    risks_misleading_points: Optional[str] = Field(
        None, description="Riskler / Yanıltıcı noktalar"
    )

    # G) Güven Puanı
    confidence_score: ConfidenceScore = Field(..., description="Güven puanı detayları")

    # H) Etiketler
    tags_market: Market = Field(..., description="Pazar etiketi")
    tags_funnel: Funnel = Field(..., description="Hunisi etiketi")
    tags_campaign: list[CampaignType] = Field(..., description="Kampanya etiketi")
    tags_lever: list[Lever] = Field(..., description="Değişiklik etiketi")
    tags_outcome: list[Outcome] = Field(..., description="Sonuç etiketi")
    tags_confidence: Confidence = Field(..., description="Güven seviyesi")

    # Meta
    analyzed_at: datetime = Field(
        default_factory=datetime.now, description="Analiz zamanı"
    )


class WeeklyReport(BaseModel):
    """Haftalık rapor."""

    week_id: str = Field(..., description="Hafta ID (YYYY-WW)")
    week_start: datetime = Field(..., description="Hafta başlangıç tarihi")
    week_end: datetime = Field(..., description="Hafta bitiş tarihi")

    # Pazartesi Tarama
    monday_scan_date: datetime = Field(..., description="Tarama tarihi")
    candidates_found: int = Field(..., description="Bulunan aday sayısı")
    candidates: list[CaseCandidate] = Field(..., description="Aday listesi")
    top_3_for_friday: list[str] = Field(
        ..., description="Cuma için önerilen top 3 (URL listesi)"
    )

    # Cuma Analiz
    friday_analysis_date: Optional[datetime] = Field(
        None, description="Analiz tarihi"
    )
    cases_analyzed: int = Field(0, description="Analiz edilen vaka sayısı")
    case_studies: list[CaseStudy] = Field(
        default_factory=list, description="Derin analiz vakaları"
    )

    # Aksiyon Önerileri
    top_5_actions: list[str] = Field(
        default_factory=list, description="Bu hafta uygulanacak 5 aksiyon"
    )

    # Meta
    created_at: datetime = Field(
        default_factory=datetime.now, description="Oluşturulma zamanı"
    )
