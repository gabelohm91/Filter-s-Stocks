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

# --- BARRA LATERAL: PARÁMETROS E INTERFAZ DE CORREO ---
st.sidebar.header("⚙️ Parámetros de Ingeniería")
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 400, 150)
rsi_limit = st.sidebar.slider("Filtro RSI (14) Máx", 10, 100, 65)

st.sidebar.divider()
st.sidebar.header("📧 Configuración de Alertas")
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = "gabelohm@live.com"

nuevo_email = st.sidebar.text_input("Cambiar correo de destino:", value=st.session_state['user_email'])
if st.sidebar.button("💾 Actualizar Correo"):
    st.session_state['user_email'] = nuevo_email
    st.sidebar.success("Correo actualizado")

st.sidebar.info(f"📍 Correo configurado: \n{st.session_state['user_email']}")

if st.sidebar.button('🔄 Refrescar Datos'):
    st.cache_data.clear()
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

# --- LISTAS Y GESTIÓN DE ACTIVOS ---
# Tu lista fija que siempre debe aparecer en la segunda tabla
MIS_ACTIVOS_PLAN = [
    "VOO", "SCHD", "VGT", "VXUS", "VUG", "QQQ", "KO", "PEP", "WMT", "PG", 
    "O", "CVX", "JNJ", "MCD", "JPM", "XOM", "V", "ASML", "BHP", "ABBV", 
    "SBUX", "LOW", "AVGO", "NEE", "TXN", "GOOG", "MSFT"
]

@st.cache_data(ttl=86400)
def get_market_universe():
    try:
        # S&P 500
        sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
        # NASDAQ 100 (QQQ)
        nasdaq100 = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')[4]['Ticker'].tolist()
        combined = list(set(sp500 + nasdaq100 + MIS_ACTIVOS_PLAN))
        return [s.replace('.', '-') for s in combined]
    except:
        return MIS_ACTIVOS_PLAN

