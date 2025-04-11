# app.py

import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="Algoritmik Alım-Satım Paneli", layout="wide")
st.title("📈 Algoritmik Alım-Satım ve Piyasa Tahmini Paneli")

st.markdown("""
Bu platform, Borsa İstanbul'daki hisse senetleri için **yapay zeka destekli** piyasa analizi ve al-sat sinyalleri üretir. 
İlk adımda, sahte (dummy) verilerle çalışan bir demo arayüzü kuruyoruz.
""")

tarihler = pd.date_range(start="2024-01-01", end=datetime.datetime.today(), freq='D')
veri = pd.DataFrame({
    "Tarih": tarihler,
    "Fiyat": np.cumsum(np.random.randn(len(tarihler))) + 100,
})
veri["Hareketli Ortalama 8"] = veri["Fiyat"].rolling(window=8).mean()
veri["Hareketli Ortalama 12"] = veri["Fiyat"].rolling(window=12).mean()
veri["Hareketli Ortalama 20"] = veri["Fiyat"].rolling(window=20).mean()

st.subheader("📊 Fiyat ve Hareketli Ortalamalar")
st.line_chart(veri.set_index("Tarih"))

st.subheader("🔍 Veri Önizlemesi")
st.dataframe(veri.tail(30))

son_fiyat = veri.iloc[-1]["Fiyat"]
son_ort8 = veri.iloc[-1]["Hareketli Ortalama 8"]
son_ort20 = veri.iloc[-1]["Hareketli Ortalama 20"]

sinyal = "BEKLE"
if son_ort8 > son_ort20:
    sinyal = "AL"
elif son_ort8 < son_ort20:
    sinyal = "SAT"

st.subheader("📍 Anlık Sinyal")
st.markdown(f"### {sinyal}")
