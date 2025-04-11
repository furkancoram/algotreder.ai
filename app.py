# app.py (Versiyon 2.4: Ekstra Grafik Eklendi - Hacim Çubuğu Grafiği)

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import yfinance as yf
import matplotlib.pyplot as plt

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
Bu platform, Borsa İstanbul'daki hisse senetleri için **yapay zeka destekli** piyasa analizi ve al-sat sinyalleri üretir. 
Aşağıdan hisse senedi kodunu girerek analiz başlatabilirsiniz. Örnekler: `GARAN.IS`, `THYAO.IS`, `AKBNK.IS`
""")

# FAVORİ HİSSELER
st.sidebar.title("⭐ Favori Hisseler")
favoriler = ["GARAN.IS", "THYAO.IS", "AKBNK.IS", "ASELS.IS", "SISE.IS"]
favori_secim = st.sidebar.selectbox("Favori bir hisse seçin:", favoriler)

# Kullanıcıdan hisse ve tarih aralığı al
hisse = st.text_input("Hisse Kodu (örn: GARAN.IS)", value=favori_secim)
baslangic = st.date_input("Veri Başlangıç Tarihi", value=datetime.date(2024, 1, 1))
bitis = st.date_input("Veri Bitiş Tarihi", value=datetime.date.today())

if st.button("🔄 Veriyi Getir"):
    try:
        veri = yf.download(hisse, start=baslangic, end=bitis)

        if veri.empty:
            st.warning("❗ Veri çekilemedi. Lütfen hisse kodunu kontrol edin.")
        else:
            if "Adj Close" in veri.columns:
                veri["Fiyat"] = veri["Adj Close"]
            elif "Close" in veri.columns:
                veri["Fiyat"] = veri["Close"]
            else:
                st.error("❌ Veride fiyat bilgisi bulunamadı.")
                st.stop()

            if "Volume" in veri.columns:
                veri["Hacim"] = veri["Volume"]

            veri["Hareketli Ortalama 8 Gün"] = veri["Fiyat"].rolling(window=8).mean()
            veri["Hareketli Ortalama 12 Gün"] = veri["Fiyat"].rolling(window=12).mean()
            veri["Hareketli Ortalama 20 Gün"] = veri["Fiyat"].rolling(window=20).mean()

            # Sadece geçerli (NaN olmayan) veriyi kullanalım
            veri_clean = veri.dropna(subset=["Hareketli Ortalama 8 Gün", "Hareketli Ortalama 20 Gün"])

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
                    "Date": "Tarih",
                    "Open": "Açılış",
                    "High": "En Yüksek",
                    "Low": "En Düşük",
                    "Close": "Kapanış",
                    "Volume": "Hacim (Ham)",
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