@st.cache_data(ttl=3600)
def fetch_full_analysis(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y", interval="1d")
        if hist.empty or len(hist) < 252: return None
        
        info = stock.info
        hist['MA50'] = ta.sma(hist['Close'], length=50)
        hist['MA125'] = ta.sma(hist['Close'], length=125)
        hist['MA200'] = ta.sma(hist['Close'], length=200)
        hist['RSI_14'] = ta.rsi(hist['Close'], length=14)
        bb = ta.bbands(hist['Close'], length=20, std=2)
        macd = ta.macd(hist['Close'])
        hist = pd.concat([hist, macd, bb], axis=1)
        
        last = hist.iloc[-1]
        price = last['Close']
        c_bbl = [c for c in hist.columns if c.startswith('BBL')][0]
        
        # LÓGICA DE ESTADO (Ajustada para detectar casos como MCD)
        # Acecho si RSI < 32 O si el precio está tocando/cerca de la banda inferior
        if last['RSI_14'] <= 34 or price <= last[c_bbl] * 1.02:
            estado = "🚨 ACECHO / COMPRAR"
        elif last['RSI_14'] >= 70:
            estado = "🚫 NO COMPRAR (CARA)"
        elif last['MACD_12_26_9'] < last['MACDs_12_26_9']:
            estado = "⚠️ VIGILAR (BAJISTA)"
        else:
            estado = "✅ OK"

        def fmt_ma(val, p):
            return f"{'🟢' if p > val else '🔴'} ${round(val, 2)}"

        return {
            "Ticker": ticker, "Precio": round(price, 2), 
            "RSI(14)": round(last['RSI_14'], 2),
            "MA50": fmt_ma(last['MA50'], price),
            "MA125": fmt_ma(last['MA125'], price), 
            "MA200": fmt_ma(last['MA200'], price),
            "Net Inc(B)": round(info.get('netIncomeToCommon', 0) / 1e9, 2),
            "D/E Ratio(%)": round(info.get('debtToEquity', 0), 2),
            "MACD": round(last['MACD_12_26_9'], 3), 
            "Señal": round(last['MACDs_12_26_9'], 3),
            "Estado": estado, "df": hist
        }
    except: return None

# --- TABLA 1: ESCANEO DE MERCADO (S&P 500 + QQQ) ---
st.header("🚀 Escaneo de Oportunidades (S&P 500 & Nasdaq)")
if st.checkbox("🔍 Iniciar Escaneo Profundo"):
    universe = get_market_universe()
    scanned_results = []
    prog = st.progress(0)
    for i, t in enumerate(universe):
        res = fetch_full_analysis(t)
        if res:
            # Filtro Dinámico: Mostramos si cumple criterios de RSI o de Acecho por precio
            if (res["RSI(14)"] <= rsi_limit and res["Net Inc(B)"] >= min_net_income and res["D/E Ratio(%)"] <= max_de_ratio):
                scanned_results.append(res)
        prog.progress((i + 1) / len(universe))
    prog.empty()

    if scanned_results:
        df_scan = pd.DataFrame(scanned_results).drop(columns=['df'])
        st.subheader(f"📋 Resultados del Escaneo ({len(scanned_results)} activos)")
        st.dataframe(df_scan, use_container_width=True)

# --- TABLA 2: MI CARTERA ESTRATÉGICA (SIEMPRE TUS ACCIONES) ---
st.divider()
st.header("🎯 Mi Cartera Estratégica (Vigilancia Permanente)")
plan_data = []
for t in MIS_ACTIVOS_PLAN:
    res = fetch_full_analysis(t)
    if res: plan_data.append(res)

if plan_data:
    df_plan = pd.DataFrame(plan_data).drop(columns=['df'])
    def style_estado(val):
        if "ACECHO" in val: return 'background-color: rgba(255, 75, 75, 0.2)'
        if "VIGILAR" in val: return 'background-color: rgba(255, 165, 0, 0.2)'
        return ''
    st.dataframe(df_plan.style.map(style_estado, subset=['Estado']), use_container_width=True)

# --- GRÁFICA DETALLADA (RESTAURADA CON TODAS LAS ANOTACIONES) ---
st.divider()
st.header("📊 Análisis Técnico Visual")
ticker_plot = st.selectbox("🎯 Ver Gráfica de:", sorted(list(set([d["Ticker"] for d in plan_data]))))
if ticker_plot:
    data = fetch_full_analysis(ticker_plot)
    if data:
        df_p = data["df"].tail(252)
        last_p = df_p.iloc[-1]
        c_bbu, c_bbl = [c for c in df_p.columns if c.startswith('BBU')][0], [c for c in df_p.columns if c.startswith('BBL')][0]

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.5, 0.2, 0.3])
        
        # Precio y Medias
        fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA50'], line=dict(color='cyan', width=1), name="MA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA125'], line=dict(color='orange', width=1), name="MA125"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red', width=2), name="MA200"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbu], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Sup"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbl], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Inf"), row=1, col=1)

        # Anotaciones (Sin traslapes)
        fig.add_annotation(x=df_p.index[-1], y=last_p['Close'], text=f"PRECIO: ${round(last_p['Close'],2)}", showarrow=True, arrowhead=1, row=1, col=1, font=dict(color="white"), bgcolor="black")
        fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbu], text=f"B.SUP: ${round(last_p[c_bbu],2)}", showarrow=False, xanchor="left", xshift=10, row=1, col=1, font=dict(color="#00d4ff"))
        fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbl], text=f"B.INF: ${round(last_p[c_bbl],2)}", showarrow=False, xanchor="left", xshift=10, row=1, col=1, font=dict(color="#00d4ff"))

        # RSI
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_14'], line=dict(color='#C084FC', width=2), name="RSI"), row=2, col=1)
        fig.add_hline(y=30, line_color="green", line_dash="dash", row=2, col=1)
        fig.add_hline(y=70, line_color="red", line_dash="dash", row=2, col=1)
        fig.add_annotation(x=df_p.index[-1], y=last_p['RSI_14'], text=f"RSI: {round(last_p['RSI_14'],2)}", showarrow=False, xanchor="left", xshift=10, row=2, col=1)

        # MACD
        hist_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
        fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=hist_colors, name="Impulso"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'], line=dict(color='#2962ff'), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACDs_12_26_9'], line=dict(color='#ff6d00'), name="Señal"), row=3, col=1)

        fig.update_layout(height=1100, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(r=150))
        st.plotly_chart(fig, use_container_width=True)
