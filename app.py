import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Terminal de Valor - Gabriel Herrera", layout="wide")

st.title("💎 Terminal de Valor y Estrategia de Acecho")

# --- SECCIÓN DE AYUDA / REFERENCIAS ---
with st.expander("ℹ️ Guía de Referencia y Valores Clave"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Market Cap (Estabilidad)**")
        st.write("- **+50B:** Empresa estable (Large Cap).")
        st.write("- **+100B:** Muy estable (Mega Cap/Blue Chip).")
        st.write("- **+200B:** Gigantes del mercado (Suelen ser menos volátiles).")
    with col2:
        st.markdown("**Fundamentales (Salud)**")
        st.write("- **Net Income:** Debe ser positivo. Idealmente creciente año tras año.")
        st.write("- **Debt/Equity:** Mide el apalancamiento. Ideal < 100% o 120%. Evitar > 200% en empresas no bancarias.")
    with col3:
        st.markdown("**Técnicos (Timing)**")
        st.write("- **RSI Anual:** < 35 es zona de fuerte acecho (oferta).")
        st.write("- **Cruce MACD:** Cuando la línea azul cruza hacia arriba la naranja, es señal de compra.")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Parámetros de Análisis")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=50)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 300, 120)
rsi_anual_limit = st.sidebar.slider("Filtro RSI Anual Máx", 10, 70, 45)

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
        
        # Datos para tabla
        last = hist.iloc[-1]
        price_now = last['Close']
        min_52w = hist['Close'].tail(252).min()
        
        return {
            "Ticker": ticker,
            "Precio": round(price_now, 2),
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
            "Var 52W Low%": round(((price_now - min_52w) / min_52w) * 100, 2),
            "df": hist
        }
    except: return None

# --- PROCESAMIENTO ---
data_list = []
for t in tickers:
    res = fetch_full_data(t)
    if res and res["Mkt Cap(B)"] >= market_cap_min and res["D/E Ratio(%)"] <= max_de_ratio and res["RSI Anual"] <= rsi_anual_limit:
        data_list.append(res)

if data_list:
    df_tab = pd.DataFrame(data_list).drop(columns=['df'])
    st.subheader("📋 Monitor de Oportunidades")
    st.dataframe(df_tab, use_container_width=True)

    st.divider()
    seleccion = st.selectbox("🎯 Análisis Técnico Detallado:", [d["Ticker"] for d in data_list])

    if seleccion:
        item = next(i for i in data_list if i["Ticker"] == seleccion)
        df_plot = item["df"].tail(252)
        
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5, 0.2, 0.3])
        
        # 1. PRECIO Y MEDIAS (Yahoo Style)
        fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name="Precio"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA50'], line=dict(color='cyan', width=1), name="MA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA125'], line=dict(color='yellow', width=1), name="MA125"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA200'], line=dict(color='red', width=1.5), name="MA200"), row=1, col=1)

        # 2. RSI
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI_14'], line=dict(color='purple'), name="RSI (14)"), row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)

        # 3. MACD COMPLETO (Yahoo Style)
        # Colores dinámicos para el histograma
        hist_colors = ['#26a69a' if val >= 0 else '#ef5350' for val in df_plot['MACDh_12_26_9']]
        
        fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['MACDh_12_26_9'], marker_color=hist_colors, name="Histograma"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MACD_12_26_9'], line=dict(color='#2962ff', width=1.5), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MACDs_12_26_9'], line=dict(color='#ff6d00', width=1.5), name="Señal"), row=3, col=1)

        fig.update_layout(height=850, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Sin resultados. Ajusta los filtros en la barra lateral.")
