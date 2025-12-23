# 🌐 Web Dashboard Kullanım Kılavuzu

## 🚀 3 Farklı Çalıştırma Yöntemi

### Yöntem 1: Lokal Streamlit (En Kolay) ✅

```bash
# Bağımlılıkları kur
pip install streamlit plotly

# Streamlit dashboard'u başlat
streamlit run src/web/app.py
```

Tarayıcınız otomatik açılacak: `http://localhost:8501`

---

### Yöntem 2: Antigravity (Cloud-based)

#### A. Streamlit Cloud ile

1. **Repository'yi GitHub'a push et** (✓ Zaten yapıldı)

2. **Streamlit Cloud'a git:**
   - https://streamlit.io/cloud
   - "New app" tıkla
   - Repository: `aydnpamuk/aydn`
   - Branch: `claude/amazon-ppc-seo-system-kVtQH`
   - Main file: `src/web/app.py`

3. **Deploy et!**
   - Dakikalar içinde canlı olacak
   - URL: `https://your-app.streamlit.app`

#### B. Google Colab ile

```python
# Colab notebook'ta çalıştır:

# 1. Clone repository
!git clone https://github.com/aydnpamuk/aydn.git
%cd aydn
!git checkout claude/amazon-ppc-seo-system-kVtQH

# 2. Install dependencies
!pip install -q streamlit plotly typer pydantic pandas numpy rich python-dateutil

# 3. Run with ngrok
!pip install -q pyngrok
from pyngrok import ngrok

# Start streamlit in background
!streamlit run src/web/app.py &

# Create public URL
public_url = ngrok.connect(8501)
print(f"Public URL: {public_url}")
```

#### C. Jupyter Notebook ile

İnteraktif notebook oluşturalım:

```bash
# Jupyter çalıştır
jupyter notebook examples/interactive_dashboard.ipynb
```

---

### Yöntem 3: FastAPI + REST API

API server ile çalıştırma:

```bash
# FastAPI backend başlat
uvicorn src.api.main:app --reload

# API dokümantasyonu
http://localhost:8000/docs
```

---

## 📦 Kurulum

### Hızlı Kurulum
```bash
# Tüm web bağımlılıkları
pip install -r requirements.txt

# Sadece streamlit
pip install streamlit plotly
```

### Development Kurulum
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

---

## 🎨 Dashboard Özellikleri

### 1. 📈 Kampanya Analizi
- Metrik hesaplama (ACoS, TACOS, CTR, CVR)
- Gerçek zamanlı benchmark karşılaştırma
- Organik:PPC ratio analizi

### 2. 💰 Bid Optimizasyonu
- RPC formülü hesaplama
- Otomatik bid önerileri
- Değişim yüzdesi analizi

### 3. 🚨 Stok Kontrolü
- 4 seviye stok durumu
- Otomatik aksiyon planları
- Reorder point hesaplama
- PPC bütçe önerileri

### 4. ⚖️ Golden Rules Check
- 5 altın kural kontrolü
- Compliance scoring
- Detaylı ihlal raporları

### 5. 📚 Benchmark Karşılaştırma
- Sektör standartları ile karşılaştırma
- Performance level indicator
- Visual progress bars

---

## 🔗 Deployment Seçenekleri

### Streamlit Cloud (Ücretsiz)
✅ En kolay
✅ Otomatik HTTPS
✅ Git entegrasyonu
✅ Ücretsiz tier yeterli

**Setup:**
1. streamlit.io/cloud'a git
2. GitHub hesabını bağla
3. Repository seç → Deploy

### Heroku
```bash
# Procfile oluştur
echo "web: streamlit run src/web/app.py --server.port=$PORT" > Procfile

# Deploy
heroku create amazon-ppc-system
git push heroku main
```

### Railway
```bash
# Railway CLI
railway login
railway init
railway up
```

### Docker
```bash
# Build
docker build -t amazon-ppc-system .

# Run
docker run -p 8501:8501 amazon-ppc-system
```

---

## 💡 Kullanım Örnekleri

### Örnek 1: Kampanya Analizi
1. Sol menüden "📈 Kampanya Analizi" seç
2. Finansal verileri gir (ad spend, sales)
3. Trafik verilerini gir (impressions, clicks)
4. "Analiz Et" butonuna bas
5. Sonuçları gör!

### Örnek 2: Bid Optimizasyonu
1. "💰 Bid Optimizasyonu" seç
2. Mevcut bid ve performans gir
3. Hedef ACoS belirle
4. "Öneri Al" - RPC formülü ile otomatik hesaplama

### Örnek 3: Stok Krizi
1. "🚨 Stok Kontrolü" seç
2. Mevcut stok ve satış hızı gir
3. "Analiz Et"
4. Durum seviyesi + aksiyon planı al

---

## 🎯 Pro Tips

### Performance
- İlk yüklemede biraz yavaş olabilir (Streamlit startup)
- Sonraki kullanımlar çok hızlı (cache)
- Büyük veri setleri için pandas optimize edilmiş

### Security
- Hassas verileri .env dosyasında sakla
- API keys için Streamlit secrets kullan
- Production'da SSL zorunlu

### Customization
```python
# src/web/app.py dosyasında özelleştir:
st.set_page_config(
    page_title="Your Company - PPC Dashboard",
    page_icon="🚀",
    layout="wide"
)
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit plotly
```

### "Port 8501 already in use"
```bash
streamlit run src/web/app.py --server.port 8502
```

### Dashboard yüklenmiyor
```bash
# Cache temizle
streamlit cache clear

# Yeniden başlat
streamlit run src/web/app.py
```

---

## 📱 Mobile Support

Dashboard mobile-responsive:
- ✅ Tablet görünümü optimize
- ✅ Phone'da da kullanılabilir
- ✅ Touch-friendly controls

---

## 🎬 Video Tutorial

```bash
# Demo video oluştur
streamlit run src/web/app.py --server.headless true
# Screen record yap
```

---

## 📊 Analytics

Kullanım istatistikleri ekle:
```python
# Google Analytics integration
st.components.v1.html("""
    <!-- GA code -->
""")
```

---

**Hazırladı:** Amazon PPC System v1.0.0
**Last Updated:** 2024-12-23
