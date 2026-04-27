import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Scanner Pro - Gabriel", layout="wide")

st.title("💎 Terminal de Valor: Gabriel Herrera")
st.sidebar.header("⚙️ Parámetros de Ingeniería Financiera")

# --- FILTROS DINÁMICOS (AJUSTABLES) ---
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=50)
# Filtros de Salud Financiera
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0, step=1)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 300, 120)

# Filtros de Oportunidad (RSI)
rsi_anual_limit = st.sidebar.slider("RSI Anual Máximo (Filtro Tabla)", 10, 70, 45)

# Lista Maestra
tickers = ["KO", "PEP", "MCD", "JNJ", "DHR", "XOM", "CVX", "PG", "JPM", "MSFT", "AAPL", "TXN", "WMT", "COST", "V", "MA", "SNY", "MCHI"]

@st.cache_data(ttl=3600)
def fetch_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        # Traemos 2 años para tener datos suficientes para medias y RSI mensual/anual
        hist = stock.history(period="2y")
        info = stock.info
        
        # --- CÁLCULOS TÉCNICOS ---
        # RSI Mensual (basado en los últimos 20-22 días de trading aprox)
        rsi_series = ta.rsi(hist['Close'], length=14)
        rsi_actual = rsi_series.iloc[-1]
        
        # RSI "Anual" (usamos una ventana más larga para ver la fuerza del año)
        rsi_anual = ta.rsi(hist['Close'], length=50).iloc[-1] 
        
        # 52 Week Calculation
        price_now = hist['Close'].iloc[-1]
        min_52w = hist['Close'].tail(252).min()
        change_52w = ((price_now - min_52w) / min_52w) * 100
        
        return {
            "Ticker": ticker,
            "Precio": round(price_now, 2),
            "RSI Mensual": round(rsi_actual, 2),
            "RSI Anual": round(rsi_anual, 2),
            "Var vs 52W Low (%)": round(change_52w, 2),
            "Net Income (B)": round(info.get('netIncomeToCommon', 0) / 1e9, 2),
            "D/E Ratio (%)": round(info.get('debtToEquity', 0), 2),
            "Market Cap (B)": round(info.get('marketCap', 0) / 1e9, 2),
            "df": hist
        }
    except: return None

# --- EJECUCIÓN ---
data_list = []
for t in tickers:
    res = fetch_data(t)
    if res:
        # APLICACIÓN DE TUS FILTROS AJUSTABLES
        if (res["Market Cap (B)"] >= market_cap_min and 
            res["D/E Ratio (%)"] <= max_de_ratio and 
            res["Net Income (B)"] >= min_net_income and
            res["RSI Anual"] <= rsi_anual_limit):
            data_list.append(res)

if data_list:
    df_display = pd.DataFrame(data_list).drop(columns=['df'])
    st.subheader("📋 Empresas en el Radar")
    st.dataframe(df_display, use_container_width=True)

    # --- GRÁFICO DINÁMICO ---
    st.divider()
    opciones = [d["Ticker"] for d in data_list]
    seleccion = st.selectbox("🎯 Radiografía Técnica de:", opciones)

    if seleccion:
        item = next(i for i in data_list if i["Ticker"] == seleccion)
        df_plot = item["df"].tail(252)
        
        # Indicadores para el gráfico
        bbands = ta.bbands(df_plot['Close'], length=20, std=2)
        ma200 = ta.sma(df_plot['Close'], length=200)
        
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2])
        
        # 1. Velas y MA200
        fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name="Precio"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_plot.index, y=ma200, line=dict(color='orange', width=2), name="MA200"), row=1, col=1)
        
        # Bollinger Dinámico
        col_bbu = [c for c in bbands.columns if c.startswith('BBU')][0]
        col_bbl = [c for c in bbands.columns if c.startswith('BBL')][0]
        fig.add_trace(go.Scatter(x=df_plot.index, y=bbands[col_bbu], line=dict(color='rgba(173,216,230,0.2)'), name="B. Sup"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_plot.index, y=bbands[col_bbl], line=dict(color='rgba(173,216,230,0.2)'), fill='tonexty', name="B. Inf"), row=1, col=1)

        # 2. RSI (El de 14 periodos para el gráfico)
        rsi_plot = ta.rsi(df_plot['Close'], length=14)
        fig.add_trace(go.Scatter(x=df_plot.index, y=rsi_plot, name="RSI (14)", line=dict(color='yellow')), row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)

        # 3. MACD
        macd = ta.macd(df_plot['Close'])
        fig.add_trace(go.Bar(x=df_plot.index, y=macd['MACDh_12_26_9'], name="MACD Hist"), row=3, col=1)

        fig.update_layout(height=750, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Ajustá los filtros para ver resultados. (Sugerencia: Subí el Debt/Equity o el RSI Anual).")
