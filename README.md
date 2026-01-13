# AYDN - Amazon Review Analyzer

**Ethical and Compliant Amazon Product Review Analysis Tool**

![Status](https://img.shields.io/badge/status-production-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
![React](https://img.shields.io/badge/react-18-blue)

---

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Mimari](#-mimari)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [API Dokümantasyonu](#-api-dokümantasyonu)
- [Uyumluluk ve Etik](#-uyumluluk-ve-etik)
- [Teknoloji Stack](#-teknoloji-stack)
- [Katkıda Bulunma](#-katkıda-bulunma)

---

## ✨ Özellikler

### 🎯 Temel Özellikler

- **Çoklu Marketplace Desteği**: Amazon.com, .de, .co.uk, .fr, .it, .es, .ca, .co.jp
- **Akıllı Yorum Filtreleme**:
  - ⭐ Negatif yorumlar (≤4 yıldız) - müşteri şikayetlerini analiz et
  - ⭐⭐⭐⭐⭐ Pozitif yorumlar (≥4 yıldız) - güçlü yanları keşfet
  - Tüm yorumlar - kapsamlı analiz
- **Sentiment Analizi**: VADER ile otomatik duygu analizi
- **Rakip Karşılaştırma**: 10'a kadar ürünü karşılaştır
- **İleri Filtreleme**: Rating, tarih, doğrulanmış alım, yardımcı oylar
- **Gerçek Zamanlı Dashboard**: Görsel istatistikler ve grafikler

### 🛡️ Uyumluluk Özellikleri

- ✅ **Manuel HTML Upload** (Önerilen): %100 uyumlu, sıfır risk
- ✅ **Kontrollü Scraping**: Kullanıcı denetiminde, rate-limited
- ✅ **Şeffaf Operasyon**: Non-headless browser, açık çalışma
- ✅ **Saygılı Rate Limiting**: 2-5 saniye gecikmeler, max 10 sayfa/ürün
- ❌ **NO CAPTCHA Bypass**: Hiçbir anti-bot teknolojisi kullanmaz
- ❌ **NO Aggressive Scraping**: Etik sınırlar içinde

---

## 🏗️ Mimari

```
┌─────────────────┐
│   React UI      │  Frontend (Vite + TypeScript + Tailwind)
│   (Port 3000)   │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI        │  Backend API (Python 3.11)
│  (Port 8000)    │
└────┬──────┬─────┘
     │      │
     │      └───────▶ ┌──────────────┐
     │                │ Celery Worker│  Async Scraping
     │                └──────────────┘
     ▼                        │
┌──────────┐                 │
│PostgreSQL│◀────────────────┘
│ (5432)   │
└──────────┘
     ▲
     │
┌────┴─────┐
│  Redis   │  Task Queue & Cache
│  (6379)  │
└──────────┘
```

### Veri Akışı

1. **Manuel Upload (Önerilen)**:
   ```
   User → Browser → Save HTML → Upload → Parser → DB
   ```

2. **Kontrollü Scraping**:
   ```
   User → API → Celery Task → Playwright → Parser → Sentiment → DB
   ```

---

## 🚀 Kurulum

### Gereksinimler

- Docker & Docker Compose
- 4GB+ RAM
- 10GB+ Disk space

### Hızlı Başlangıç

```bash
# 1. Repo'yu klonla
git clone https://github.com/yourusername/aydn.git
cd aydn

# 2. Environment dosyasını kopyala
cp .env.example .env

# 3. Docker ile başlat
docker-compose up -d

# 4. Database migration (ilk kurulum)
docker-compose exec backend alembic upgrade head

# 5. Uygulamayı aç
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Geliştirme Ortamı

```bash
# Backend (Python)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload

# Frontend (Node.js)
cd frontend
npm install
npm run dev
```

---

## 📖 Kullanım

### 1️⃣ Manuel HTML Upload (ÖNERİLEN)

**En güvenli ve uyumlu yöntem:**

```
1. Amazon'da ürün yorumlarına git
   Örnek: https://amazon.com/product-reviews/B08N5WRWNW

2. Sayfayı HTML olarak kaydet
   • Chrome/Edge: Ctrl+S (Cmd+S Mac'te)
   • "Tam Web Sayfası" seç

3. AYDN'de Upload butonuna tıkla
   • ASIN gir
   • Marketplace seç
   • HTML dosyasını yükle

4. ✅ Yorumlar anında parse edilir!
```

### 2️⃣ Kontrollü Scraping

**Dikkatli kullanım için:**

```
1. "Controlled Scraping" moduna geç

2. Ürün URL'lerini gir (max 10):
   https://amazon.com/dp/B08N5WRWNW
   https://amazon.de/dp/B07XQK7H3P

3. Ayarları seç:
   • Marketplace
   • Rating Filter (negative/positive/all)

4. "Start Scraping" tıkla

5. İş durumunu izle (Job Status)

⚠️ Not:
- Browser açılır (non-headless)
- 2-5 sn gecikmeler
- Max 10 sayfa/ürün
- CAPTCHA çıkarsa durdur!
```

### 3️⃣ Dashboard & Analiz

```
1. ASIN seç (dropdown)

2. Dashboard gösterir:
   📊 Total Reviews
   ⭐ Average Rating
   ✓ Verified %
   📉 Negatif Yorum Sayısı

3. Grafikler:
   • Rating Distribution (Bar Chart)
   • Sentiment Distribution (Pie Chart)

4. Review List:
   • Filtrele: Negative/Positive
   • Sırala: Latest/Rating/Helpful
   • Paginate: 20 per page
```

### 4️⃣ Rakip Karşılaştırma

```bash
# API üzerinden
curl "http://localhost:8000/api/v1/reviews/compare?asins=B08N5WRWNW,B07XQK7H3P&marketplace=us"

# Response:
{
  "marketplace": "us",
  "products": [
    {
      "asin": "B08N5WRWNW",
      "title": "Product A",
      "stats": {
        "total_reviews": 1250,
        "average_rating": 4.2,
        "negative_count": 180,
        "negative_percentage": 14.4
      },
      "sample_negative_reviews": [...]
    },
    ...
  ]
}
```

---

## 🔌 API Dokümantasyonu

### Swagger UI

Detaylı API dokümantasyonu: http://localhost:8000/docs

### Temel Endpoints

- `POST /api/v1/ingest/` - Scrape job oluştur
- `GET /api/v1/ingest/status/{job_id}` - Job durumu
- `POST /api/v1/upload/html` - HTML yükle
- `POST /api/v1/upload/csv` - CSV yükle
- `GET /api/v1/reviews/` - Yorumları listele
- `GET /api/v1/reviews/stats` - İstatistikler
- `GET /api/v1/reviews/compare` - Ürün karşılaştır

---

## 🛡️ Uyumluluk ve Etik

### ✅ YAPILMASI GEREKENLER

1. **Manuel Upload Kullan**: En güvenli ve uyumlu yöntem
2. **Rate Limit'e Uy**: Sistemdeki default ayarları değiştirme
3. **Non-headless Kullan**: Scraping şeffaf olmalı
4. **CAPTCHA'ya Saygı Göster**: Çıkarsa işlemi durdur
5. **Research Amaçlı Kullan**: Kişisel analiz, rakip araştırma

### ❌ YAPILMAMASI GEREKENLER

1. **Aggressive Scraping**: Rate limit aşma, hızlı istekler
2. **CAPTCHA Bypass**: Anti-bot teknolojileri kullanma
3. **Commercial Resale**: Veriyi ticari olarak satma
4. **Automation Abuse**: 7/24 otomatik scraping
5. **ToS İhlali**: Amazon kullanım şartlarını ihlal etme

---

## 🛠️ Teknoloji Stack

### Backend
- FastAPI, SQLAlchemy, PostgreSQL, Celery, Redis
- Playwright, BeautifulSoup, VADER Sentiment

### Frontend
- React 18, TypeScript, Vite, Tailwind CSS, Recharts

### DevOps
- Docker, Docker Compose, Nginx

---

## 📝 Lisans

MIT License

---

**AYDN - Etik Amazon Yorum Analizi** 🚀
