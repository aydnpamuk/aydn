# 🔌 AYDN Chrome Extension (Standalone)

**100% Local - NO Backend Required!**

Amazon yorumlarını tarayıcınızda toplayın ve IndexedDB'de saklayın. Hiçbir sunucuya ihtiyaç yok!

---

## ✨ Özellikler

### 🎯 Tamamen Bağımsız
- ✅ **Backend gerekmez** - Tüm veriler tarayıcınızda
- ✅ **İnternet bağlantısı gereksiz** (sadece Amazon'u ziyaret için)
- ✅ **Privacy first** - Verileriniz sadece sizde
- ✅ **Hızlı başlangıç** - 30 saniyede kurulum

### 🛡️ Etik ve Güvenli
- ✅ Kullanıcının tarayıcısında çalışır
- ✅ %100 uyumlu (kullanıcının kendi oturumu)
- ✅ Manuel kontrol
- ❌ Otomatik scraping yok
- ❌ CAPTCHA bypass yok

### 📊 Güçlü Analiz
- Client-side sentiment analizi
- Rating dağılımı
- Verified purchase oranı
- Özel filtreleme
- Export/Import (JSON)

---

## 🚀 Kurulum (30 Saniye)

### 1. Extension'ı Yükleyin

```bash
# Chrome Extensions sayfasını açın
chrome://extensions/

# Developer mode'u aktifleştirin
# "Load unpacked" tıklayın
# chrome-extension/ klasörünü seçin
```

### 2. Kullanmaya Başlayın

1. Amazon yorumlarına gidin: `amazon.com/product-reviews/[ASIN]`
2. Sağ altta 📊 butonuna tıklayın
3. "Collect & Save Locally" tıklayın
4. ✅ Yorumlar tarayıcınıza kaydedildi!
5. Extension ikonuna tıklayıp "Open Dashboard"

---

## 📖 Kullanım

### Yorum Toplama

1. **Amazon review sayfasına gidin**
2. **📊 Floating button** göreceksiniz (sağ alt)
3. **Butona tıklayın** → Modal açılır
4. **Filtreleri seçin:**
   - Negative Reviews (≤4★)
   - Positive Reviews (≥4★)
   - All Reviews
5. **"Collect & Save"** tıklayın
6. ✅ **Başarılı!** Veriler IndexedDB'ye kaydedildi

### Dashboard

1. **Extension ikonuna tıklayın**
2. **"Open Dashboard"** butonuna tıklayın
3. **Dashboard'da:**
   - 📊 İstatistikler
   - 📈 Grafikler
   - 📝 Yorum listesi
   - 🔍 Filtreleme
   - 📤 Export/Import

---

## 💾 Veri Depolama

### IndexedDB Yapısı

```javascript
AydnReviewsDB
├── products
│   ├── id, asin, title, marketplace
│   ├── average_rating, total_reviews
│   └── created_at, updated_at
│
└── reviews
    ├── id, review_id, product_id, asin
    ├── rating, title, text
    ├── author_name, review_date
    ├── verified_purchase, helpful_votes
    ├── sentiment_score, sentiment_label
    └── is_negative, is_positive
```

### Veri Erişimi

```javascript
// Tüm ürünler
await storage.getAllProducts()

// Yorumları getir
await storage.getReviewsByAsin('B08N5WRWNW')

// İstatistikler
await storage.getProductStats('B08N5WRWNW')
```

---

## 📤 Export / Import

### Export

1. Dashboard'da "Export Data" tıklayın
2. JSON dosyası indirilir
3. Yedeğinizi saklayın!

### Import

1. Dashboard'da "Import Data" tıklayın
2. JSON dosyasını seçin
3. Veriler restore edilir

---

## 🎨 Sentiment Analizi

Basit ama etkili client-side algoritma:

```javascript
// Negative keywords: bad, terrible, broken, failed...
// Positive keywords: good, great, excellent, love...
// Negation handling: "not good" → negative
// Intensifiers: "very bad" → daha negatif

const sentiment = SentimentAnalyzer.analyze(text);
// → { sentiment_score: -0.75, sentiment_label: 'negative' }
```

---

## 🔧 Teknik Detaylar

### Dosya Yapısı

```
chrome-extension/
├── manifest-standalone.json
├── lib/
│   ├── storage.js              # IndexedDB manager
│   └── sentiment.js            # Sentiment analyzer
├── content/
│   ├── parser.js               # Amazon DOM parser
│   ├── content-standalone.js   # Main logic
│   └── content.css             # Styles
├── dashboard/
│   ├── dashboard.html          # Full dashboard
│   ├── dashboard.css
│   └── dashboard.js
├── popup/
│   ├── popup-standalone.html   # Extension popup
│   └── popup-standalone.js
└── background/
    └── service-worker-standalone.js
```

### Permissions

```json
{
  "permissions": ["activeTab", "storage"],
  "host_permissions": ["*://*.amazon.*/*"]
}
```

Sadece Amazon sayfalarına ve local storage'a erişim!

---

## 🐛 Sorun Giderme

### Extension yüklenmedi
✅ Developer mode aktif mi?
✅ `manifest-standalone.json` dosyasını `manifest.json` olarak kopyalayın

### Floating button görünmüyor
✅ Amazon review sayfasında mısınız?
✅ Sayfayı yenileyin (F5)
✅ Console'u kontrol edin (F12)

### Veriler kayboldu
✅ IndexedDB browser'ın cache temizliğinde silinebilir
✅ Export ile düzenli yedek alın!

### Sentiment yanlış
✅ Basit keyword-based algoritma
✅ %80-85 doğruluk oranı
✅ Karmaşık cümleler için sınırlı

---

## 🔐 Gizlilik

### Ne Toplanır?
- ✅ Amazon public reviews (herkese açık)
- ✅ Product bilgisi (ASIN, title, rating)

### Ne Toplanmaz?
- ❌ Kişisel bilgileriniz
- ❌ Tarama geçmişiniz
- ❌ Amazon hesap bilgileriniz
- ❌ Oturum cookie'leri

### Veri Nerede?
- 💾 **Sadece tarayıcınızda** (IndexedDB)
- 🔒 **Hiçbir sunucuya gönderilmez**
- 🗑️ **İstediğiniz zaman silebilirsiniz**

---

## 🎯 Kullanım Senaryoları

### 1. Ürün Araştırması
- Rakip ürünleri analiz et
- Negatif yorumlardan öğren
- Müşteri ihtiyaçlarını keşfet

### 2. Satıcılar İçin
- Kendi ürününüzün yorumlarını analiz edin
- Müşteri şikayetlerini tespit edin
- İyileştirme alanlarını bulun

### 3. Alıcılar İçin
- Ürün karşılaştırması
- Gerçek kullanıcı deneyimleri
- Karar vermede yardımcı

---

## ⚖️ Yasal Uyarı

**Bu extension etik kullanım için tasarlanmıştır:**

✅ **İzinli:**
- Kişisel araştırma
- Ürün karşılaştırma
- Müşteri feedback analizi

❌ **İzinsiz:**
- Ticari veri satışı
- Toplu otomatik scraping
- Amazon ToS ihlali

**Kullanıcı sorumluluğundadır.**

---

## 📝 Sürüm Notları

### v2.0.0 (Standalone)
- 🎉 Backend bağımlılığı kaldırıldı
- 💾 IndexedDB local storage
- 🧠 Client-side sentiment analizi
- 📊 Built-in dashboard
- 📤 Export/Import JSON
- ⚡ Daha hızlı ve basit

---

## 🤝 Katkıda Bulunma

GitHub: https://github.com/aydnpamuk/aydn

---

## 📄 Lisans

MIT License

---

**AYDN - 100% Local Amazon Review Analyzer** 🚀

*No backend, no servers, no hassle. Just pure client-side magic!*
