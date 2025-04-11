# app.py

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import yfinance as yf

st.set_page_config(page_title="Algoritmik Alım-Satım Paneli", layout="wide")
st.title("📈 Algoritmik Alım-Satım ve Piyasa Tahmini Paneli")

st.markdown("""
Bu platform, Borsa İstanbul'daki hisse senetleri için **yapay zeka destekli** piyasa analizi ve al-sat sinyalleri üretir. 
Aşağıdan hisse senedi kodunu girerek analiz başlatabilirsiniz. Örn: `GARAN.IS`, `THYAO.IS`, `AKBNK.IS`
""")

# Kullanıcıdan hisse ve tarih aralığı al
hisse = st.text_input("Hisse Kodu (örnek: GARAN.IS)", value="GARAN.IS")
baslangic = st.date_input("Başlangıç Tarihi", value=datetime.date(2024, 1, 1))
bitis = st.date_input("Bitiş Tarihi", value=datetime.date.today())

if st.button("Veriyi Getir"):
    try:
        veri = yf.download(hisse, start=baslangic, end=bitis)

        if veri.empty:
            st.warning("Veri çekilemedi. Lütfen hisse kodunu kontrol edin.")
        else:
            # Güvenli sütun seçimi
            if "Adj Close" in veri.columns:
                veri["Fiyat"] = veri["Adj Close"]
            elif "Close" in veri.columns:
                veri["Fiyat"] = veri["Close"]
            else:
                st.error("Veride fiyat bilgisi bulunamadı.")
                st.stop()

            if "Volume" in veri.columns:
                veri["Hacim"] = veri["Volume"]

            # Hareketli ortalamalar
            veri["Hareketli Ortalama 8"] = veri["Fiyat"].rolling(window=8).mean()
            veri["Hareketli Ortalama 12"] = veri["Fiyat"].rolling(window=12).mean()
            veri["Hareketli Ortalama 20"] = veri["Fiyat"].rolling(window=20).mean()

            st.subheader("📊 Fiyat ve Hareketli Ortalamalar")
            st.line_chart(veri[["Fiyat", "Hareketli Ortalama 8", "Hareketli Ortalama 20"]])

            st.subheader("🔍 Veri Önizlemesi")
            st.dataframe(veri.tail(30))

            # Sinyal üret
            son = veri.iloc[-1]
            ort8 = son["Hareketli Ortalama 8"]
            ort20 = son["Hareketli Ortalama 20"]

            sinyal = "BEKLE"
            if ort8 > ort20:
                sinyal = "AL"
            elif ort8 < ort20:
                sinyal = "SAT"

            st.subheader("📍 Anlık Sinyal")
            st.markdown(f"### {sinyal}")

    except Exception as e:
        st.error(f"Hata oluştu: {e}")
