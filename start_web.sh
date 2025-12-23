#!/bin/bash

echo "🚀 Amazon PPC Dashboard Başlatılıyor..."
echo ""
echo "📦 Bağımlılıklar kontrol ediliyor..."

# Check if streamlit is installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "⚠️  Streamlit kurulu değil. Kuruluyor..."
    pip install -q streamlit plotly
    echo "✅ Streamlit kuruldu!"
fi

echo ""
echo "🌐 Dashboard başlatılıyor..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Tarayıcınız otomatik açılacak"
echo "  URL: http://localhost:8501"
echo ""
echo "  Durdurmak için: CTRL+C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start streamlit
streamlit run src/web/app.py
