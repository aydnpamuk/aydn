"""
Amazon PPC Dashboard - Streamlit Web App

Antigravity veya lokal tarayıcıda çalıştırılabilir
"""

import streamlit as st
from datetime import datetime

from src.core.metrics.calculator import MetricsCalculator
from src.core.benchmarks.standards import BenchmarkEvaluator
from src.core.formulas.bid_optimization import RPCBidOptimizer
from src.decision.acos.manager import ACoSDecisionTree
from src.crisis.stockout.protocol import StockoutProtocol
from src.core.constants.golden_rules import GoldenRulesChecker

# Page config
st.set_page_config(
    page_title="Amazon PPC Manager",
    page_icon="📊",
    layout="wide",
)

# Header
st.title("📊 Amazon PPC & SEO Management System")
st.markdown("*Based on Amazon PPC & SEO Bible v3.0 (Rating: 9.5/10)*")

# Sidebar
st.sidebar.title("🔧 Navigation")
page = st.sidebar.radio(
    "Seçim yapın:",
    [
        "📈 Kampanya Analizi",
        "💰 Bid Optimizasyonu",
        "🚨 Stok Kontrolü",
        "⚖️ Golden Rules Check",
        "📚 Benchmark Karşılaştırma",
    ],
)

# ============================
# PAGE 1: Kampanya Analizi
# ============================
if page == "📈 Kampanya Analizi":
    st.header("📈 Kampanya Performans Analizi")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Finansal Veriler")
        ad_spend = st.number_input("Reklam Harcaması ($)", min_value=0.0, value=500.0, step=10.0)
        ad_sales = st.number_input("Reklam Satışları ($)", min_value=0.0, value=2000.0, step=10.0)
        total_sales = st.number_input("Toplam Satışlar ($)", min_value=0.0, value=5000.0, step=10.0)

    with col2:
        st.subheader("📊 Trafik Verileri")
        impressions = st.number_input("Gösterim Sayısı", min_value=0, value=10000, step=100)
        clicks = st.number_input("Tıklama Sayısı", min_value=0, value=100, step=1)
        orders = st.number_input("Sipariş Sayısı", min_value=0, value=10, step=1)

    if st.button("📊 Analiz Et", type="primary"):
        # Calculate metrics
        result = MetricsCalculator.calculate(
            ad_spend=ad_spend,
            ad_sales=ad_sales,
            total_sales=total_sales,
            impressions=impressions,
            clicks=clicks,
            orders=orders,
        )

        # Display results
        st.success("✅ Analiz Tamamlandı!")

        # Metrics in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("ACoS", f"{result.acos:.2f}%",
                     delta=f"Hedef: 25%" if float(result.acos) <= 25 else "Hedefin üstünde",
                     delta_color="normal" if float(result.acos) <= 25 else "inverse")

        with col2:
            st.metric("TACOS", f"{result.tacos:.2f}%",
                     delta="Sağlıklı" if 8 <= float(result.tacos) <= 12 else "Dikkat")

        with col3:
            st.metric("CTR", f"{result.ctr:.3f}%",
                     delta="İyi" if float(result.ctr) >= 0.5 else "Optimize et")

        with col4:
            st.metric("CVR", f"{result.cvr:.2f}%",
                     delta="İyi" if float(result.cvr) >= 10 else "Düşük")

        # Detailed table
        st.subheader("📋 Detaylı Metrikler")
        metrics_data = {
            "Metrik": ["ACoS", "TACOS", "ROAS", "CTR", "CVR", "RPC", "CPC"],
            "Değer": [
                f"{result.acos:.2f}%",
                f"{result.tacos:.2f}%",
                f"{result.roas:.2f}x",
                f"{result.ctr:.3f}%",
                f"{result.cvr:.2f}%",
                f"${result.rpc:.2f}",
                f"${result.cpc:.2f}",
            ],
        }
        st.table(metrics_data)

        # Performance summary
        organic_sales = float(total_sales - ad_sales)
        ppc_sales = float(ad_sales)
        ratio = organic_sales / ppc_sales if ppc_sales > 0 else 0

        st.info(f"🎯 **Organic:PPC Ratio:** {ratio:.1f}:1")

        if ratio >= 3:
            st.success("✅ Mükemmel - Sürdürülebilir")
        elif ratio >= 2:
            st.success("✅ Sağlıklı")
        elif ratio >= 1:
            st.warning("⚠️ Normal büyüme")
        else:
            st.error("❌ PPC'ye bağımlı")

