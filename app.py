
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Terminal Pro - Gabriel Herrera", layout="wide")

if 'last_update' not in st.session_state:
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

st.title("💎 Terminal de Valor y Estrategia de Acecho")

# --- GUÍA DE PARÁMETROS (MANTENIDA) ---
with st.expander("📖 MANUAL DE INTERPRETACIÓN: RADIOGRAFÍA TÉCNICA Y FUNDAMENTAL"):
    st.markdown("""
    * **MA50/125/200**: Representan tendencias de corto, mediano y largo plazo. El precio por encima de la MA200 indica salud estructural.
    * **RSI (14)**: Momentum de corto plazo. Buscamos activos en niveles de oportunidad (cerca de 30) o filtrados por debajo de un límite.
    * **MACD & Señal**: El cruce del MACD por encima de la Señal indica un momentum de entrada alcista.
    * **Debt/Equity**: Evalúa el apalancamiento. Idealmente buscamos valores sostenibles para estabilidad financiera.
    """)

# --- BARRA LATERAL: PARÁMETROS DE INGENIERÍA ---
st.sidebar.header("⚙️ Parámetros de Ingeniería")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=20)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 400, 150)
# Ajustado a RSI 14 según tu solicitud
rsi_limit = st.sidebar.slider("Filtro RSI (14) Máx", 10, 100, 65)

if st.sidebar.button('🔄 Refrescar Datos'):
    st.cache_data.clear()
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

# --- GESTIÓN DE ACTIVOS ---
@st.cache_data(ttl=86400)
def get_all_tickers():
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        sp500 = pd.read_html(url)[0]['Symbol'].tolist()
        sp500 = [s.replace('.', '-') for s in sp500]
    except:
        sp500 = ["AAPL", "MSFT", "GOOGL", "VOO", "QQQ"]
    
    especiales = [
        "SCHD", "VGT", "VXUS", "VUG", "DHR", "KO", "PEP", "COST", 
        "MCHI", "SNY", "TXN", "JPM", "V", "MA", "ABBV", "SBUX", 
        "LOW", "AVGO", "NEE", "XOM", "CVX", "PG", "WMT", "JNJ", "MCD"
    ]
    return sorted(list(set(sp500 + especiales)))

@st.cache_data(ttl=3600)
def fetch_full_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        # Intervalo de días como solicitaste
        hist = stock.history(period="2y", interval="1d")
        if hist.empty or len(hist) < 252: return None
        
        info = stock.info
        
        # Cálculos Técnicos (Ajustado a RSI 14)
        hist['MA50'] = ta.sma(hist['Close'], length=50)
        hist['MA125'] = ta.sma(hist['Close'], length=125)
        hist['MA200'] = ta.sma(hist['Close'], length=200)
        hist['RSI_14'] = ta.rsi(hist['Close'], length=14)
        bb = ta.bbands(hist['Close'], length=20, std=2)
        macd = ta.macd(hist['Close'])
        hist = pd.concat([hist, macd, bb], axis=1)
        
        last = hist.iloc[-1]
        price_now = last['Close']
        
        # 52 Week Change %
        price_year_ago = hist.iloc[-252]['Close']
        change_52w = ((price_now - price_year_ago) / price_year_ago) * 100
        
        def fmt_ma(val, price):
            icon = "🟢" if price > val else "🔴"
            return f"{icon} ${round(val, 2)}"

        return {
            "Ticker": ticker, 
            "Precio": round(price_now, 2), 
            "52W Chg %": round(change_52w, 2),
            "RSI(14)": round(last['RSI_14'], 2), # RSI 14 en la tabla
            "MA50": fmt_ma(last['MA50'], price_now),
            "MA125": fmt_ma(last['MA125'], price_now), 
            "MA200": fmt_ma(last['MA200'], price_now),
            "Net Inc(B)": round(info.get('netIncomeToCommon', 0) / 1e9, 2),
            "D/E Ratio(%)": round(info.get('debtToEquity', 0), 2),
            "MACD": round(last['MACD_12_26_9'], 3), 
            "Señal": round(last['MACDs_12_26_9'], 3), 
            "df": hist
        }
    except: return None

