# 🔌 AYDN Chrome Extension

**Etik Amazon Yorum Toplayıcı - Chrome Eklentisi**

Amazon ürün yorumlarını tarayıcınızdan direkt toplayın ve AYDN backend'ine gönderin.

---

## ✨ Özellikler

### 🎯 Kullanıcı Dostu
- ✅ Tek tıkla yorum toplama
- ✅ Amazon sayfasında floating action button
- ✅ Gerçek zamanlı ilerleme göstergesi
- ✅ Otomatik sentiment analizi
- ✅ Backend ile entegrasyon

### 🛡️ Etik ve Uyumlu
- ✅ **Kullanıcının tarayıcısında çalışır**
- ✅ **Kullanıcının IP ve oturum bilgilerini kullanır**
- ✅ **Kullanıcı kontrolünde toplama**
- ✅ **Saygılı rate limiting (2-3 sn delay)**
- ❌ **Otomatik scraping yok**
- ❌ **CAPTCHA bypass yok**

### 🌍 Desteklenen Marketler
- 🇺🇸 Amazon.com
- 🇩🇪 Amazon.de
- 🇬🇧 Amazon.co.uk
- 🇫🇷 Amazon.fr
- 🇮🇹 Amazon.it
- 🇪🇸 Amazon.es
- 🇨🇦 Amazon.ca
- 🇯🇵 Amazon.co.jp

---

## 📦 Kurulum

### Ön Gereksinimler
1. **AYDN Backend** çalışıyor olmalı
   ```bash
   cd backend
   python start_dev.py
   ```
   Backend şu adreste olmalı: `http://localhost:8000`

### Chrome'a Yükleme

#### Yöntem 1: Developer Mode (Önerilen)

1. **Chrome Extensions sayfasını açın:**
   ```
   chrome://extensions/
   ```

2. **Developer mode'u aktif edin:**
   - Sağ üst köşede "Developer mode" toggle'ını açın

3. **Extension'ı yükleyin:**
   - "Load unpacked" butonuna tıklayın
   - `chrome-extension` klasörünü seçin
   - ✅ AYDN eklentisi yüklendi!

4. **Extension'ı pin'leyin:**
   - Chrome toolbar'da extensions ikonuna (puzzle) tıklayın
   - AYDN'i bulun ve pin ikonuna tıklayın

#### Yöntem 2: CRX Paketi (İleride)
Yakında Chrome Web Store'da yayınlanacak!

---

## 🚀 Kullanım

### 1️⃣ Amazon Review Sayfasına Gidin

Amazon'da bir ürünün yorumlarını açın:
```
https://www.amazon.com/product-reviews/[ASIN]
```

Örnek:
```
https://www.amazon.com/product-reviews/B08N5WRWNW
```

### 2️⃣ AYDN Butonunu Tıklayın

Sayfanın sağ alt köşesinde **📊 floating button** görünecek.

### 3️⃣ Toplama Ayarlarını Yapın

Modal pencerede:
- **Collection Mode:** Current Page veya Multiple Pages
- **Rating Filter:** Negative (≤4★), Positive (≥4★), veya All
- **Max Pages:** Kaç sayfa toplanacak (max 50)

### 4️⃣ Başlatın

"🚀 Start Collection" butonuna tıklayın:
- Yorumlar parse edilecek
- Sentiment analizi yapılacak
- Backend'e gönderilecek
- ✅ Success mesajı alacaksınız!

### 5️⃣ Dashboard'da İnceleyin

"View Dashboard" butonuyla toplanan yorumları görüntüleyin:
```
http://localhost:3000
```

---

## 🎯 Nasıl Çalışır?

### Mimari

```
┌─────────────────────┐
│  Amazon Review Page │
│   (User's Browser)  │
└──────────┬──────────┘
           │
    ┌──────▼──────┐
    │   Content   │  Parse reviews from DOM
    │   Script    │  Extract product info
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │  Extension  │  Apply filters
    │   Popup     │  Show progress
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │  Background │  Send to backend API
    │   Worker    │  Store metadata
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │   Backend   │  /api/v1/reviews/bulk
    │   API       │  Save to PostgreSQL/SQLite
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │  Dashboard  │  Visualize & analyze
    │   (React)   │  Sentiment, charts, filters
    └─────────────┘
```

### Veri Akışı

1. **Parse:** Content script Amazon DOM'dan yorumları çeker
2. **Filter:** Kullanıcı ayarlarına göre filtreleme (rating, verified, vb.)
3. **Analyze:** Her yorum için sentiment analizi (VADER)
4. **Send:** Bulk endpoint'e POST request
5. **Store:** Backend veritabanına kaydet
6. **Display:** Dashboard'da göster

---

## ⚙️ Ayarlar

### Backend URL Değiştirme

1. Extension popup'ı açın (puzzle icon → AYDN)
2. "Backend URL" alanını düzenleyin
3. "💾 Save Settings" tıklayın
4. Bağlantı test edilecek

Varsayılan:
```
http://localhost:8000
```

Production:
```
https://your-domain.com/api
```

### Sık Kullanılan Ayarlar

Extension storage'da saklanır:
- Backend URL
- Son toplama istatistikleri
- Kullanıcı tercihleri

---

