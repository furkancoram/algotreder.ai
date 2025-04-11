# app.py (Versiyon 2.3: Favori Hisseler Eklendi + 2 Kolon + Renkli Sinyal Kutusu)

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import yfinance as yf

st.set_page_config(
    page_title="Algoritmik Alım-Satım Paneli",
    page_icon="📈",
    layout="wide",
    menu_items={
        'Get help': 'mailto:destek@algotreder.com',
        'Report a bug': 'mailto:destek@algotreder.com',
        'About': "Bu platform, BIST hisseleri için AI destekli analiz ve al-sat sinyalleri sunar."
    }
)

st.title("📈 Algoritmik Alım-Satım ve Piyasa Tahmini Paneli")

st.markdown("""
Bu platform, Borsa İstanbul'daki hisse senetleri için **yapay zeka destekli** piyasa analizi ve al-sat sinyalleri üretir. 
Aşağıdan hisse senedi kodunu girerek analiz başlatabilirsiniz. Örn: `GARAN.IS`, `THYAO.IS`, `AKBNK.IS`
""")

# FAVORİ HİSSELER
st.sidebar.title("⭐ Favori Hisseler")
favoriler = ["GARAN.IS", "THYAO.IS", "AKBNK.IS", "ASELS.IS", "SISE.IS"]
favori_secim = st.sidebar.selectbox("Favori bir hisse seç:", favoriler)

# Kullanıcıdan hisse ve tarih aralığı al
hisse = st.text_input("Hisse Kodu (örnek: GARAN.IS)", value=favori_secim)
baslangic = st.date_input("Başlangıç Tarihi", value=datetime.date(2024, 1, 1))
bitis = st.date_input("Bitiş Tarihi", value=datetime.date.today())

if st.button("Veriyi Getir"):
    try:
        veri = yf.download(hisse, start=baslangic, end=bitis)

        if veri.empty:
            st.warning("Veri çekilemedi. Lütfen hisse kodunu kontrol edin.")
        else:
            if "Adj Close" in veri.columns:
                veri["Fiyat"] = veri["Adj Close"]
            elif "Close" in veri.columns:
                veri["Fiyat"] = veri["Close"]
            else:
                st.error("Veride fiyat bilgisi bulunamadı.")
                st.stop()

            if "Volume" in veri.columns:
                veri["Hacim"] = veri["Volume"]

            veri["Hareketli Ortalama 8"] = veri["Fiyat"].rolling(window=8).mean()
            veri["Hareketli Ortalama 12"] = veri["Fiyat"].rolling(window=12).mean()
            veri["Hareketli Ortalama 20"] = veri["Fiyat"].rolling(window=20).mean()

            col1, col2 = st.columns([3, 1])

            with col1:
                st.subheader("📊 Fiyat ve Hareketli Ortalamalar")
                try:
                    st.line_chart(veri[["Fiyat", "Hareketli Ortalama 8", "Hareketli Ortalama 20"]])
                except:
                    st.warning("Grafik çizilemedi. Yeterli veri olmayabilir.")

                st.subheader("🔍 Veri Önizlemesi")
                st.dataframe(veri.tail(30))

            with col2:
                son = veri.dropna().iloc[-1]
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

                st.subheader("📍 Anlık Sinyal")
                st.markdown(f"""
                    <div style='background-color:{renk};padding:25px;border-radius:10px;text-align:center;'>
                        <h2 style='color:white;'> {sinyal} </h2>
                    </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Hata oluştu: {e}")
