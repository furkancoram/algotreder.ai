# app.py (Marketstack Hibrit Mod: Türk Hisseleri EOD, ABD Hisseleri Intraday + Mum Grafik + Daha İyi Görsellik)

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import requests
import plotly.graph_objects as go

API_KEY = "0941f6e63943730e07659becf1658167"

st.set_page_config(
    page_title="Algoritmik Alım-Satım Paneli",
    page_icon="📈",
    layout="wide",
    menu_items={
        'Get help': 'mailto:destek@algotreder.com',
        'Report a bug': 'mailto:destek@algotreder.com',
        'About': "Bu platform, BIST ve ABD hisseleri için yapay zeka destekli analiz ve sinyal üretimi sunar."
    }
)

st.title("📈 Algoritmik Alım-Satım Paneli")

st.markdown("""
Bu panel, Marketstack API üzerinden **BIST hisseleri için gün sonu**, **ABD hisseleri için anlık (intraday)** verileriyle çalışır.
""")

st.sidebar.title("⭐ Favori Hisseler")
favoriler = ["GARAN.IS", "THYAO.IS", "AKBNK.IS", "ASELS.IS", "SISE.IS", "AAPL", "MSFT", "GOOGL"]
favori_secim = st.sidebar.selectbox("Favori bir hisse seçin:", favoriler)

hisse = st.text_input("Hisse Kodu", value=favori_secim)
limit = st.slider("Kaç veri noktası çekilsin?", 30, 300, 100)
interval = st.selectbox("Zaman Aralığı (ABD hisseleri için)", ["1min", "5min", "15min", "30min", "1hour"], index=1)

if st.button("🔄 Veriyi Getir"):
    try:
        is_turkish = hisse.endswith(".IS")

        if is_turkish:
            url = f"https://api.marketstack.com/v1/eod?access_key={API_KEY}&symbols={hisse}&limit={limit}"
        else:
            url = f"https://api.marketstack.com/v1/intraday?access_key={API_KEY}&symbols={hisse}&interval={interval}&limit={limit}"

        r = requests.get(url)
        data = r.json()

        if "data" not in data or len(data["data"]) == 0:
            st.warning("❗ Veri çekilemedi. Lütfen hisse kodunu ve API planınızı kontrol edin.")
            st.stop()

        df = pd.DataFrame(data["data"])
        df = df.sort_values("date")
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        df.rename(columns={"close": "Fiyat", "volume": "Hacim"}, inplace=True)

        df["Hareketli Ortalama 8"] = df["Fiyat"].rolling(window=8).mean()
        df["Hareketli Ortalama 20"] = df["Fiyat"].rolling(window=20).mean()

        ort_sutunlar = ["Hareketli Ortalama 8", "Hareketli Ortalama 20"]
        veri_clean = df.copy()
        if all(col in veri_clean.columns for col in ort_sutunlar):
            veri_clean = veri_clean.dropna(subset=ort_sutunlar)
        else:
            st.warning("Hareketli ortalamalar hesaplanamadı. Veride eksiklik olabilir.")
            st.stop()

        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader("📊 Mum Grafik + Ortalamalar")
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=veri_clean.index,
                open=veri_clean["open"],
                high=veri_clean["high"],
                low=veri_clean["low"],
                close=veri_clean["Fiyat"],
                name="Mum Grafik"
            ))
            fig.add_trace(go.Scatter(x=veri_clean.index, y=veri_clean["Hareketli Ortalama 8"],
                                     mode='lines', name='HO-8'))
            fig.add_trace(go.Scatter(x=veri_clean.index, y=veri_clean["Hareketli Ortalama 20"],
                                     mode='lines', name='HO-20'))
            fig.update_layout(xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("🔍 Son Veriler")
            tablo = veri_clean.tail(30).copy()
            tablo.reset_index(inplace=True)
            tablo.rename(columns={"date": "Tarih"}, inplace=True)
            st.dataframe(tablo)

        with col2:
            if not veri_clean.empty:
                son = veri_clean.iloc[-1]
                ort8 = son["Hareketli Ortalama 8"]
                ort20 = son["Hareketli Ortalama 20"]

                sinyal = "BEKLE"
                renk = "gray"
                if ort8 > ort20:
                    sinyal = "AL"
                    renk = "green"
                elif ort8 < ort20:
                    sinyal = "SAT"
                    renk = "red"

                st.subheader("📍 Güncel Sinyal")
                st.markdown(f"""
                    <div style='background-color:{renk};padding:25px;border-radius:10px;text-align:center;'>
                        <h2 style='color:white;'> {sinyal} </h2>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Yeterli veri bulunamadı. Sinyal üretilemedi.")

    except Exception as e:
        st.error(f"❌ Hata oluştu: {e}")
