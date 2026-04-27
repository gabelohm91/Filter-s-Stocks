import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

st.set_page_config(page_title="Terminal Pro - Gabriel Herrera", layout="wide")

if 'last_update' not in st.session_state:
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

st.title("💎 Terminal de Estrategia de Acecho")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Parámetros de Ingeniería")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=50)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 300, 120)
rsi_anual_limit = st.sidebar.slider("Filtro RSI Anual Máx", 10, 70, 45)

if st.sidebar.button('🔄 Refrescar Datos'):
    st.cache_data.clear()
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

# --- GUÍA DE REFERENCIA ---
with st.expander("📖 Manual de Acecho (RSI & Inercia)"):
    st.markdown("""
    ### 📉 Indicadores Clave
    * **RSI Anual (50):** Evalúa la fuerza del precio en el último año. 
        * **Zona < 45:** Indica una empresa con valor pero "olvidada" o castigada por el mercado.
    * **MACD (Inercia):** * **Histograma Verde:** Impulso alcista.
        * **Histograma Rojo:** Impulso bajista (momento de acecho).
    * **Distancia al Suelo (52W Low %):** * **0%:** El precio actual es exactamente el mínimo del año.
    """)

tickers = ["KO", "PEP", "MCD", "JNJ", "DHR", "XOM", "CVX", "PG", "JPM", "MSFT", "AAPL", "TXN", "WMT", "COST", "V", "MA", "SNY", "MCHI"]

@st.cache_data(ttl=3600)
def fetch_full_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y")
        info = stock.info
        hist['RSI_50'] = ta.rsi(hist['Close'], length=50) # RSI Anual
        macd = ta.macd(hist['Close'])
        hist = pd.concat([hist, macd], axis=1)
        last = hist.iloc[-1]
        min_52w = hist['Close'].tail(252).min()
        
        return {
            "Ticker": ticker, "Precio": round(last['Close'], 2),
            "RSI Anual": round(last['RSI_50'], 2),
            "MACD": round(last['MACD_12_26_9'], 3), "Señal": round(last['MACDs_12_26_9'], 3),
            "Net Inc(B)": round(info.get('netIncomeToCommon', 0) / 1e9, 2),
            "D/E Ratio(%)": round(info.get('debtToEquity', 0), 2),
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
    st.subheader(f"📋 Monitor de Oportunidades ({len(data_list)})")
    st.dataframe(pd.DataFrame(data_list).drop(columns=['df']), use_container_width=True)

    st.divider()
    seleccion = st.selectbox("🎯 Radiografía Técnica de Acecho:", [d["Ticker"] for d in data_list])

    if seleccion:
        item = next(i for i in data_list if i["Ticker"] == seleccion)
        df_p = item["df"].tail(252)
        last_p = df_p.iloc[-1]

        # --- NUEVA CONFIGURACIÓN: 2 FILAS (RSI GRANDE + MACD) ---
        fig = make_subplots(rows=2, cols=1, 
                            shared_xaxes=True, 
                            vertical_spacing=0.08,
                            row_heights=[0.6, 0.4],
                            subplot_titles=("ÍNDICE DE FUERZA RELATIVA (RSI ANUAL)", "CONVERGENCIA/DIVERGENCIA (MACD)"))
        
        def add_lab(fig, y, text, color, row, col, offset=0):
            fig.add_annotation(x=df_p.index[-1], y=y, text=text, showarrow=False, xanchor="left",
                               xshift=15, yshift=offset, font=dict(size=14, color=color, family="Arial Black"), 
                               bgcolor="rgba(0,0,0,0.8)", row=row, col=col)

        # 1. RSI ANUAL (FILA 1 - AHORA MÁS GRANDE)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_50'], line=dict(color='#C084FC', width=3), name="RSI Anual"), row=1, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=1, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=1, col=1)
        fig.update_yaxes(range=[0, 100], row=1, col=1)
        add_lab(fig, last_p['RSI_50'], f"<b>RSI(50): {item['RSI Anual']}</b>", "#C084FC", 1, 1)

        # 2. MACD (FILA 2)
        h_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
        fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=h_colors, name="Hist"), row=2, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'], line=dict(color='#2962ff', width=2), name="MACD"), row=2, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACDs_12_26_9'], line=dict(color='#ff6d00', width=2), name="Señal"), row=2, col=1)
        add_lab(fig, last_p['MACD_12_26_9'], f"M: {item['MACD']}", "#2962ff", 2, 1, 15)
        add_lab(fig, last_p['MACDs_12_26_9'], f"S: {item['Señal']}", "#ff6d00", 2, 1, -15)

        fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=True, margin=dict(r=150))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No hay empresas que cumplan los filtros actuales.")