## 🐛 Sorun Giderme

### Extension görünmüyor
✅ **Çözüm:**
- Developer mode aktif mi kontrol edin
- Extension'ı pin'lediğinizden emin olun
- Sayfayı yenileyin (F5)

### Backend'e bağlanamıyor
✅ **Çözüm:**
- Backend çalışıyor mu kontrol edin: `http://localhost:8000/health`
- CORS ayarlarını kontrol edin
- Backend URL'yi extension ayarlarında doğrulayın

### Yorumlar parse edilmiyor
✅ **Çözüm:**
- Amazon review sayfasında olduğunuzdan emin olun
- Sayfanın tam yüklendiğini bekleyin
- Console logları kontrol edin (F12)

### CAPTCHA çıkıyor
✅ **Çözüm:**
- Bu normaldir, CAPTCHA'yı manuel çözün
- Daha yavaş toplama yapın (max pages azalt)
- Biraz bekleyip tekrar deneyin

---

## 🔐 Gizlilik ve Güvenlik

### Veri Toplama
- ❌ Kişisel bilgileriniz toplanmaz
- ❌ Oturum bilgileriniz kaydedilmez
- ✅ Sadece public yorumlar parse edilir
- ✅ Backend'e sadece yorum metinleri gönderilir

### İzinler
Extension şu izinleri kullanır:
- `activeTab`: Mevcut Amazon sayfasını okumak için
- `storage`: Ayarları saklamak için
- `scripting`: Content script inject etmek için

### Kaynak Kodu
Tamamen açık kaynak:
```
https://github.com/aydnpamuk/aydn/tree/main/chrome-extension
```

---

## 📊 API Referansı

### Bulk Import Endpoint

```http
POST /api/v1/reviews/bulk
Content-Type: application/json

{
  "product": {
    "asin": "B08N5WRWNW",
    "title": "Product Title",
    "average_rating": 4.2,
    "total_reviews": 1250,
    "marketplace": "us",
    "url": "https://amazon.com/dp/B08N5WRWNW"
  },
  "reviews": [
    {
      "review_id": "R1ABC123",
      "rating": 3,
      "title": "Disappointed",
      "text": "Product broke after...",
      "author_name": "John D.",
      "review_date": "2023-12-15",
      "verified_purchase": true,
      "helpful_votes": 5,
      "marketplace": "us",
      "asin": "B08N5WRWNW"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Imported 50 reviews",
  "saved": 45,
  "duplicates": 5,
  "errors": 0,
  "product": {
    "asin": "B08N5WRWNW",
    "title": "Product Title",
    "marketplace": "us"
  }
}
```

---

## 🔧 Geliştirme

### Yerel Geliştirme

1. **Chrome extension klasörüne gidin:**
   ```bash
   cd chrome-extension
   ```

2. **Değişiklik yapın:**
   - `content/` - Amazon sayfası scripts
   - `popup/` - Extension popup UI
   - `background/` - Service worker

3. **Extension'ı reload edin:**
   - `chrome://extensions/` sayfasını açın
   - AYDN extension'ında "Reload" tıklayın

4. **Test edin:**
   - Amazon review sayfasına gidin
   - Console'u açın (F12)
   - Extension'ı test edin

### Debug

**Content Script:**
```javascript
// Amazon sayfasında F12 > Console
console.log('AYDN Extension loaded');
```

**Background Worker:**
```javascript
// chrome://extensions/ > AYDN > Inspect views: service worker
console.log('Background worker running');
```

**Popup:**
```javascript
// Popup açıkken F12
console.log('Popup opened');
```

---

## 📝 Changelog

### v1.0.0 (2026-01-13)
- 🎉 İlk sürüm
- ✅ Tek sayfa ve çoklu sayfa toplama
- ✅ Rating filtreleme (negative/positive/all)
- ✅ Otomatik sentiment analizi
- ✅ Backend entegrasyonu
- ✅ 8 marketplace desteği
- ✅ Floating action button UI
- ✅ Progress tracking
- ✅ Settings management

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz!

1. Fork edin
2. Feature branch oluşturun
3. Commit edin
4. Push edin
5. Pull Request açın

---

## 📄 Lisans

MIT License - Detaylar için [LICENSE](../LICENSE) dosyasına bakın

---

## 🔗 Linkler

- **GitHub:** https://github.com/aydnpamuk/aydn
- **Backend API:** http://localhost:8000/docs
- **Frontend Dashboard:** http://localhost:3000
- **Issues:** https://github.com/aydnpamuk/aydn/issues

---

## ⚠️ Yasal Uyarı

Bu extension **etik ve uyumlu kullanım** için tasarlanmıştır:

✅ **İzin Verilen:**
- Kişisel araştırma ve analiz
- Rakip ürün karşılaştırma
- Müşteri feedback analizi
- Ürün geliştirme insights

❌ **İzin Verilmeyen:**
- Ticari veri satışı
- Agresif otomatik scraping
- Amazon ToS ihlali
- CAPTCHA bypass
- Rate limit aşma

**Kullanıcı Sorumluluğu:**
Bu aracı kullanarak Amazon'un kullanım şartlarına uymayı kabul edersiniz.

---

**AYDN Chrome Extension - Etik Yorum Toplama** 🚀