# ============================
# PAGE 2: Bid Optimizasyonu
# ============================
elif page == "💰 Bid Optimizasyonu":
    st.header("💰 Bid Optimizasyonu (RPC Formülü)")

    st.info("📐 **Formül:** Optimal Bid = RPC × Target ACoS")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Mevcut Veriler")
        current_bid = st.number_input("Mevcut Bid ($)", min_value=0.0, value=2.0, step=0.1)
        total_sales_bid = st.number_input("Toplam Satış ($)", min_value=0.0, value=1000.0, step=10.0, key="bid_sales")
        total_clicks_bid = st.number_input("Toplam Tıklama", min_value=1, value=200, step=1, key="bid_clicks")

    with col2:
        st.subheader("🎯 Hedefler")
        target_acos = st.slider("Hedef ACoS (%)", min_value=5, max_value=50, value=25, step=1)
        current_acos_input = st.number_input("Mevcut ACoS (%)", min_value=0.0, value=40.0, step=1.0)

    if st.button("💡 Öneri Al", type="primary"):
        recommendation = RPCBidOptimizer.recommend_bid_adjustment(
            current_bid=current_bid,
            total_sales=total_sales_bid,
            total_clicks=total_clicks_bid,
            target_acos=target_acos / 100,
            current_acos=current_acos_input / 100,
        )

        st.success("✅ Optimizasyon Önerisi Hazır!")

        # Show recommendation
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Mevcut Bid", f"${recommendation.current_bid:.2f}")

        with col2:
            change_color = "normal" if float(recommendation.change_percentage) < 0 else "inverse"
            st.metric(
                "Önerilen Bid",
                f"${recommendation.recommended_bid:.2f}",
                delta=f"{recommendation.change_percentage:.1f}%",
                delta_color=change_color,
            )

        with col3:
            st.metric("Güven Seviyesi", recommendation.confidence.upper())

        # Explanation
        st.info(f"💡 **Açıklama:** {recommendation.reason}")

        # RPC Calculation
        rpc = total_sales_bid / total_clicks_bid
        st.markdown("---")
        st.subheader("🔢 Hesaplama Detayları")
        st.code(f"""
RPC = Total Sales / Total Clicks
RPC = ${total_sales_bid} / {total_clicks_bid}
RPC = ${rpc:.2f}

Optimal Bid = RPC × Target ACoS
Optimal Bid = ${rpc:.2f} × {target_acos/100:.2f}
Optimal Bid = ${recommendation.recommended_bid:.2f}
        """)

