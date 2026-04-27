import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

st.set_page_config(page_title="Terminal Pro - Gabriel Herrera", layout="wide")

# Título y Estado
st.title("💎 Terminal de Estrategia de Acecho")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Parámetros de Ingeniería")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=50)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 300, 120)
rsi_anual_limit = st.sidebar.slider("Filtro RSI Anual Máx", 10, 70, 45)

# --- GUÍA DE ESTRATEGIA ---
with st.expander("📖 Manual de Acecho"):
    st.markdown("""
    * **52W Low %:** El objetivo es **0%**. Es cuando el precio "besa" el suelo anual.
    * **RSI Anual (50):** Buscamos que esté en la zona baja (púrpura) mientras los fundamentales sean sólidos.
    """)

tickers = ["KO", "PEP", "MCD", "JNJ", "DHR", "XOM", "CVX", "PG", "JPM", "MSFT", "AAPL", "TXN", "WMT", "COST", "V", "MA", "SNY", "MCHI"]

@st.cache_data(ttl=3600)
def fetch_full_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y")
        info = stock.info
        # Cálculos Técnicos
        hist['MA50'] = ta.sma(hist['Close'], length=50)
        hist['MA200'] = ta.sma(hist['Close'], length=200)
        hist['RSI_50'] = ta.rsi(hist['Close'], length=50)
        macd = ta.macd(hist['Close'])
        bb = ta.bbands(hist['Close'], length=20, std=2)
        hist = pd.concat([hist, macd, bb], axis=1)
        
        last = hist.iloc[-1]
        min_52w = hist['Close'].tail(252).min()
        
        return {
            "Ticker": ticker, "Precio": round(last['Close'], 2),
            "RSI Anual": round(last['RSI_50'], 2),
            "D/E Ratio(%)": round(info.get('debtToEquity', 0), 2),
            "Net Inc(B)": round(info.get('netIncomeToCommon', 0) / 1e9, 2),
            "Mkt Cap(B)": round(info.get('marketCap', 0) / 1e9, 2),
            "52W Low %": round(((last['Close'] - min_52w) / min_52w) * 100, 2),
            "df": hist
        }
    except: return None

data_list = []
for t in tickers:
    res = fetch_full_data(t)
    if res and res["Mkt Cap(B)"] >= market_cap_min and res["Net Inc(B)"] >= min_net_income and res["D/E Ratio(%)"] <= max_de_ratio and res["RSI Anual"] <= rsi_anual_limit:
        data_list.append(res)

if data_list:
    st.subheader(f"📋 Oportunidades Detectadas ({len(data_list)})")
    st.dataframe(pd.DataFrame(data_list).drop(columns=['df']), use_container_width=True)

    st.divider()
    seleccion = st.selectbox("🎯 Análisis Técnico Detallado:", [d["Ticker"] for d in data_list])

    if seleccion:
        item = next(i for i in data_list if i["Ticker"] == seleccion)
        df_p = item["df"].tail(252)
        last_p = df_p.iloc[-1]
        col_bbu = [c for c in df_p.columns if c.startswith('BBU')][0]
        col_bbl = [c for c in df_p.columns if c.startswith('BBL')][0]

        # --- GRÁFICA MAESTRA ---
        # Solo 2 filas: una grande para Precio/RSI y una pequeña para MACD
        fig = make_subplots(rows=2, cols=1, 
                            shared_xaxes=True, 
                            vertical_spacing=0.05,
                            row_heights=[0.7, 0.3],
                            specs=[[{"secondary_y": True}], [{"secondary_y": False}]])

        # 1. TRAZAS DE PRECIO (Eje Y Primario - Izquierda)
        fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red', width=2), name="MA200"), row=1, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[col_bbu], line=dict(color='rgba(173,216,230,0.15)', width=1), name="B.Sup"), row=1, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[col_bbl], line=dict(color='rgba(173,216,230,0.15)', width=1), fill='tonexty', name="B.Inf"), row=1, col=1, secondary_y=False)

        # 2. TRAZA DE RSI (Eje Y Secundario - Derecha)
        # Aquí forzamos que sea SOLAMENTE la línea del RSI
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_50'], line=dict(color='#C084FC', width=3), name="RSI Anual"), row=1, col=1, secondary_y=True)
        
        # Ajuste de escalas para que el RSI aparezca en la parte inferior sin chocar
        fig.update_yaxes(title_text="Precio ($)", secondary_y=False, row=1, col=1)
        fig.update_yaxes(title_text="RSI", range=[-50, 150], secondary_y=True, row=1, col=1, showgrid=False)

        # 3. MACD (Fila 2)
        h_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
        fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=h_colors, name="Hist"), row=2, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'], line=dict(color='#2962ff', width=2), name="MACD"), row=2, col=1)

        # Anotaciones de valor
        fig.add_annotation(x=df_p.index[-1], y=last_p['Close'], text=f"<b>${item['Precio']}</b>", showarrow=False, xshift=40, font=dict(color="white"), bgcolor="black", row=1, col=1)
        fig.add_annotation(x=df_p.index[-1], y=last_p['RSI_50'], text=f"<b>RSI: {item['RSI Anual']}</b>", showarrow=False, xshift=40, font=dict(color="#C084FC"), bgcolor="black", row=1, col=1, secondary_y=True)

        fig.update_layout(height=900, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(r=150))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Ajusta los filtros para encontrar oportunidades.")
