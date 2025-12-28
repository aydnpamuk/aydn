# 🤖 JARVIS - Sesli + Ekran AI Asistan

> **Kullanıcının ekranını görebilen ve sesli konuşabilen gelişmiş AI asistan sistemi.**

JARVIS, uzman system prompt kütüphanesi ile farklı uzmanlık modlarında çalışabilen, ekran görüntüsü analizi yapabilen ve sesli iletişim kurabilen bir yapay zeka asistanıdır.

## ✨ Özellikler

### 🎯 Uzman Prompt Kütüphanesi
- **Çoklu Uzman Modlar**: Farklı uzmanlık alanları için prompt'lar kaydedin
- **CRUD İşlemleri**: Prompt ekleme, güncelleme, silme, listeleme
- **Aktif Prompt Sistemi**: İstediğiniz an farklı uzmanlık moduna geçin
- **Genel Mod**: Uzman prompt olmadan genel amaçlı asistan

### 📸 Ekran Görüntüsü Analizi
- **Gerçek Zamanlı Yakalama**: Ekranınızı anlık olarak yakalar
- **Vision AI**: Claude/GPT-4 Vision ile ekran analizi
- **Bölge Seçimi**: Sadece belirli bir alanı yakalayın
- **Otomatik Kayıt**: Tüm ekran görüntüleri kaydedilir

### 🎤 Sesli Arayüz
- **Text-to-Speech (TTS)**: AI cevapları sesli olarak duyun (Türkçe destekli)
- **Speech-to-Text (STT)**: Sesli komutlarla JARVIS'i kontrol edin
- **Sürekli Dinleme Modu**: Kesintisiz sesli etkileşim
- **Çoklu Dil**: Türkçe, İngilizce ve karma mod

### 🧠 AI Entegrasyonu
- **Claude & OpenAI**: Anthropic Claude ve OpenAI GPT desteği
- **Vision Desteği**: Ekran görüntüleriyle konuşun
- **Konuşma Geçmişi**: Bağlamsal diyaloglar
- **Özelleştirilebilir**: Farklı modeller ve API'lar

## 📦 Kurulum

### 1. Depoyu Klonlayın

```bash
git clone <repo-url>
cd aydn
```

### 2. Virtual Environment Oluşturun

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### 4. Sistem Bağımlılıkları (Opsiyonel - Ses için)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install mpg123 portaudio19-dev python3-pyaudio
```

**macOS:**
```bash
brew install mpg123 portaudio
```

**Windows:**
- Ses çıkışı otomatik çalışır
- Mikrofon için PyAudio kurulumu gerekebilir

### 5. API Key Ayarlayın

`.env.example` dosyasını `.env` olarak kopyalayın:

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyip API key'inizi ekleyin:

```bash
# Anthropic Claude (önerilen)
ANTHROPIC_API_KEY=sk-ant-xxxxx

# veya OpenAI
OPENAI_API_KEY=sk-xxxxx
```

### 6. Paketi Yükleyin (Opsiyonel)

```bash
pip install -e .
```

Bu adımdan sonra `jarvis` komutunu doğrudan kullanabilirsiniz.

## 🚀 Kullanım

### Hızlı Başlangıç

#### İnteraktif Metin Modu

```bash
python -m src.jarvis_cli chat
```

Veya eğer paketi yüklediyseniz:

```bash
jarvis chat
```

#### Sesli Mod

```bash
jarvis voice
```

#### Tek Mesaj Gönder

```bash
jarvis chat -m "Merhaba JARVIS, bu ekran görüntüsünü analiz eder misin?" -s
```

- `-m`: Mesaj metni
- `-s`: Ekran görüntüsü ile sor
- `--no-voice`: Sesli cevap verme

### 📚 Prompt Kütüphanesi Yönetimi

#### Prompt Listele

```bash
jarvis prompt list
```

#### Yeni Prompt Ekle

```bash
jarvis prompt add "Amazon Gatekeeper" \
  --text "Sen Amazon PPC uzmanısın. Kullanıcılara kampanya optimizasyonu konusunda yardım et." \
  --description "Amazon reklamları için uzman asistan" \
  --tags "amazon,ppc,ads" \
  --language tr
```

Veya dosyadan:

```bash
jarvis prompt add "Python Expert" --file prompts/python_expert.txt
```

#### Prompt Detaylarını Göster

```bash
jarvis prompt show "Amazon Gatekeeper"
```

#### Prompt Güncelle

```bash
jarvis prompt update "Amazon Gatekeeper" \
  --description "Güncellenmiş açıklama" \
  --tags "amazon,ppc,optimization"
```

#### Prompt Aktif Et

```bash
jarvis prompt activate "Amazon Gatekeeper"
```

Artık JARVIS bu uzmanlık modunda çalışacak!

#### Genel Moda Dön

```bash
jarvis prompt activate none
```

#### Prompt Sil

```bash
jarvis prompt delete "Prompt Adı"
```

## 🎭 Kullanım Senaryoları

### Senaryo 1: Amazon PPC Optimizasyonu

```bash
# 1. Uzman prompt'u ekle
jarvis prompt add "Amazon PPC Expert" \
  --file prompts/amazon_ppc.txt \
  --tags "amazon,ppc"

# 2. Aktif et
jarvis prompt activate "Amazon PPC Expert"