# ============================
# PAGE 3: Stok Kontrolü
# ============================
elif page == "🚨 Stok Kontrolü":
    st.header("🚨 Stok Krizi Yönetimi")

    st.warning("⚠️ **GOLDEN RULE #1:** NEVER RUN OUT OF STOCK")

    col1, col2 = st.columns(2)

    with col1:
        current_stock = st.number_input("Mevcut Stok (birim)", min_value=0, value=100, step=1)
        daily_velocity = st.number_input("Günlük Satış Hızı", min_value=0.1, value=5.0, step=0.1)

    with col2:
        lead_time = st.number_input("Lead Time (gün)", min_value=1, value=30, step=1)

    if st.button("🔍 Stok Durumunu Analiz Et", type="primary"):
        analysis = StockoutProtocol.analyze_stock_situation(
            current_stock=current_stock,
            daily_velocity=daily_velocity,
            lead_time_days=lead_time,
        )

        # Status indicator
        status_colors = {
            "HEALTHY": "🟢",
            "WARNING": "🟡",
            "CRITICAL": "🔴",
            "EMERGENCY": "🚨",
        }
        status_icon = status_colors.get(analysis.stock_level.value.upper(), "⚪")

        st.markdown(f"## {status_icon} Durum: {analysis.stock_level.value.upper()}")

        # Metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Mevcut Stok", f"{analysis.current_stock} birim")

        with col2:
            st.metric("Kalan Gün", f"{analysis.days_remaining:.1f} gün")

        with col3:
            reorder_point = StockoutProtocol.calculate_reorder_point(
                daily_velocity=daily_velocity, lead_time_days=lead_time
            )
            st.metric("Reorder Point", f"{reorder_point} birim")

        # PPC Recommendation
        should_pause = StockoutProtocol.should_pause_ppc(analysis.days_remaining)
        budget_multiplier = StockoutProtocol.calculate_budget_reduction(analysis.days_remaining)

        if should_pause:
            st.error("🚨 **PPC Önerisi:** TÜM KAMPANYALARI DURDUR!")
        elif budget_multiplier < 1.0:
            reduction = (1 - budget_multiplier) * 100
            st.warning(f"⚠️ **PPC Önerisi:** Bütçeyi %{reduction:.0f} azalt")
        else:
            st.success("✅ **PPC Önerisi:** Normal operasyonlara devam")

        # Action plan
        if analysis.recommended_actions:
            st.subheader("📋 Aksiyon Planı")
            for idx, action in enumerate(analysis.recommended_actions, 1):
                priority_icons = {
                    "immediate": "🔴",
                    "short_term": "🟡",
                    "medium_term": "🔵",
                }
                icon = priority_icons.get(action.priority.value, "⚪")

                with st.expander(f"{icon} {idx}. {action.priority.value.upper()}: {action.action}"):
                    st.write(f"**Neden:** {action.reason}")
                    if action.deadline:
                        st.write(f"**Son Tarih:** {action.deadline.strftime('%d/%m/%Y %H:%M')}")

# ============================
# PAGE 4: Golden Rules Check
# ============================
elif page == "⚖️ Golden Rules Check":
    st.header("⚖️ Golden Rules Compliance Check")

    st.info("5 Altın Kural - Amazon PPC başarısının temeli")

    with st.form("golden_rules_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📦 Stok Bilgileri")
            gr_stock = st.number_input("Mevcut Stok", min_value=0, value=500, key="gr_stock")
            gr_velocity = st.number_input("Günlük Satış", min_value=0.1, value=8.0, key="gr_velocity")
            gr_lead_time = st.number_input("Lead Time (gün)", min_value=1, value=30, key="gr_lead")

        with col2:
            st.subheader("💰 Bütçe ve Kampanya")
            gr_budget = st.number_input("Bütçe Tüketimi (%)", min_value=0.0, max_value=100.0, value=65.0)
            gr_hour = st.slider("Mevcut Saat", min_value=0, max_value=23, value=18)
            gr_paused = st.number_input("Durmuş Kampanya Sayısı", min_value=0, value=0)

        st.subheader("📊 Satış Verileri")
        col3, col4 = st.columns(2)
        with col3:
            gr_organic = st.number_input("Organik Satış ($)", min_value=0.0, value=6000.0)
        with col4:
            gr_ppc = st.number_input("PPC Satış ($)", min_value=0.0, value=2000.0)

        submitted = st.form_submit_button("🔍 Kontrol Et", type="primary")

        if submitted:
            violations = GoldenRulesChecker.check_all(
                current_stock=int(gr_stock),
                daily_sales_velocity=float(gr_velocity),
                lead_time_days=int(gr_lead_time),
                budget_spent_percentage=float(gr_budget),
                current_hour=int(gr_hour),
                campaigns_paused=int(gr_paused),
                organic_sales=float(gr_organic),
                ppc_sales=float(gr_ppc),
            )

            if not violations:
                st.success("✅ **TÜM GOLDEN RULES'A UYUMLU!**")
                st.balloons()
                st.info("Hesabınız en iyi pratiklere uygun şekilde yönetiliyor.")
            else:
                st.error(f"⚠️ **{len(violations)} İHLAL TESPİT EDİLDİ!**")

                for idx, violation in enumerate(violations, 1):
                    severity_colors = {
                        "critical": "🔴",
                        "high": "🟡",
                        "medium": "🔵",
                        "low": "⚪",
                    }
                    icon = severity_colors.get(violation.severity.value, "⚪")

                    with st.expander(f"{icon} Kural #{violation.rule_number}: {violation.rule_name}"):
                        st.write(f"**Ciddiyet:** {violation.severity.value.upper()}")
                        st.write(f"**Mesaj:** {violation.message}")
                        st.write(f"**Önerilen Aksiyon:** {violation.recommended_action}")
                        st.write(f"**Etki:** {violation.impact}")

