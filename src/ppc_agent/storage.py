"""Amazon PPC Vaka Avcısı - Veri Saklama Katmanı."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import CaseCandidate, CaseStudy, WeeklyReport


class CaseLibrary:
    """Vaka kütüphanesi - JSON tabanlı veri saklama."""

    def __init__(self, library_path: str = "data/case_library"):
        """
        Kütüphane başlatıcı.

        Args:
            library_path: Kütüphane veri dizini
        """
        self.library_path = Path(library_path)
        self.candidates_dir = self.library_path / "candidates"
        self.cases_dir = self.library_path / "cases"
        self.reports_dir = self.library_path / "reports"

        # Dizinleri oluştur
        self._init_directories()

    def _init_directories(self) -> None:
        """Kütüphane dizinlerini oluştur."""
        self.library_path.mkdir(parents=True, exist_ok=True)
        self.candidates_dir.mkdir(exist_ok=True)
        self.cases_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

    def save_candidate(self, candidate: CaseCandidate) -> Path:
        """
        Aday vakayı kaydet.

        Args:
            candidate: Kaydedilecek aday vaka

        Returns:
            Kaydedilen dosyanın yolu
        """
        # Dosya adı: YYYY-MM-DD_HH-MM-SS.json
        timestamp = candidate.scraped_at.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}.json"
        filepath = self.candidates_dir / filename

        with filepath.open("w", encoding="utf-8") as f:
            json.dump(candidate.model_dump(mode="json"), f, ensure_ascii=False, indent=2)

        return filepath

    def save_case_study(self, case: CaseStudy) -> Path:
        """
        Derin analiz vakasını kaydet.

        Args:
            case: Kaydedilecek vaka çalışması

        Returns:
            Kaydedilen dosyanın yolu
        """
        filename = f"{case.case_id}.json"
        filepath = self.cases_dir / filename

        with filepath.open("w", encoding="utf-8") as f:
            json.dump(case.model_dump(mode="json"), f, ensure_ascii=False, indent=2)

        return filepath

    def save_weekly_report(self, report: WeeklyReport) -> Path:
        """
        Haftalık raporu kaydet.

        Args:
            report: Kaydedilecek haftalık rapor

        Returns:
            Kaydedilen dosyanın yolu
        """
        filename = f"{report.week_id}.json"
        filepath = self.reports_dir / filename

        with filepath.open("w", encoding="utf-8") as f:
            json.dump(report.model_dump(mode="json"), f, ensure_ascii=False, indent=2)

        return filepath

    def load_candidates(self, limit: Optional[int] = None) -> list[CaseCandidate]:
        """
        Aday vakaları yükle.

        Args:
            limit: Yüklenecek maksimum aday sayısı

        Returns:
            Aday vaka listesi
        """
        candidates = []
        files = sorted(self.candidates_dir.glob("*.json"), reverse=True)

        if limit:
            files = files[:limit]

        for filepath in files:
            with filepath.open("r", encoding="utf-8") as f:
                data = json.load(f)
                candidates.append(CaseCandidate.model_validate(data))

        return candidates

    def load_case_studies(
        self, week_id: Optional[str] = None, limit: Optional[int] = None
    ) -> list[CaseStudy]:
        """
        Vaka çalışmalarını yükle.

        Args:
            week_id: Belirli bir haftanın vakaları (ör. "2025-W01")
            limit: Yüklenecek maksimum vaka sayısı

        Returns:
            Vaka çalışması listesi
        """
        cases = []
        files = sorted(self.cases_dir.glob("*.json"), reverse=True)

        for filepath in files:
            with filepath.open("r", encoding="utf-8") as f:
                data = json.load(f)
                case = CaseStudy.model_validate(data)

                # Hafta filtresi
                if week_id and not case.case_id.startswith(week_id):
                    continue

                cases.append(case)

                if limit and len(cases) >= limit:
                    break

        return cases

    def load_weekly_report(self, week_id: str) -> Optional[WeeklyReport]:
        """
        Haftalık raporu yükle.

        Args:
            week_id: Hafta ID (YYYY-WW)

        Returns:
            Haftalık rapor veya None
        """
        filepath = self.reports_dir / f"{week_id}.json"

        if not filepath.exists():
            return None

        with filepath.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return WeeklyReport.model_validate(data)

    def get_latest_report(self) -> Optional[WeeklyReport]:
        """
        En son haftalık raporu getir.

        Returns:
            En son rapor veya None
        """
        files = sorted(self.reports_dir.glob("*.json"), reverse=True)

        if not files:
            return None

        with files[0].open("r", encoding="utf-8") as f:
            data = json.load(f)
            return WeeklyReport.model_validate(data)

    def search_cases(
        self,
        market: Optional[str] = None,
        category: Optional[str] = None,
        min_confidence: Optional[int] = None,
    ) -> list[CaseStudy]:
        """
        Vakalarda arama yap.

        Args:
            market: Pazar filtresi
            category: Kategori filtresi
            min_confidence: Minimum güven puanı

        Returns:
            Filtrelenmiş vaka listesi
        """
        cases = self.load_case_studies()
        filtered = []

        for case in cases:
            # Market filtresi
            if market and case.market.value != market:
                continue

            # Kategori filtresi
            if category and case.product_category.value != category:
                continue

            # Güven puanı filtresi
            if min_confidence and case.confidence_score.total < min_confidence:
                continue

            filtered.append(case)

        return filtered

    def get_statistics(self) -> dict:
        """
        Kütüphane istatistiklerini getir.

        Returns:
            İstatistik bilgileri
        """
        total_candidates = len(list(self.candidates_dir.glob("*.json")))
        total_cases = len(list(self.cases_dir.glob("*.json")))
        total_reports = len(list(self.reports_dir.glob("*.json")))

        cases = self.load_case_studies()

        avg_confidence = 0
        if cases:
            avg_confidence = sum(c.confidence_score.total for c in cases) / len(cases)

        return {
            "total_candidates": total_candidates,
            "total_cases": total_cases,
            "total_reports": total_reports,
            "average_confidence_score": round(avg_confidence, 2),
            "library_path": str(self.library_path),
        }


def get_current_week_id() -> str:
    """
    Mevcut haftanın ID'sini getir (YYYY-WW formatı).

    Returns:
        Hafta ID
    """
    now = datetime.now()
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"
