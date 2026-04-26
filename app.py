import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="Screener de Gabriel", layout="wide")

st.title("📊 Estrategia de Acecho - Gabriel Herrera")
st.sidebar.header("Ajustar Filtros")

# Filtros que definimos juntos
market_cap_min = st.sidebar.number_input("Market Cap Mínimo (Billones $)", value=50, step=10)
rsi_max = st.sidebar.slider("RSI Máximo", 0, 100, 35)
prox_piso = st.sidebar.slider("Cercanía al mínimo 52W (%)", 0, 20, 10)

# Tu lista de seguimiento (podes agregar mas tickers aca)
tickers = ["MCD", "JNJ", "DHR", "XOM", "CVX", "KO", "PG", "JPM", "MSFT", "GOOGL", "AAPL", "TXN", "WMT", "MCHI"]

def obtener_datos(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        if hist.empty: return None

        # Calculo de Indicadores
        hist['RSI'] = ta.rsi(hist['Close'], length=14)
        macd = ta.macd(hist['Close'])
        
        # Ultimos valores
        precio = hist['Close'].iloc[-1]
        min_52w = hist['Close'].min()
        dist_piso = ((precio - min_52w) / min_52w) * 100
        rsi_val = hist['RSI'].iloc[-1]
        
        # Inercia MACD (Viendo si el histograma sube o baja)
        h_macd = macd['MACDh_12_26_9']
        inercia = "⬆️ Subiendo" if h_macd.iloc[-1] > h_macd.iloc[-2] else "⬇️ Bajando"

        return {
            "Ticker": ticker,
            "Precio": round(precio, 2),
            "RSI": round(rsi_val, 2),
            "Dist. al Piso (%)": round(dist_piso, 2),
            "Market Cap (B)": round(stock.info.get('marketCap', 0) / 1e9, 2),
            "Inercia (MACD)": inercia
        }
    except: return None

if st.button('🔍 Buscar Ofertas Ahora'):
    with st.spinner('Analizando el mercado...'):
        resultados = []
        for t in tickers:
            d = obtener_datos(t)
            if d and d["RSI"] <= rsi_max and d["Dist. al Piso (%)"] <= prox_piso and d["Market Cap (B)"] >= market_cap_min:
                resultados.append(d)
        
        if resultados:
            st.success(f"¡Se encontraron {len(resultados)} oportunidades!")
            st.table(pd.DataFrame(resultados))
        else:
            st.warning("No hay acciones que cumplan los filtros en este momento.")
