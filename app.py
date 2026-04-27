import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

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

# --- BARRA LATERAL: PARÁMETROS DE INGENIERÍA Y EMAIL ---
st.sidebar.header("⚙️ Parámetros de Ingeniería")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=20)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 400, 150)
rsi_limit = st.sidebar.slider("Filtro RSI (14) Máx", 10, 100, 65)

st.sidebar.divider()
st.sidebar.header("📧 Configuración de Alertas")
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = "tu_correo@ejemplo.com" # Cambiar por el predeterminado

email_input = st.sidebar.text_input("Configurar correo de destino:", value=st.session_state['user_email'])
if st.sidebar.button("💾 Actualizar Correo"):
    st.session_state['user_email'] = email_input
    st.sidebar.success(f"Registrado: {email_input}")

st.sidebar.info(f"📍 Correo actual: \n{st.session_state['user_email']}")

if st.sidebar.button('🔄 Refrescar Datos'):
    st.cache_data.clear()
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

# --- GESTIÓN DE ACTIVOS ---
MIS_ACTIVOS_FIJOS = [
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
        return sorted(list(set(sp500 + MIS_ACTIVOS_FIJOS)))
    except:
        return MIS_ACTIVOS_FIJOS

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
        
        # Lógica de Alerta (RSI <= 32, MACD bajo, o Precio cerca de Banda Inferior)
        alerta_compra = False
        if last['RSI_14'] <= 32 or price_now <= last[c_bbl] * 1.02 or last['MACD_12_26_9'] <= 0.05:
            alerta_compra = True

        def fmt_ma(val, price):
            return f"{'🟢' if price > val else '🔴'} ${round(val, 2)}"

        return {
            "Ticker": ticker, "Precio": round(price_now, 2), "RSI(14)": round(last['RSI_14'], 2),
            "MA50": fmt_ma(last['MA50'], price_now), "MA125": fmt_ma(last['MA125'], price_now),
            "MA200": fmt_ma(last['MA200'], price_now),
            "Net Inc(B)": round(info.get('netIncomeToCommon', 0) / 1e9, 2),
            "D/E Ratio(%)": round(info.get('debtToEquity', 0), 2),
            "MACD": round(last['MACD_12_26_9'], 3), "Señal": round(last['MACDs_12_26_9'], 3),
            "Alerta": "🚨 COMPRA" if alerta_compra else "✅ HOLD",
            "df": hist, "info": info
        }
    except: return None

# --- 1. PRIMERA TABLA: ESCANEO DINÁMICO ---
all_tickers = get_all_tickers()
data_scan = []
if st.checkbox("🚀 Iniciar Escaneo Profundo"):
    prog = st.progress(0)
    for i, t in enumerate(all_tickers):
        res = fetch_full_data(t)
        if res:
            if (res["RSI(14)"] <= rsi_limit and res["Net Inc(B)"] >= min_net_income and res["D/E Ratio(%)"] <= max_de_ratio):
                data_scan.append(res)
        prog.progress((i + 1) / len(all_tickers))
    prog.empty()

if data_scan:
    df_view = pd.DataFrame(data_scan).drop(columns=['df', 'info'])
    st.subheader(f"📋 Resultados del Acecho ({len(data_scan)} activos)")
    st.dataframe(df_view, use_container_width=True)
    
    # --- 2. GRÁFICAS LIGADAS A LA PRIMERA TABLA ---
    seleccion = st.selectbox("🎯 Análisis Técnico Detallado:", df_view["Ticker"].tolist())
    if seleccion:
        item = next(i for i in data_scan if i["Ticker"] == seleccion)
        df_p = item["df"].tail(252)
        last_p = df_p.iloc[-1]
        c_bbu, c_bbl = [c for c in df_p.columns if c.startswith('BBU')][0], [c for c in df_p.columns if c.startswith('BBL')][0]

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.5, 0.2, 0.3])
        fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA50'], line=dict(color='cyan', width=1), name="MA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA125'], line=dict(color='orange', width=1), name="MA125"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red', width=2), name="MA200"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbu], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Sup"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbl], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Inf"), row=1, col=1)

        # Anotaciones escalonadas
        fig.add_annotation(x=df_p.index[-5], y=last_p['Close'], text=f"PRECIO: ${round(last_p['Close'],2)}", showarrow=True, row=1, col=1, font=dict(color="white"), bgcolor="black")
        fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbu], text=f"B.SUP: ${round(last_p[c_bbu],2)}", showarrow=False, xanchor="left", xshift=10, row=1, col=1, font=dict(color="#00d4ff"))
        fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbl], text=f"B.INF: ${round(last_p[c_bbl],2)}", showarrow=False, xanchor="left", xshift=10, row=1, col=1, font=dict(color="#00d4ff"))

        # RSI y MACD
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_14'], line=dict(color='#C084FC', width=2), name="RSI(14)"), row=2, col=1)
        hist_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
        fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=hist_colors, name="Impulso"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'], line=dict(color='#2962ff'), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACDs_12_26_9'], line=dict(color='#ff6d00'), name="Señal"), row=3, col=1)

        fig.update_layout(height=1000, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(r=150))
        st.plotly_chart(fig, use_container_width=True)

# --- 3. SEGUNDA TABLA: MI PLAN ESTRATÉGICO ---
st.divider()
st.header("🎯 Vigilancia de Mi Plan Estratégico")
data_plan = []
alertas_detectadas = []

for t in MIS_ACTIVOS_FIJOS:
    res = fetch_full_data(t)
    if res:
        data_plan.append(res)
        if res["Alerta"] == "🚨 COMPRA":
            alertas_detectadas.append(t)

if data_plan:
    df_plan = pd.DataFrame(data_plan).drop(columns=['df', 'info'])
    
    # Estilizado de la tabla de plan
    def highlight_alerts(val):
        color = 'background-color: rgba(255, 75, 75, 0.3)' if val == "🚨 COMPRA" else ''
        return color

    st.dataframe(df_plan.style.applymap(highlight_alerts, subset=['Alerta']), use_container_width=True)

    if alertas_detectadas:
        st.warning(f"⚠️ Oportunidades de Compra Detectadas en tu Plan: {', '.join(alertas_detectadas)}")
        if st.button("📧 Enviar Informe de Alertas al Correo"):
            # Aquí iría la función de smtplib configurada
            st.info(f"Simulando envío a {st.session_state['user_email']}... Informe enviado con éxito.")
