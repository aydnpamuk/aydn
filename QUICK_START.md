# 🚀 Quick Start Guide

## Hızlı Başlangıç

### 1️⃣ En Sık Kullanılan Komutlar

```bash
# Kampanya performansını analiz et
python -m src.cli.app metrics calculate \
    --ad-spend 500 \
    --ad-sales 2000 \
    --total-sales 5000 \
    --impressions 10000 \
    --clicks 100 \
    --orders 10

# Stok durumunu kontrol et
python -m src.cli.app crisis check-stock 100 5.0

# Hızlı ACoS hesaplama
python -m src.cli.app metrics acos 500 2000
```

### 2️⃣ Demo Senaryoları

```bash
# Tüm özellikleri gösteren demo
PYTHONPATH=. python examples/demo.py

# Kampanya analizi senaryosu
PYTHONPATH=. python examples/scenario_campaign_analysis.py

# Stok krizi senaryosu
PYTHONPATH=. python examples/scenario_stock_crisis.py

# Golden Rules kontrolü
PYTHONPATH=. python examples/scenario_golden_rules.py
```

## 📊 En Önemli Metrikler

### ACoS (Advertising Cost of Sale)
```
ACoS = (Reklam Harcaması / Reklam Satışları) × 100

✓✓✓ Mükemmel: < 15%
✓✓  İyi: 15-20%
✓   Ortalama: 20-35%
⚠️   Yüksek: 35-50%
❌  Kârsız: > 50%
```

### TACOS (Total Advertising Cost of Sale)
```
TACOS = (Toplam Reklam / Toplam Satış) × 100

Muhafazakar: 5-8%
Standart (Sağlıklı): 8-12% ⭐
Agresif: 12-20%
Ultra Agresif: > 20%
```

### Optimal Bid (RPC Formülü)
```
RPC = Toplam Satış / Toplam Tıklama
Optimal Bid = RPC × Target ACoS

Örnek:
- Satış: $1,000
- Tıklama: 200
- RPC: $5
- Hedef ACoS: 25%
→ Optimal Bid: $1.25
```

## 🛡️ 5 Golden Rules

| # | Kural | Açıklama |
|---|-------|----------|
| 1️⃣ | **ASLA STOKSUZ KALMA** | Min 4 haftalık stok tamponu |
| 2️⃣ | **BÜTÇEYI ERKEN TÜKETME** | Saat 18:00'e kadar max %70 |
| 3️⃣ | **SÜREKLI REKLAM VER** | Momentum kırılmasın |
| 4️⃣ | **VERİYE SAYGI GÖSTER** | Min 20 tıklama gerekli |
| 5️⃣ | **SEO + PPC BİRLİKTE** | Organic:PPC min 2:1 |

## 🎯 Gerçek Dünya Örnekleri

### Örnek 1: ACoS %35'ten %21'e Düşürme

```python
from src.core.formulas.bid_optimization import RPCBidOptimizer

# Mevcut durum
current_bid = 7.50
total_sales = 3500
total_clicks = 180
target_acos = 0.25

# Öneri al
recommendation = RPCBidOptimizer.recommend_bid_adjustment(
    current_bid=current_bid,
    total_sales=total_sales,
    total_clicks=total_clicks,
    target_acos=target_acos,
    current_acos=0.357
)

print(f"Yeni bid: ${recommendation.recommended_bid}")
# Output: Yeni bid: $4.86 (35% düşüş)
```

**Sonuç:**
- Bid: $7.50 → $4.86
- ACoS: %35.7 → ~%21 (tahmini)
- ✓ Hedefe ulaşıldı!

### Örnek 2: Stok Krizi Önleme

```python
from src.crisis.stockout.protocol import StockoutProtocol

analysis = StockoutProtocol.analyze_stock_situation(
    current_stock=50,
    daily_velocity=8.0,
    lead_time_days=30
)

print(f"Kalan gün: {analysis.days_remaining:.1f}")
# Output: Kalan gün: 6.2

if analysis.stock_level == "CRITICAL":
    print("🚨 ACİL: Stok siparişi ver!")
    print("⚠️  PPC bütçesini %50 azalt!")
```

