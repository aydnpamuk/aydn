# 🌐 Antigravity ile Çalıştırma

## 🎯 3 Kolay Yöntem

### ✅ Yöntem 1: Lokal Streamlit (ÖNERİLEN)

En basit ve hızlı yöntem:

```bash
# Tek komut ile başlat
./start_web.sh

# Veya manuel:
streamlit run src/web/app.py
```

**Sonuç:** Tarayıcınızda `http://localhost:8501` açılacak

---

### ☁️ Yöntem 2: Streamlit Cloud (Antigravity)

Ücretsiz cloud deployment:

1. **https://streamlit.io/cloud** adresine git
2. "New app" butonuna tıkla
3. GitHub hesabını bağla
4. Şu bilgileri gir:
   ```
   Repository: aydnpamuk/aydn
   Branch: claude/amazon-ppc-seo-system-kVtQH
   Main file: src/web/app.py
   ```
5. "Deploy" tıkla!

**Sonuç:** Birkaç dakika içinde public URL alacaksınız
- Örnek: `https://amazon-ppc-system.streamlit.app`
- Herkesle paylaşabilirsiniz
- HTTPS otomatik
- Ücretsiz!

---

### 🔬 Yöntem 3: Google Colab (Antigravity)

Jupyter Notebook tarzı kullanım:

1. **https://colab.research.google.com** aç
2. Yeni notebook oluştur
3. Bu kodu çalıştır:

```python
# 1. Repository'yi clone et
!git clone https://github.com/aydnpamuk/aydn.git
%cd aydn
!git checkout claude/amazon-ppc-seo-system-kVtQH

# 2. Bağımlılıkları kur
!pip install -q streamlit plotly typer pydantic pandas numpy rich python-dateutil pyngrok

# 3. Dashboard başlat
from pyngrok import ngrok
import subprocess
import time

# Streamlit başlat
subprocess.Popen(['streamlit', 'run', 'src/web/app.py', '--server.port', '8501'])
time.sleep(5)

# Public URL oluştur
public_url = ngrok.connect(8501)
print(f"🌐 Dashboard URL: {public_url}")
```

**Sonuç:** Public URL alacaksınız, tarayıcıda açın!

---

## 🎨 Dashboard Özellikleri

Streamlit dashboard 5 sayfa içerir:

### 1. 📈 Kampanya Analizi
- Form doldur → Metrik hesapla
- ACoS, TACOS, CTR, CVR anlık
- Benchmark karşılaştırma
- Performance summary

### 2. 💰 Bid Optimizasyonu
- RPC formülü otomatik hesaplama
- Mevcut vs Önerilen bid
- Değişim yüzdesi
- Güven seviyesi

### 3. 🚨 Stok Kontrolü
- Stok durumu (4 seviye)
- Kalan gün hesaplama
- Otomatik aksiyon planı
- PPC bütçe önerileri

### 4. ⚖️ Golden Rules Check
- 5 altın kural kontrolü
- İhlal raporları
- Ciddiyet seviyeleri
- Aksiyon önerileri

### 5. 📚 Benchmark Karşılaştırma
- Sektör standartları
- Performance indicator
- Visual progress bars

---

## 🚀 Hızlı Başlangıç

### İlk Kez Kullanım

```bash
# 1. Bağımlılıkları kur
pip install streamlit plotly

# 2. Dashboard'u başlat
./start_web.sh

# 3. Tarayıcıda aç
# http://localhost:8501
```

### Colab'da Hızlı Test

```python
# Sadece Python API kullanımı
!git clone https://github.com/aydnpamuk/aydn.git && cd aydn
!pip install -q typer pydantic pandas numpy rich

import sys
sys.path.insert(0, '/content/aydn')

from src.core.metrics.calculator import MetricsCalculator

result = MetricsCalculator.calculate(
    ad_spend=500,
    ad_sales=2000,
    total_sales=5000
)

print(f"ACoS: {result.acos}%")
print(f"TACOS: {result.tacos}%")
```

---

## 📱 Mobile Support

Dashboard mobile-friendly:
- ✅ Responsive design
- ✅ Touch controls
- ✅ Tablet optimize
- ✅ Phone'da da çalışır

---

## 🎯 Use Cases

### Günlük Kullanım
- Sabah: Golden Rules check
- Gün içi: Kampanya performans
- Akşam: Bid optimizasyon

### Haftalık Review
- Wasted spend analizi
- ACoS trend
- Stok durumu
- Benchmark karşılaştırma

### Acil Durumlar
- Stok krizi protokolü
- ACoS ani artış
- Golden rule violations

---

## 🔧 Troubleshooting

### Problem: "Streamlit bulunamadı"
```bash
pip install streamlit plotly
```

### Problem: "Port 8501 meşgul"
```bash
streamlit run src/web/app.py --server.port 8502
```

### Problem: "Modül import hatası"
```bash
# PYTHONPATH ayarla
export PYTHONPATH=/path/to/aydn:$PYTHONPATH
streamlit run src/web/app.py
```

### Problem: Colab'da ngrok hatası
```python
# Ngrok token gerekebilir (ücretsiz)
!ngrok authtoken YOUR_TOKEN
```

---

## 💡 Pro Tips

### Tip 1: Cache Kullanımı
Streamlit otomatik cache yapar → Hızlı reload

### Tip 2: Veri Kaydet
Dashboard'da sonuçları CSV export edebilirsiniz

### Tip 3: Tema Değiştir
`.streamlit/config.toml` dosyası ile:
```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
```

### Tip 4: Production Deploy
Streamlit Cloud ücretsiz ama production için:
- Heroku
- Railway
- AWS/GCP
- Docker

---

## 📊 Örnek Kullanım

### Senaryo 1: Kampanya Hızlı Analiz

1. Dashboard aç → "Kampanya Analizi"
2. Verileri gir:
   - Ad Spend: $1,250
   - Ad Sales: $3,500
   - Total Sales: $8,000
   - Clicks: 180
   - Orders: 21
3. "Analiz Et" tıkla
4. Sonuç: ACoS %35.7 (Hedefin üstünde)
5. Bid Optimizasyon sayfasına geç
6. Öneri: Bid'i $7.50'den $4.86'ya düşür
7. Beklenen ACoS: %21 ✅

---

## 🎓 Video Tutorial

Yakında video eklenecek:
- Dashboard tour
- Örnek senaryolar
- Pro tips
- Troubleshooting

---

## 🆘 Destek

- **Dokümantasyon:** README.md, USAGE.md
- **Örnekler:** examples/ klasörü
- **Demo:** Tüm senaryolar examples/ içinde

---

**🎉 Hazırsınız!**

3 yöntemden birini seçin ve kullanmaya başlayın!

---

**Sistem:** Amazon PPC & SEO Management System v1.0.0
**Temel:** Amazon PPC & SEO Bible v3.0 (9.5/10)
**Last Updated:** 2024-12-23
