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

# --- GUÍA DE PARÁMETROS ---
with st.expander("📖 MANUAL DE INTERPRETACIÓN: RADIOGRAFÍA TÉCNICA Y FUNDAMENTAL"):
    st.markdown("""
    * **MA50/125/200**: Tendencias de corto, mediano y largo plazo. El precio sobre la MA200 indica salud estructural.
    * **RSI (14)**: Momentum de corto plazo. Buscamos niveles cerca de 32 o menos para "Acecho".
    * **MACD**: El cruce sobre la señal indica momentum alcista.
    * **Debt/Equity**: Evalúa apalancamiento. Buscamos estabilidad financiera.
    """)

# --- BARRA LATERAL: PARÁMETROS DE INGENIERÍA ---
st.sidebar.header("⚙️ Parámetros de Ingeniería")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=20)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 400, 150)
rsi_limit = st.sidebar.slider("Filtro RSI (14) Máx", 10, 100, 65)

if st.sidebar.button('🔄 Refrescar Datos'):
    st.cache_data.clear()
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

# --- LISTAS DE ACTIVOS ---
MIS_ACTIVOS_ESTRATEGICOS = [
    "VOO", "SCHD", "VGT", "VXUS", "VUG", "QQQ", "KO", "PEP", "WMT", "PG", 
    "O", "CVX", "JNJ", "MCD", "JPM", "XOM", "V", "ASML", "BHP", "ABBV", 
    "SBUX", "LOW", "AVGO", "NEE", "TXN", "GOOG", "MSFT"
]

@st.cache_data(ttl=86400)
def get_all_tickers():
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        sp500 = pd.read_html(url)[0]['Symbol'].tolist()
        sp500 = [s.replace('.', '-') for s in sp500]
    except:
        sp500 = ["AAPL", "MSFT", "GOOGL"]
    
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
        price_now = last['Close']
        c_bbl = [c for c in hist.columns if c.startswith('BBL')][0]
        
        # Lógica de Alerta (Acecho)
        alerta = (last['RSI_14'] <= 32) or (price_now <= last[c_bbl] * 1.05)
        
        def fmt_ma(val, price):
            icon = "🟢" if price > val else "🔴"
            return f"{icon} ${round(val, 2)}"

        return {
            "Ticker": ticker, "Precio": round(price_now, 2), 
            "RSI(14)": round(last['RSI_14'], 2),
            "MA50": fmt_ma(last['MA50'], price_now),
            "MA125": fmt_ma(last['MA125'], price_now), 
            "MA200": fmt_ma(last['MA200'], price_now),
            "Net Inc(B)": round(info.get('netIncomeToCommon', 0) / 1e9, 2),
            "D/E Ratio(%)": round(info.get('debtToEquity', 0), 2),
            "MACD": round(last['MACD_12_26_9'], 3),
            "Alerta": "🚨 ACECHO" if alerta else "✅ OK",
            "df": hist
        }
    except: return None

# --- BLOQUE 1: ESCANEO DE MERCADO (OPORTUNIDADES) ---
st.header("🚀 Escaneo de Oportunidades (S&P 500 + Especiales)")
all_tickers = get_all_tickers()
data_scanned = []

if st.checkbox("🔍 Iniciar Escaneo Profundo de Mercado"):
    prog = st.progress(0)
    for i, t in enumerate(all_tickers):
        res = fetch_full_data(t)
        if res:
            if (res["RSI(14)"] <= rsi_limit and 
                res["Net Inc(B)"] >= min_net_income and 
                res["D/E Ratio(%)"] <= max_de_ratio):
                data_scanned.append(res)
        prog.progress((i + 1) / len(all_tickers))
    prog.empty()

    if data_scanned:
        df_scanned = pd.DataFrame(data_scanned).drop(columns=['df'])
        st.subheader(f"📋 Resultados del Filtro ({len(data_scanned)} activos)")
        st.dataframe(df_scanned, use_container_width=True)
    else:
        st.info("No se encontraron activos que cumplan los filtros actuales.")

# --- BLOQUE 2: ANÁLISIS GRÁFICO ---
st.divider()
st.header("📊 Análisis Técnico Detallado")
# Combinamos los encontrados en el escaneo con los estratégicos para tener opciones en el selectbox
lista_grafica = sorted(list(set([d["Ticker"] for d in data_scanned] + MIS_ACTIVOS_ESTRATEGICOS)))
seleccion = st.selectbox("Seleccione un activo para inspeccionar:", lista_grafica)

if seleccion:
    # Intentamos obtener de data_scanned o descargamos si es solo de estratégicos
    item = next((i for i in data_scanned if i["Ticker"] == seleccion), fetch_full_data(seleccion))
    if item:
        df_p = item["df"].tail(252)
        last_p = df_p.iloc[-1]
        c_bbu, c_bbl = [c for c in df_p.columns if c.startswith('BBU')][0], [c for c in df_p.columns if c.startswith('BBL')][0]

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.5, 0.2, 0.3])
        fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA50'], line=dict(color='cyan', width=1), name="MA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA125'], line=dict(color='orange', width=1), name="MA125"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red', width=2), name="MA200"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbu], line=dict(color='rgba(255,255,255,0.2)', dash='dot'), name="B.Sup"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbl], line=dict(color='rgba(255,255,255,0.2)', dash='dot'), name="B.Inf"), row=1, col=1)
        
        # Anotaciones
        fig.add_annotation(x=df_p.index[-1], y=last_p['Close'], text=f"PRECIO: ${round(last_p['Close'],2)}", showarrow=True, row=1, col=1)
        
        # RSI y MACD
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_14'], line=dict(color='#C084FC', width=2), name="RSI(14)"), row=2, col=1)
        fig.add_hline(y=32, line_color="orange", line_dash="dash", row=2, col=1)
        
        hist_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
        fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=hist_colors, name="Impulso"), row=3, col=1)
        
        fig.update_layout(height=900, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

# --- BLOQUE 3: MI CARTERA ESTRATÉGICA (PLAN PERSONAL) ---
st.divider()
st.header("🎯 Mi Cartera Estratégica (Vigilancia Permanente)")
cartera_data = []
with st.spinner("Cargando datos de tu plan personal..."):
    for t in MIS_ACTIVOS_ESTRATEGICOS:
        res = fetch_full_data(t)
        if res: cartera_data.append(res)

if cartera_data:
    df_cartera = pd.DataFrame(cartera_data).drop(columns=['df'])
    
    # Aplicación de estilo corregida (.map en lugar de .applymap)
    def style_alerta(val):
        return 'background-color: rgba(255, 75, 75, 0.2)' if val == "🚨 ACECHO" else ''

    st.dataframe(df_cartera.style.map(style_alerta, subset=['Alerta']), use_container_width=True)