### Örnek 3: CTR Düşükse Ne Yapmalı?

```python
from src.decision.ctr.optimizer import CTROptimizer

if ctr < 0.3:  # Poor performance
    actions = [
        "🖼️  Ana görseli değiştir (anahtar kelime ekle)",
        "💰 Fiyatı rakiplerle karşılaştır",
        "⭐ Review sayısını artır",
        "📝 Başlığı optimize et"
    ]
```

## 🔧 Troubleshooting

### Problem: "ACoS çok yüksek (%50+)"

**Çözüm:**
1. Kaç tıklama var? < 20 ise → Bekle, veri yetersiz
2. CVR > %10 mu? → Evet: Bid çok yüksek, düşür
3. CVR < %10 mu? → Hayır: Keyword-product mismatch, negatifle

### Problem: "Bütçe saat 10'da bitiyor"

**Çözüm:**
1. Bid'leri %15-20 düşür
2. Gün boyunca görünür kalmak > Yüksek teklifle kısa süre görünmek
3. Hedef: Saat 18:00'de %70 tüketim

### Problem: "Organik rank düştü"

**Olası Nedenler:**
1. Stok tükendi mi? → Acil stok ekle
2. PPC durdu mu? → Hemen başlat
3. Rakip agresifleşti mi? → Competitor analizi yap
4. Review düştü mü? → Review stratejisi

## 📈 Haftalık Checklist

- [ ] Search Term Report analizi (wasted spend)
- [ ] Top 10 keyword performansı
- [ ] Bütçe tüketim oranı kontrolü
- [ ] Stok seviyesi (4 hafta+?)
- [ ] Negatif keyword ekleme
- [ ] ACoS trend analizi

## 🎓 İleri Seviye Özellikler

### Placement Modifiers
```python
from src.core.formulas.bid_optimization import PlacementModifierOptimizer

# Top of Search için öneri
tos_modifier = PlacementModifierOptimizer.recommend_tos_modifier(
    review_count=250,
    rating=4.6,
    price_competitive=True,
    main_image_quality="excellent"
)
# Sonuç: +100% (çok agresif)
```

### Strike Zone Analizi
```
Organik Rank 20-50 arasındaki keywordler:
- Az bir PPC desteğiyle ilk sayfaya çıkabilir
- En yüksek ROI potansiyeli
- PPC'yi organik'e dönüştürme fırsatı
```

### Benchmark Evaluation
```python
from src.core.benchmarks.standards import BenchmarkEvaluator

results = BenchmarkEvaluator.evaluate_all(
    ctr_ppc=0.65,
    cvr=12.0,
    acos=28.0,
    tacos=10.0
)
# Her metrik için performans seviyesi
```

## 💡 Pro Tips

1. **Test yavaş, ölçeklendir hızlı**: Yeni keyword/campaign test ederken düşük bütçe, başarılıysa hızlı ölçeklendir

2. **Negatif = Altın**: Wasted spend'i azaltmak, bid artırmaktan daha kolay ACoS düşürür

3. **Organik güçlüyse CPC düşer**: Amazon, alakalı ürünleri ödüllendirir

4. **Data > Sezgi**: 20 tıklama altı veriyle karar verme

5. **Momentum kutsaldır**: Bir kez kırılınca 2-4 hafta geri kazanmak gerekir

## 🆘 Destek

- **Dokümantasyon**: [README.md](README.md)
- **Detaylı Kullanım**: [USAGE.md](USAGE.md)
- **Örnekler**: `examples/` klasörü
- **Testler**: `pytest tests/`

---

**Hazırladı:** Amazon PPC & SEO Management System v1.0.0
**Temel:** Amazon PPC & SEO Bible v3.0 (9.5/10)
