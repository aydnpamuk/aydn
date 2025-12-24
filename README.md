# Amazon PPC Vaka Avcısı 🔍

Her hafta **gerçek**, **metrik içeren**, **kaynağı doğrulanabilir** Amazon PPC vaka örneklerini bul, analiz et ve kütüphanele.

## Özellikler

- ✅ **Pazartesi Hızlı Tarama**: Reddit, LinkedIn, blog kaynaklarından 8-15 aday vaka bul
- ✅ **Cuma Derin Analiz**: Top 2-3 vakayı detaylı incele, güven puanı ver
- ✅ **Akıllı Kütüphane**: JSON tabanlı veri saklama, etiketleme, arama
- ✅ **Güven Puanlama**: 0-100 arası objektif güvenilirlik puanı
- ✅ **Uygulanabilir Dersler**: Her vakadan IF-THEN formatında dersler çıkar

## Proje Yapısı

```
src/ppc_agent/
├── models.py          # Pydantic veri modelleri
├── storage.py         # JSON kütüphane sistemi
├── scrapers.py        # Reddit/Blog scraper'lar
├── monday_agent.py    # Pazartesi tarama ajanı
├── friday_agent.py    # Cuma analiz ajanı
└── cli.py            # CLI komutları

data/case_library/     # Vaka kütüphanesi
├── candidates/        # Pazartesi adayları
├── cases/            # Derin analiz vakaları
└── reports/          # Haftalık raporlar
```

## Kurulum

### 1. Bağımlılıkları yükle

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
```

### 2. Reddit API ayarla (opsiyonel ama önerilen)

Reddit API key almak için: https://www.reddit.com/prefs/apps

```bash
cp .env.example .env
# .env dosyasını düzenle ve Reddit bilgilerini ekle
```

### 3. Testi çalıştır

```bash
make test
python -m src.app --help
```

## Kullanım

### Pazartesi Tarama (20 dakika)

Son 7 günün PPC vakalarını tara:

```bash
python -m src.app scan --days 7
```

Çıktı:
- Toplam aday sayısı
- Top 3 öneri (Cuma için)
- Detaylı aday listesi tablosu
- Adaylar `data/case_library/candidates/` dizinine kaydedilir

### Cuma Derin Analiz (1 saat)

Belirli bir URL'i derin analiz et:

```bash
python -m src.app analyze --url "https://example.com/case-study" --title "Vaka Başlığı"
```

Çıktı:
- Metrik analizi (önce/sonra)
- Güven puanı (0-100) + rubrik
- Uygulanabilir dersler (IF-THEN)
- Risk değerlendirmesi
- Etiketler (pazar, hunisi, kampanya, vb.)
- Vaka `data/case_library/cases/` dizinine kaydedilir

### Raporlar ve İstatistikler

Kütüphane istatistikleri:

```bash
python -m src.app report --stats
```

Haftalık rapor:

```bash
python -m src.app report --week current
python -m src.app report --week 2025-W01
```

Vaka listesi:

```bash
python -m src.app report --list --limit 10
```

### Arama

Belirli kriterlerde vaka ara:

```bash
# Pazar bazlı arama
python -m src.app search --market US --min-confidence 70

# Kategori bazlı arama
python -m src.app search --category "Home&Kitchen" --limit 5
```

## Komutlar

| Komut | Açıklama | Örnek |
|-------|----------|-------|
| `scan` | Pazartesi hızlı tarama | `python -m src.app scan --days 7` |
| `analyze` | Cuma derin analiz | `python -m src.app analyze --url "..."` |
| `report` | Raporlar ve istatistikler | `python -m src.app report --stats` |
| `search` | Kütüphane araması | `python -m src.app search --market US` |

## Haftalık Rutin

### Pazartesi (20 dk)

```bash
python -m src.app scan --days 7
```

1. Reddit, blog kaynaklarını tara
2. 8-15 aday vaka bul
3. Top 3 öneriyi belirle

### Cuma (1 saat)

```bash
python -m src.app analyze --url "<top-1-url>"
python -m src.app analyze --url "<top-2-url>"
python -m src.app analyze --url "<top-3-url>"
```

1. Top 2-3 vakayı derin analiz et
2. Metrik çıkar, güven puanı ver
3. Uygulanabilir dersler oluştur

### Haftalık Rapor

```bash
python -m src.app report --week current
```

## Geliştirme

Format ve lint:

```bash
make fmt
make lint
```

Testler:

```bash
make test
```

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'feat: Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## Lisans

Bu proje açık kaynaklıdır.

---

**Not**: Bu ajan gerçek veri toplar. Toplanan verilerin doğruluğunu her zaman manuel olarak kontrol edin.
