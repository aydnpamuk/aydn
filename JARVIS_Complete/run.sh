#!/bin/bash
# JARVIS Hızlı Başlatma Scripti

# Virtual environment kontrol et
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment bulunamadı!"
    echo "Önce kurulum yapın: bash setup.sh"
    exit 1
fi

# Virtual environment aktif et
source .venv/bin/activate

# Komut argümanı var mı?
if [ $# -eq 0 ]; then
    # Argüman yoksa interaktif mod
    echo "🤖 JARVIS İnteraktif Mod Başlatılıyor..."
    python jarvis_cli.py chat
else
    # Argümanlar varsa direkt çalıştır
    python jarvis_cli.py "$@"
fi
