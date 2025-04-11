# app.py (Tam Sayfa Tasarımı: Hisse Listesi + TradingView Grafik + KAP Haber Akışı + Döviz ve Endeks Paneli)

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(
    page_title="Borsa İzleme Paneli",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get help': 'mailto:destek@borsapanel.com',
        'About': "Bu platform, TradingView altyapısı ile gerçek zamanlı grafikler sunar."
    }
)

# Başlık ve üst info bar
st.markdown("""
<style>
    .title-bar {{
        background-color: #0e1117;
        padding: 10px 20px;
        border-radius: 8px;
        color: #fff;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 10px;
    }}
</style>
<div class="title-bar">
    📈 BIST100: 9380,95 | BIST30: 10214,77 | USD/TRY: 38,03 | EUR/TRY: 43,28
</div>
""", unsafe_allow_html=True)

st.title("📊 Gerçek Zamanlı Borsa Paneli")

col1, col2, col3 = st.columns([1.2, 4, 1.6], gap="large")

# Sol sütun - Hisse listesi
with col1:
    st.subheader("📋 Hisse Listesi (500+)")
    hisse_listesi = pd.read_csv("https://raw.githubusercontent.com/erkansirin78/dataset-bist/main/bist100.csv")
    secilen = st.selectbox("Bir hisse seçin:", hisse_listesi["Kod"].sort_values(), index=0)
    sembol = f"BIST:{secilen}" if not secilen.startswith("BIST:") else secilen

# Orta sütun - TradingView Grafik
with col2:
    st.subheader(f"📈 {sembol} Canlı Grafik")
    html_code = f"""
    <div class="tradingview-widget-container">
      <div id="tradingview_chart"></div>
      <script src="https://s3.tradingview.com/tv.js"></script>
      <script>
        new TradingView.widget({{
          "width": "100%",
          "height": 600,
          "symbol": "{sembol}",
          "interval": "D",
          "timezone": "Europe/Istanbul",
          "theme": "dark",
          "style": "1",
          "locale": "tr",
          "toolbar_bg": "#1e1e1e",
          "enable_publishing": false,
          "allow_symbol_change": false,
          "container_id": "tradingview_chart"
        }});
      </script>
    </div>
    """
    components.html(html_code, height=620)

# Sağ sütun - KAP haber akışı
with col3:
    st.subheader("📰 Son Dakika KAP Haberleri")
    kap_veri = pd.DataFrame([
        {"Hisse": "EKGYO", "Saat": "22:34", "Başlık": "Özel Durum Açıklaması (Genel)"},
        {"Hisse": "HURGZ", "Saat": "22:21", "Başlık": "Bağımsız Denetim Kuruluşunun Belirlenmesi"},
        {"Hisse": "HURGZ", "Saat": "22:20", "Başlık": "Genel Kurul İşlemlerine İlişkin Bildirim"},
        {"Hisse": "BINHO", "Saat": "22:04", "Başlık": "Bağımsız Denetim Kuruluşunun Belirlenmesi"},
        {"Hisse": "SELVA", "Saat": "22:00", "Başlık": "Kar Payı Dağıtım İşlemlerine İlişkin"},
    ])
    for index, row in kap_veri.iterrows():
        st.markdown(f"**{row['Saat']}** • `{row['Hisse']}` → {row['Başlık']}")
