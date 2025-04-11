# app.py (Geliştirilmiş Mum Grafik - TradingView'e Daha Yakın Görsellik)

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
        'About': "Bu platform, Borsa İstanbul (BIST) ve ABD hisseleri için anlık ve günlük analizler sunar."
    }
)

st.title("📈 Algoritmik Alım-Satım Paneli")

st.markdown("""
Bu uygulama, **Marketstack API** kullanarak Türk ve ABD hisseleri üzerinde **gerçek zamanlı veya gün sonu analiz** yapmanı sağlar.
Türk hisseleri için gün sonu (EOD), ABD hisseleri için intraday (anlık) veri kullanılır.
""")

st.sidebar.title("⭐ Favori Hisseler")
favoriler = ["GARAN.IS", "THYAO.IS", "AKBNK.IS", "ASELS.IS", "SISE.IS", "AAPL", "MSFT", "GOOGL"]
favori_secim = st.sidebar.selectbox("Favori Hissenizi Seçin:", favoriler)

hisse = st.text_input("📌 Hisse Kodu (örn: GARAN.IS, AAPL)", value=favori_secim)
limit = st.slider("🔢 Veri Noktası Sayısı", 30, 300, 100)
interval = st.selectbox("⏱️ ABD Hisseleri İçin Zaman Aralığı", ["1min", "5min", "15min", "30min", "1hour"], index=1)

if st.button("📥 Veriyi Çek"):
    try:
        is_turkish = hisse.endswith(".IS")
        if is_turkish:
            url = f"https://api.marketstack.com/v1/eod?access_key={API_KEY}&symbols={hisse}&limit={limit}"
        else:
            url = f"https://api.marketstack.com/v1/intraday?access_key={API_KEY}&symbols={hisse}&interval={interval}&limit={limit}"

        r = requests.get(url)
        data = r.json()

        if "data" not in data or len(data["data"]) == 0:
            st.warning("⚠️ Veri çekilemedi. Lütfen hisse kodunu ve API planınızı kontrol edin.")
            st.stop()

        df = pd.DataFrame(data["data"])
        df = df.sort_values("date")
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        df.rename(columns={"close": "Fiyat", "volume": "Hacim"}, inplace=True)

        df["HO-8"] = df["Fiyat"].rolling(window=8).mean()
        df["HO-20"] = df["Fiyat"].rolling(window=20).mean()

        if "open" not in df.columns or "high" not in df.columns or "low" not in df.columns:
            st.error("Gerekli mum grafik sütunları eksik. Lütfen farklı bir hisse deneyin.")
            st.stop()

        df_clean = df.dropna(subset=["Fiyat", "HO-8", "HO-20"])

        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader("📊 Mum Grafik (TradingView Tarzı)")
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df_clean.index,
                open=df_clean["open"],
                high=df_clean["high"],
                low=df_clean["low"],
                close=df_clean["Fiyat"],
                name="Mum Grafik",
                increasing_line_color="limegreen",
                decreasing_line_color="red",
                increasing_fillcolor="rgba(0,255,0,0.6)",
                decreasing_fillcolor="rgba(255,0,0,0.6)"
            ))
            fig.add_trace(go.Scatter(x=df_clean.index, y=df_clean["HO-8"],
                                     mode='lines', name='HO-8', line=dict(color='royalblue')))
            fig.add_trace(go.Scatter(x=df_clean.index, y=df_clean["HO-20"],
                                     mode='lines', name='HO-20', line=dict(color='orange')))
            fig.update_layout(
                xaxis_rangeslider_visible=False,
                template="plotly_dark",
                plot_bgcolor="black",
                paper_bgcolor="black",
                font=dict(color="white")
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📄 Son 30 Günlük Veriler")
            tablo = df_clean.tail(30).copy().reset_index()
            tablo.rename(columns={"date": "Tarih"}, inplace=True)
            st.dataframe(tablo)

        with col2:
            if not df_clean.empty:
                son = df_clean.iloc[-1]
                ort8 = son["HO-8"]
                ort20 = son["HO-20"]

                sinyal = "BEKLE"
                renk = "gray"
                if ort8 > ort20:
                    sinyal = "AL"
                    renk = "green"
                elif ort8 < ort20:
                    sinyal = "SAT"
                    renk = "red"

                st.subheader("📍 Anlık Sinyal")
                st.markdown(f"""
                    <div style='background-color:{renk};padding:25px;border-radius:10px;text-align:center;'>
                        <h2 style='color:white;'> {sinyal} </h2>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Sinyal üretilemedi. Yeterli veri yok.")

    except Exception as e:
        st.error(f"❌ Hata oluştu: {e}")
