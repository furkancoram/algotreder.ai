if st.button("Veriyi Getir"):
    try:
        veri = yf.download(hisse, start=baslangic, end=bitis)

        if veri.empty:
            st.warning("Veri çekilemedi. Lütfen hisse kodunu kontrol edin.")
        else:
            # Fiyat sütunu kontrolü
            if "Adj Close" in veri.columns:
                veri["Fiyat"] = veri["Adj Close"]
            elif "Close" in veri.columns:
                veri["Fiyat"] = veri["Close"]
            else:
                st.error("Veride kullanılabilir fiyat sütunu bulunamadı.")
                st.stop()

            # Hacim varsa al
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
