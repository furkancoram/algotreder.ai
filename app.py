# app.py (Marketstack Entegrasyonu - Gerçek Zamanlı BIST Veri Çekimi)

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import requests
import matplotlib.pyplot as plt

API_KEY = "0941f6e63943730e07659becf1658167"

st.set_page_config(
    page_title="Algoritmik Alım-Satım Paneli",
    page_icon="📈",
    layout="wide",
    menu_items={
        'Get help': 'mailto:destek@algotreder.com',
        'Report a bug': 'mailto:destek@algotreder.com',
        'About': "Bu platform, Borsa İstanbul (BIST) hisseleri için yapay zeka destekli analiz ve al-sat sinyalleri sunar."
    }
)

st.title("📈 Algoritmik Alım-Satım ve Piyasa Tahmini Paneli")

st.markdown("""
Bu platform, Borsa İstanbul'daki hisse senetleri için **gerçek zamanlı API verisiyle** piyasa analizi ve al-sat sinyalleri üretir. 
Marketstack API ile entegredir. 
""")

st.sidebar.title("⭐ Favori Hisseler")
favoriler = ["GARAN.IS", "THYAO.IS", "AKBNK.IS", "ASELS.IS", "SISE.IS"]
favori_secim = st.sidebar.selectbox("Favori bir hisse seçin:", favoriler)

hisse = st.text_input("Hisse Kodu (örn: GARAN.IS)", value=favori_secim)
limit = st.slider("Kaç günlük veri çekilsin?", 30, 300, 100)

if st.button("🔄 Veriyi Getir"):
    try:
        url = f"http://api.marketstack.com/v1/eod?access_key={API_KEY}&symbols={hisse}&limit={limit}"
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

        df["Hareketli Ortalama 8 Gün"] = df["Fiyat"].rolling(window=8).mean()
        df["Hareketli Ortalama 12 Gün"] = df["Fiyat"].rolling(window=12).mean()
        df["Hareketli Ortalama 20 Gün"] = df["Fiyat"].rolling(window=20).mean()

        ort_sutunlar = ["Hareketli Ortalama 8 Gün", "Hareketli Ortalama 20 Gün"]
        veri_clean = df.copy()
        if all(col in veri_clean.columns for col in ort_sutunlar):
            veri_clean = veri_clean.dropna(subset=ort_sutunlar)
        else:
            st.warning("Hareketli ortalamalar hesaplanamadı. Veride eksiklik olabilir.")
            st.stop()

        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader("📊 Fiyat ve Hareketli Ortalama Grafiği")
            try:
                st.line_chart(veri_clean[["Fiyat", "Hareketli Ortalama 8 Gün", "Hareketli Ortalama 20 Gün"]])
            except:
                st.warning("⚠️ Grafik çizilemedi. Yeterli veri olmayabilir.")

            st.subheader("📉 Hacim (İşlem Miktarı) Grafiği")
            try:
                fig, ax = plt.subplots(figsize=(10, 3))
                ax.bar(veri_clean.index, veri_clean["Hacim"], color='orange')
                ax.set_title("Günlük Hacim")
                ax.set_xlabel("Tarih")
                ax.set_ylabel("Hacim")
                st.pyplot(fig)
            except:
                st.warning("⚠️ Hacim grafiği çizilemedi.")

            st.subheader("🔍 Son 30 Günlük Veri Tablosu")
            tablo = veri_clean.tail(30).copy()
            tablo.reset_index(inplace=True)
            tablo.rename(columns={
                "date": "Tarih",
                "open": "Açılış",
                "high": "En Yüksek",
                "low": "En Düşük",
                "close": "Kapanış",
                "volume": "Hacim (Ham)",
            }, inplace=True)
            st.dataframe(tablo)

        with col2:
            if not veri_clean.empty:
                son = veri_clean.iloc[-1]
                ort8 = son["Hareketli Ortalama 8 Gün"]
                ort20 = son["Hareketli Ortalama 20 Gün"]

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
