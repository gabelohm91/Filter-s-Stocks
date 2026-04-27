import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

st.set_page_config(page_title="Terminal Pro - Gabriel Herrera", layout="wide")

# --- ESTADO DE ACTUALIZACIÓN ---
if 'last_update' not in st.session_state:
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

st.title("💎 Terminal de Valor y Estrategia de Acecho")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Parámetros de Análisis")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=50)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 300, 120)
rsi_anual_limit = st.sidebar.slider("Filtro RSI Anual Máx", 10, 70, 45)

if st.sidebar.button('🔄 Refrescar Datos de Mercado'):
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")
    st.cache_data.clear()

st.sidebar.success(f"✅ Datos Sincronizados: {st.session_state['last_update']}")

# --- GUÍA DE REFERENCIA ---
with st.expander("ℹ️ Guía de Referencia y Valores Clave"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Market Cap (Estabilidad)**")
        st.write("- **+100B:** Muy estable (Blue Chip).")
    with col2:
        st.markdown("**Fundamentales**")
        st.write("- **D/E:** Ideal < 100%. Mide riesgo de deuda.")
    with col3:
        st.markdown("**Técnicos**")
        st.write("- **RSI Anual:** < 35 es zona de fuerte acecho.")

# Lista de Tickers
tickers = ["KO", "PEP", "MCD", "JNJ", "DHR", "XOM", "CVX", "PG", "JPM", "MSFT", "AAPL", "TXN", "WMT", "COST", "V", "MA", "SNY", "MCHI"]

@st.cache_data(ttl=3600)
def fetch_full_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y")
        info = stock.info
        
        # Indicadores
        hist['MA50'] = ta.sma(hist['Close'], length=50)
        hist['MA125'] = ta.sma(hist['Close'], length=125)
        hist['MA200'] = ta.sma(hist['Close'], length=200)
        hist['RSI_14'] = ta.rsi(hist['Close'], length=14)
        hist['RSI_50'] = ta.rsi(hist['Close'], length=50)
        
        macd = ta.macd(hist['Close'])
        hist = pd.concat([hist, macd], axis=1)
        
        last = hist.iloc[-1]
        return {
            "Ticker": ticker,
            "Precio": round(last['Close'], 2),
            "RSI Mens": round(last['RSI_14'], 2),
            "RSI Anual": round(last['RSI_50'], 2),
            "MA50": round(last['MA50'], 2),
            "MA125": round(last['MA125'], 2),
            "MA200": round(last['MA200'], 2),
            "MACD": round(last['MACD_12_26_9'], 3),
            "Señal": round(last['MACDs_12_26_9'], 3),
            "Net Inc(B)": round(info.get('netIncomeToCommon', 0) / 1e9, 2),
            "D/E Ratio(%)": round(info.get('debtToEquity', 0), 2),
            "Mkt Cap(B)": round(info.get('marketCap', 0) / 1e9, 2),
            "Var 52W Low%": round(((last['Close'] - hist['Close'].tail(252).min()) / hist['Close'].tail(252).min()) * 100, 2),
            "df": hist
        }
    except: return None

# Procesamiento
data_list = []
with st.spinner('Actualizando tabla según filtros...'):
    for t in tickers:
        res = fetch_full_data(t)
        if res and res["Mkt Cap(B)"] >= market_cap_min and res["D/E Ratio(%)"] <= max_de_ratio and res["RSI Anual"] <= rsi_anual_limit:
            data_list.append(res)

if data_list:
    st.subheader(f"📋 Monitor de Oportunidades ({len(data_list)} encontradas)")
    st.dataframe(pd.DataFrame(data_list).drop(columns=['df']), use_container_width=True)

    st.divider()
    seleccion = st.selectbox("🎯 Análisis Técnico Detallado:", [d["Ticker"] for d in data_list])

    if seleccion:
        item = next(i for i in data_list if i["Ticker"] == seleccion)
        df_p = item["df"].tail(252)
        last_p = df_p.iloc[-1]
        
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5, 0.2, 0.3])
        
        # 1. PRECIO Y MEDIAS
        fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA50'], line=dict(color='cyan', width=1), name=f"MA50: {item['MA50']}"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA125'], line=dict(color='yellow', width=1), name=f"MA125: {item['MA125']}"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red', width=1.5), name=f"MA200: {item['MA200']}"), row=1, col=1)
        
        # Etiqueta Precio Actual
        fig.add_annotation(x=df_p.index[-1], y=last_p['Close'], text=f"${item['Precio']}", showarrow=True, arrowhead=1, row=1, col=1)

        # 2. RSI
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_14'], line=dict(color='purple'), name=f"RSI: {item['RSI Mens']}"), row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)

        # 3. MACD
        h_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
        fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=h_colors, name="Histograma"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'], line=dict(color='#2962ff', width=1.5), name=f"MACD: {item['MACD']}"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACDs_12_26_9'], line=dict(color='#ff6d00', width=1.5), name=f"Señal: {item['Señal']}"), row=3, col=1)

        fig.update_layout(height=850, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Sin resultados bajo estos filtros.")
