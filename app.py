# app.py (TradingView Widget Entegre)

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="TradingView Paneli",
    page_icon="📈",
    layout="wide",
    menu_items={
        'Get help': 'mailto:destek@algotreder.com',
        'Report a bug': 'mailto:destek@algotreder.com',
        'About': "Bu uygulama TradingView'in gelişmiş grafik altyapısını kullanır."
    }
)

st.title("📊 Gerçek Zamanlı TradingView Grafiği")

st.markdown("""
Bu panelde TradingView’in gerçek zamanlı, profesyonel mum grafik arayüzü entegre edilmiştir. 
İlgilendiğiniz hisseyi seçerek doğrudan canlı veri akışıyla detaylı analiz yapabilirsiniz.
""")

sembol = st.text_input("TradingView Sembolü (örn: BIST:XU100, BIST:GARAN, NASDAQ:AAPL)", value="BIST:XU100")

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
      "allow_symbol_change": true,
      "container_id": "tradingview_chart"
    }});
  </script>
</div>
"""

components.html(html_code, height=650)