# 3. Ekranınızda Seller Central'ı açın
# 4. JARVIS'e sorun
jarvis chat -m "Bu kampanyamın performansını değerlendirir misin?" -s
```

### Senaryo 2: Kod Review

```bash
# 1. Python Expert prompt'u ekle
jarvis prompt add "Code Reviewer" \
  --text "Sen deneyimli bir Python geliştiricisisin. Kod inceleme ve optimizasyon önerileri sun." \
  --tags "python,code-review"

# 2. Aktif et
jarvis prompt activate "Code Reviewer"

# 3. IDE'nizde kodu açın
# 4. Sesli mod ile sor
jarvis voice
# "Bu kodda potansiyel sorunlar neler?"
```

### Senaryo 3: Genel Asistan

```bash
# Genel mod
jarvis prompt activate none

# İnteraktif mod
jarvis chat

> Sen: Excel dosyamı açtım, veri analizi yapmam lazım
> JARVIS: Ekranınızı görebilir miyim? (ekran komutu yazın)
> Sen: ekran
> JARVIS: [Ekranı analiz eder ve adım adım rehberlik eder]
```

## 📂 Proje Yapısı

```
aydn/
├── src/
│   ├── jarvis/
│   │   ├── __init__.py
│   │   ├── models.py              # Pydantic veri modelleri
│   │   ├── config.py              # Konfigürasyon yönetimi
│   │   ├── prompt_library.py     # Prompt CRUD işlemleri
│   │   ├── screen_capture.py     # Ekran yakalama
│   │   ├── voice.py               # TTS + STT
│   │   ├── ai_engine.py           # Claude/OpenAI entegrasyonu
│   │   └── jarvis.py              # Ana orchestrator
│   └── jarvis_cli.py              # CLI arayüzü
├── tests/
│   ├── test_models.py
│   ├── test_config.py
│   └── test_prompt_library.py
├── data/                          # Oluşturulacak (git ignore)
│   ├── prompt_library.json       # Kayıtlı prompt'lar
│   └── screenshots/              # Ekran görüntüleri
├── .env                          # API keys (git ignore)
├── .env.example                  # Örnek config
├── requirements.txt              # Bağımlılıklar
├── requirements-dev.txt          # Dev bağımlılıkları
├── pyproject.toml
└── README.md
```

## 🧪 Testler

```bash
# Tüm testleri çalıştır
make test

# veya
pytest

# Coverage ile
pytest --cov=src/jarvis
```

## 🔧 Geliştirme

### Kod Formatla

```bash
make fmt
```

### Lint Çalıştır

```bash
make lint
```

### Tüm Kontroller

```bash
make lint test
```

## ⚙️ Konfigürasyon

Tüm ayarlar `.env` dosyasından yönetilir:

```bash
# AI Provider (anthropic veya openai)
JARVIS_AI_PROVIDER=anthropic

# API Keys
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx

# Model
JARVIS_MODEL_NAME=claude-3-5-sonnet-20241022

# Ses Ayarları
JARVIS_VOICE_ENABLED=true
JARVIS_VOICE_LANGUAGE=tr
JARVIS_VOICE_SPEED=1.0

# Ekran
JARVIS_SCREEN_ENABLED=true

# Dosya Yolları
JARVIS_LIBRARY_PATH=data/prompt_library.json
JARVIS_SCREENSHOTS_PATH=data/screenshots

# Debug
JARVIS_DEBUG=false
```

## 🎨 Örnek Prompt Şablonları

### Amazon PPC Expert

```text
Sen uzman bir Amazon PPC yöneticisisin.

GÖREVIN:
- Kampanya performansını analiz et
- ACOS, ROAS, CTR metriklerini değerlendir
- Bütçe ve teklif optimizasyon önerileri sun
- Hedefleme stratejileri geliştir

YÖNERGELERİN:
1. Ekrandaki veriyi dikkatlice incele
2. Net metrik bazlı öneriler sun
3. Aksiyon adımlarını sırala
4. ROI odaklı düşün
```

### Python Code Reviewer

```text
Sen deneyimli bir Python geliştiricisisin.

GÖREVIN:
- Kod kalitesini değerlendir
- Best practice'lere uygunluğu kontrol et
- Performans iyileştirmeleri öner
- Güvenlik açıklarını tespit et

YÖNERGELERİN:
1. PEP 8 standartlarını kontrol et
2. Type hints kullanımını değerlendir
3. Potansiyel bug'ları işaretle
4. Refactoring önerileri sun
```

## 🐛 Sorun Giderme

### Ses Çalışmıyor

**Linux:**
```bash
# mpg123 veya ffplay yükleyin
sudo apt-get install mpg123 ffmpeg
```

**Mikrofon Erişimi:**
- Sisteminizin mikrofon iznini kontrol edin
- PyAudio kurulumunu doğrulayın

### API Hataları

- `.env` dosyasında API key'in doğru olduğundan emin olun
- API kredinizi kontrol edin
- Model adının doğru olduğunu kontrol edin

### Ekran Yakalama Çalışmıyor

- Linux'ta X11 veya Wayland desteğini kontrol edin
- macOS'ta ekran kayıt iznini verin
- Windows'ta yönetici izni gerekebilir

## 📝 Lisans

Bu proje eğitim amaçlıdır.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📧 İletişim

Sorularınız için issue açabilirsiniz.

---

**JARVIS ile üretkenliğinizi artırın!** 🚀
