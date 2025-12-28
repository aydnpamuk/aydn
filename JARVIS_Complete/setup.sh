#!/bin/bash
# JARVIS Kurulum Scripti

echo "================================"
echo "🤖 JARVIS Kurulum Başlatılıyor"
echo "================================"
echo ""

# Renk kodları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 bulunamadı!${NC}"
    echo "Lütfen Python 3.8+ yükleyin."
    exit 1
fi

echo -e "${GREEN}✓ Python bulundu: $(python3 --version)${NC}"
echo ""

# Virtual environment oluştur
echo "📦 Virtual environment oluşturuluyor..."
python3 -m venv .venv

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Virtual environment oluşturuldu${NC}"
else
    echo -e "${RED}✗ Virtual environment oluşturulamadı${NC}"
    exit 1
fi

# Virtual environment aktif et
echo ""
echo "🔄 Virtual environment aktif ediliyor..."
source .venv/bin/activate

# Bağımlılıkları yükle
echo ""
echo "📥 Bağımlılıklar yükleniyor..."
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Bağımlılıklar yüklendi${NC}"
else
    echo -e "${RED}✗ Bağımlılıklar yüklenemedi${NC}"
    exit 1
fi

# Paketi development modunda yükle
echo ""
echo "🔧 JARVIS paketi yükleniyor..."
pip install -e .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ JARVIS paketi yüklendi${NC}"
else
    echo -e "${YELLOW}⚠ Paket yüklenemedi, ancak devam edebilirsiniz${NC}"
fi

# .env dosyası kontrolü
echo ""
if [ ! -f .env ]; then
    echo "📝 .env dosyası oluşturuluyor..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ .env dosyasını düzenleyip API key ekleyin!${NC}"
    echo "   nano .env"
else
    echo -e "${GREEN}✓ .env dosyası mevcut${NC}"
fi

# data klasörü oluştur
echo ""
echo "📁 Data klasörleri oluşturuluyor..."
mkdir -p data/screenshots
echo -e "${GREEN}✓ Klasörler oluşturuldu${NC}"

# Testleri çalıştır
echo ""
echo "🧪 Testler çalıştırılıyor..."
pytest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Tüm testler başarılı${NC}"
else
    echo -e "${YELLOW}⚠ Bazı testler başarısız (API key eksikliği normal)${NC}"
fi

# Sistem bağımlılıkları kontrolü
echo ""
echo "🔊 Ses sistemi kontrolü..."
if command -v mpg123 &> /dev/null; then
    echo -e "${GREEN}✓ mpg123 bulundu${NC}"
else
    echo -e "${YELLOW}⚠ mpg123 bulunamadı (ses çalma için gerekli)${NC}"
    echo "   Kurulum: sudo apt-get install mpg123"
fi

# Özet
echo ""
echo "================================"
echo -e "${GREEN}✓ Kurulum Tamamlandı!${NC}"
echo "================================"
echo ""
echo "📋 Sonraki Adımlar:"
echo ""
echo "1. .env dosyasını düzenleyin:"
echo "   nano .env"
echo "   ANTHROPIC_API_KEY veya OPENAI_API_KEY ekleyin"
echo ""
echo "2. Virtual environment aktif edin:"
echo "   source .venv/bin/activate"
echo ""
echo "3. JARVIS'i başlatın:"
echo "   python jarvis_cli.py chat"
echo "   veya"
echo "   jarvis chat  (eğer pip install -e . çalıştıysa)"
echo ""
echo "4. Yardım için:"
echo "   python jarvis_cli.py --help"
echo ""
echo "🎉 Keyifli kullanımlar!"