# ============================
# PAGE 5: Benchmark
# ============================
elif page == "📚 Benchmark Karşılaştırma":
    st.header("📚 Benchmark Karşılaştırma")

    st.info("Metriklerinizi sektör standartlarıyla karşılaştırın")

    col1, col2 = st.columns(2)

    with col1:
        bm_ctr = st.number_input("PPC CTR (%)", min_value=0.0, value=0.65, step=0.01)
        bm_cvr = st.number_input("CVR (%)", min_value=0.0, value=12.0, step=0.1)
        bm_acos = st.number_input("ACoS (%)", min_value=0.0, value=28.0, step=1.0)

    with col2:
        bm_tacos = st.number_input("TACOS (%)", min_value=0.0, value=10.0, step=0.1)
        bm_organic = st.number_input("Organik Satış ($)", min_value=0.0, value=3000.0)
        bm_ppc_sales = st.number_input("PPC Satış ($)", min_value=0.0, value=2000.0)

    if st.button("📊 Değerlendir", type="primary"):
        evaluation = BenchmarkEvaluator.evaluate_all(
            ctr_ppc=bm_ctr,
            cvr=bm_cvr,
            acos=bm_acos,
            tacos=bm_tacos,
            organic_sales=bm_organic,
            ppc_sales=bm_ppc_sales,
        )

        st.success("✅ Değerlendirme Tamamlandı!")

        # Create comparison table
        if "ctr_ppc" in evaluation:
            st.subheader("🎯 CTR (Click-Through Rate)")
            level = evaluation["ctr_ppc"]["level"].value
            st.metric("Performans Seviyesi", level.upper())
            st.progress(min(bm_ctr, 1.0))

        if "cvr" in evaluation:
            st.subheader("💰 CVR (Conversion Rate)")
            level = evaluation["cvr"]["level"].value
            st.metric("Performans Seviyesi", level.upper())
            st.progress(min(bm_cvr / 20, 1.0))

        if "acos" in evaluation:
            st.subheader("📉 ACoS")
            level = evaluation["acos"]["level"].value
            st.metric("Performans Seviyesi", level.upper())

        if "tacos" in evaluation:
            st.subheader("📊 TACOS")
            strategy = evaluation["tacos"]["strategy"]
            st.metric("Strateji", strategy.upper())
            if evaluation["tacos"]["is_healthy"]:
                st.success("✅ Sağlıklı aralıkta (8-12%)")
            else:
                st.warning("⚠️ Sağlıklı aralık dışında")

        if "organic_ppc_ratio" in evaluation:
            st.subheader("🔄 Organic:PPC Ratio")
            ratio = evaluation["organic_ppc_ratio"]["ratio"]
            health = evaluation["organic_ppc_ratio"]["health"]
            st.metric("Oran", f"{ratio:.1f}:1")
            st.metric("Sağlık Durumu", health.upper())

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p><strong>Amazon PPC & SEO Management System v1.0.0</strong></p>
        <p>Based on Amazon PPC & SEO Bible v3.0 (Rating: 9.5/10)</p>
    </div>
    """,
    unsafe_allow_html=True,
)