# --- EJECUCIÓN DEL ESCANEO ---
all_tickers = get_all_tickers()
data_list = []
if st.checkbox("🚀 Iniciar Escaneo Profundo"):
    prog = st.progress(0)
    for i, t in enumerate(all_tickers):
        res = fetch_full_data(t)
        if res:
            # Filtro por RSI 14
            if (res["RSI(14)"] <= rsi_limit and 
                res["Net Inc(B)"] >= min_net_income and 
                res["D/E Ratio(%)"] <= max_de_ratio):
                data_list.append(res)
        prog.progress((i + 1) / len(all_tickers))
    prog.empty()

# --- VISUALIZACIÓN DE RESULTADOS ---
if data_list:
    df_view = pd.DataFrame(data_list).drop(columns=['df'])
    st.subheader(f"📋 Resultados del Acecho ({len(data_list)} activos)")
    st.dataframe(df_view, use_container_width=True)
    
    seleccion = st.selectbox("🎯 Análisis Técnico Detallado:", df_view["Ticker"].tolist())
    
    if seleccion:
        item = next(i for i in data_list if i["Ticker"] == seleccion)
        df_p = item["df"].tail(252)
        last_p = df_p.iloc[-1]
        
        c_bbu = [c for c in df_p.columns if c.startswith('BBU')][0]
        c_bbl = [c for c in df_p.columns if c.startswith('BBL')][0]

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, 
                           row_heights=[0.5, 0.2, 0.3])
        
        # 1. PANEL PRINCIPAL (Precio, MAs, Bollinger)
        fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], 
                                     low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA50'], line=dict(color='cyan', width=1), name="MA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA125'], line=dict(color='orange', width=1), name="MA125"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red', width=2), name="MA200"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbu], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Sup"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbl], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Inf"), row=1, col=1)

        # ANOTACIONES ESCALONADAS
        fig.add_annotation(x=df_p.index[-5], y=last_p['Close'], text=f"PRECIO: ${round(last_p['Close'],2)}", 
                           showarrow=True, arrowhead=1, row=1, col=1, font=dict(color="white", size=14), bgcolor="black")
        fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbu], text=f"B.SUP: ${round(last_p[c_bbu],2)}", 
                           showarrow=False, xanchor="left", xshift=10, row=1, col=1, font=dict(color="#00d4ff", size=12), bgcolor="rgba(0,0,0,0.5)")
        fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbl], text=f"B.INF: ${round(last_p[c_bbl],2)}", 
                           showarrow=False, xanchor="left", xshift=10, row=1, col=1, font=dict(color="#00d4ff", size=12), bgcolor="rgba(0,0,0,0.5)")

        # 2. PANEL RSI (14) - ACTUALIZADO
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_14'], line=dict(color='#C084FC', width=2), name="RSI(14)"), row=2, col=1)
        fig.add_annotation(x=df_p.index[-1], y=last_p['RSI_14'], text=f"RSI(14): {round(last_p['RSI_14'],2)}", 
                           showarrow=False, xanchor="left", xshift=10, row=2, col=1, font=dict(color="#C084FC", size=12))
        fig.add_hline(y=30, line_color="green", line_dash="dash", row=2, col=1)
        fig.add_hline(y=70, line_color="red", line_dash="dash", row=2, col=1)

        # 3. PANEL MACD (Histograma + Líneas)
        hist_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
        fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=hist_colors, name="Impulso"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'], line=dict(color='#2962ff'), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACDs_12_26_9'], line=dict(color='#ff6d00'), name="Señal"), row=3, col=1)
        
        fig.add_annotation(x=df_p.index[-1], y=last_p['MACD_12_26_9'], text=f"MACD: {round(last_p['MACD_12_26_9'],3)}", 
                           showarrow=False, xanchor="left", xshift=10, yshift=10, row=3, col=1, font=dict(color="#2962ff", size=12))
        fig.add_annotation(x=df_p.index[-1], y=last_p['MACDs_12_26_9'], text=f"SEÑAL: {round(last_p['MACDs_12_26_9'],3)}", 
                           showarrow=False, xanchor="left", xshift=10, yshift=-10, row=3, col=1, font=dict(color="#ff6d00", size=12))

        fig.update_layout(height=1100, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(r=150))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Utiliza el checkbox de arriba para escanear el mercado.")
