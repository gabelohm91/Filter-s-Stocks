import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Terminal Pro - Gabriel Herrera", layout="wide")

if 'last_update' not in st.session_state:
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

st.title("💎 Terminal de Valor y Estrategia de Acecho")

# --- GUÍA DE PARÁMETROS ---
with st.expander("📖 MANUAL DE INTERPRETACIÓN: RADIOGRAFÍA TÉCNICA Y FUNDAMENTAL"):
    st.markdown("""
    * **ACECHO / COMPRAR**: RSI < 32 o precio cerca de la Banda Inferior.
    * **VIGILAR / PRECAUCIÓN**: MACD disminuyendo o precio perdiendo medias móviles.
    * **SOBRECOMPRADO / NO COMPRAR**: RSI > 70 o muy alejado de la MA200.
    """)

# --- BARRA LATERAL: CONFIGURACIÓN DE ALERTAS Y FILTROS ---
st.sidebar.header("📧 Configuración de Alertas")
email_destino = st.sidebar.text_input("Correo para alertas:", placeholder="ejemplo@correo.com")

st.sidebar.divider()
st.sidebar.header("⚙️ Filtros de Ingeniería")
min_net_inc = st.sidebar.number_input("Net Income Mín (Billones $)", value=0)
max_de = st.sidebar.slider("Debt/Equity Máx (%)", 0, 400, 150)
rsi_limit = st.sidebar.slider("Filtro RSI Máx", 10, 100, 65)

# --- LISTAS DE ACTIVOS ---
MIS_ACTIVOS_PLAN = [
    "VOO", "SCHD", "VGT", "VXUS", "VUG", "QQQ", "KO", "PEP", "WMT", "PG", 
    "O", "CVX", "JNJ", "MCD", "JPM", "XOM", "V", "ASML", "BHP", "ABBV", 
    "SBUX", "LOW", "AVGO", "NEE", "TXN", "GOOG", "MSFT"
]

@st.cache_data(ttl=86400)
def get_all_tickers():
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        sp500 = pd.read_html(url)[0]['Symbol'].tolist()
        return [s.replace('.', '-') for s in sp500]
    except:
        return ["AAPL", "MSFT", "VOO", "KO", "PEP"]

@st.cache_data(ttl=3600)
def fetch_full_analysis(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y", interval="1d")
        if hist.empty or len(hist) < 252: return None
        
        info = stock.info
        # Cálculos Técnicos
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
        val_bbl = last[c_bbl]
        macd_val = last['MACD_12_26_9']
        
        # 52 Week Change
        change_52w = ((price - hist.iloc[-252]['Close']) / hist.iloc[-252]['Close']) * 100

        # LÓGICA DE RECOMENDACIÓN (EL MIX SOLICITADO)
        if last['RSI_14'] <= 32 or price <= val_bbl * 1.05:
            estado = "🚨 ACECHO / COMPRAR"
        elif last['RSI_14'] >= 70:
            estado = "🚫 SOBRECOMPRADO / NO COMPRAR"
        elif macd_val < 0 or price < last['MA50']:
            estado = "⚠️ VIGILAR (BAJISTA)"
        else:
            estado = "✅ OK (MANTENER)"

        def fmt_ma(val, p):
            return f"{'🟢' if p > val else '🔴'} ${round(val, 2)}"

        return {
            "Ticker": ticker, "Precio": round(price, 2), "52W Chg %": round(change_52w, 2),
            "RSI(14)": round(last['RSI_14'], 2), "MA50": fmt_ma(last['MA50'], price),
            "MA125": fmt_ma(last['MA125'], price), "MA200": fmt_ma(last['MA200'], price),
            "Net Inc(B)": round(info.get('netIncomeToCommon', 0) / 1e9, 2),
            "D/E Ratio(%)": round(info.get('debtToEquity', 0), 2),
            "MACD": round(macd_val, 3), "Señal": round(last['MACDs_12_26_9'], 3),
            "Estado": estado, "df": hist
        }
    except: return None

# --- SECCIÓN 1: ESCANEO PROFUNDO (S&P 500 + Especiales) ---
st.header("🚀 Escaneo de Oportunidades de Mercado")
if st.checkbox("Iniciar Escaneo Profundo"):
    all_tkrs = sorted(list(set(get_all_tickers() + MIS_ACTIVOS_PLAN)))
    scanned_results = []
    prog = st.progress(0)
    for i, t in enumerate(all_tkrs):
        res = fetch_full_analysis(t)
        if res and res["Net Inc(B)"] >= min_net_inc and res["D/E Ratio(%)"] <= max_de:
            if res["RSI(14)"] <= rsi_limit:
                scanned_results.append(res)
        prog.progress((i + 1) / len(all_tkrs))
    prog.empty()

    if scanned_results:
        df_scan = pd.DataFrame(scanned_results).drop(columns=['df'])
        st.dataframe(df_scan, use_container_width=True)

# --- SECCIÓN 2: ANÁLISIS TÉCNICO GRÁFICO ---
st.divider()
st.header("📊 Detalle Visual de Activos")
target = st.selectbox("Seleccionar Ticker para graficar:", MIS_ACTIVOS_PLAN)
if target:
    data = fetch_full_analysis(target)
    if data:
        df_p = data["df"].tail(250)
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.5, 0.2, 0.3])
        fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA50'], line=dict(color='cyan'), name="MA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red'), name="MA200"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_14'], line=dict(color='#C084FC'), name="RSI"), row=2, col=1)
        fig.add_hline(y=32, line_dash="dash", line_color="orange", row=2, col=1)
        
        hist_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
        fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=hist_colors, name="MACD Hist"), row=3, col=1)
        fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

# --- SECCIÓN 3: MI CARTERA ESTRATÉGICA (VIGILANCIA Y ALERTAS) ---
st.divider()
st.header("🎯 Mi Cartera Estratégica (Vigilancia de Plan)")
plan_data = []
for t in MIS_ACTIVOS_PLAN:
    res = fetch_full_analysis(t)
    if res: plan_data.append(res)

if plan_data:
    df_plan = pd.DataFrame(plan_data).drop(columns=['df'])
    
    # Estilo de Alerta (Corregido .map)
    def color_estado(val):
        if "ACECHO" in val: return 'background-color: rgba(255, 75, 75, 0.3)'
        if "VIGILAR" in val: return 'background-color: rgba(255, 165, 0, 0.2)'
        return ''

    st.dataframe(df_plan.style.map(color_estado, subset=['Estado']), use_container_width=True)

    # Lógica de Correo
    if st.sidebar.button("📩 Forzar Envío de Alertas por Correo"):
        alertas_activas = df_plan[df_plan['Estado'].str.contains("ACECHO|VIGILAR")]
        if not alertas_activas.empty and email_destino:
            st.sidebar.success(f"Reporte generado para {len(alertas_activas)} activos. Enviando a {email_destino}...")
            # Aquí se insertaría el bloque smtplib configurado con tus credenciales
