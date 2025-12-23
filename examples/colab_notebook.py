"""
Amazon PPC System - Google Colab Setup

Bu script'i Google Colab'da çalıştırın:
https://colab.research.google.com/
"""

# ==================================
# 1. KURULUM
# ==================================

print("📦 Kurulum başlıyor...")

# Clone repository
get_ipython().system('git clone https://github.com/aydnpamuk/aydn.git')
get_ipython().run_line_magic('cd', 'aydn')
get_ipython().system('git checkout claude/amazon-ppc-seo-system-kVtQH')

# Install dependencies
get_ipython().system('pip install -q typer pydantic pandas numpy rich python-dateutil streamlit plotly')

print("✅ Kurulum tamamlandı!\n")

# ==================================
# 2. STREAMLIT DASHBOARD BAŞLAT
# ==================================

print("🌐 Streamlit dashboard başlatılıyor...")

# Install ngrok for public URL
get_ipython().system('pip install -q pyngrok')

from pyngrok import ngrok
import subprocess
import time

# Start streamlit in background
subprocess.Popen(['streamlit', 'run', 'src/web/app.py', '--server.port', '8501'])

# Wait for streamlit to start
time.sleep(5)

# Create public tunnel
public_url = ngrok.connect(8501)

print("\n" + "="*60)
print("✅ Dashboard hazır!")
print("="*60)
print(f"\n🌐 Public URL: {public_url}")
print("\n📝 Tarayıcınızda yukarıdaki URL'yi açın")
print("="*60 + "\n")

# ==================================
# 3. VEYA PYTHON API KULLANIMI
# ==================================

print("\n💡 Python API ile doğrudan kullanım:\n")

# Import modules
import sys
sys.path.insert(0, '/content/aydn')

from src.core.metrics.calculator import MetricsCalculator
from src.decision.acos.manager import ACoSDecisionTree
from src.crisis.stockout.protocol import StockoutProtocol

print("Örnek 1: Metrik Hesaplama")
print("-" * 40)

result = MetricsCalculator.calculate(
    ad_spend=500,
    ad_sales=2000,
    total_sales=5000,
    impressions=10000,
    clicks=100,
    orders=10
)

print(f"ACoS: {result.acos:.2f}%")
print(f"TACOS: {result.tacos:.2f}%")
print(f"CTR: {result.ctr:.3f}%")
print(f"CVR: {result.cvr:.2f}%\n")

print("Örnek 2: ACoS Karar Ağacı")
print("-" * 40)

decision = ACoSDecisionTree.evaluate(
    acos=67.0,
    clicks=25,
    cvr=8.0
)

print(f"Aksiyon: {decision.action.value}")
print(f"Açıklama: {decision.reason}\n")

print("Örnek 3: Stok Kontrolü")
print("-" * 40)

analysis = StockoutProtocol.analyze_stock_situation(
    current_stock=100,
    daily_velocity=5.0,
    lead_time_days=30
)

print(f"Kalan Gün: {analysis.days_remaining:.1f}")
print(f"Durum: {analysis.stock_level.value}")
print(f"Aksiyon Sayısı: {len(analysis.recommended_actions)}\n")

print("="*60)
print("🎉 Hazırsınız! Dashboard veya API kullanabilirsiniz.")
print("="*60)
