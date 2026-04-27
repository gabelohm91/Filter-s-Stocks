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
    * **MA50/125/200**: Representan tendencias de corto, mediano y largo plazo.
    * **RSI (14)**: Momentum de corto plazo. < 32 se considera zona de acecho (sobreventa).
    * **MACD & Señal**: Cruce alcista indica momentum. Valores cerca de cero sugieren consolidación.
    * **Bandas de Bollinger**: El precio cerca de la banda inferior (-5%) indica soporte potencial.
    """)

# --- BARRA LATERAL: CORREO Y ALERTAS ---
st.sidebar.header("📧 Configuración de Avisos")
# Espacio para indicar y ver el correo registrado
email_input = st.sidebar.text_input("Indicar correo para alertas:", placeholder="tu-correo@ejemplo.com")
if email_input:
    st.sidebar.info(f"Registrado: {email_input}")

st.sidebar.divider()
st.sidebar.header("⚙️ Parámetros de Ingeniería")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=20)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 400, 150)
rsi_limit = st.sidebar.slider("Filtro RSI (14) Máx", 10, 100, 65)

if st.sidebar.button('🔄 Refrescar Datos'):
    st.cache_data.clear()
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

# --- GESTIÓN DE ACTIVOS ---
@st.cache_data(ttl=86400)
def get_sp500_tickers():
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        sp500 = pd.read_html(url)[0]['Symbol'].tolist()
        return [s.replace('.', '-') for s in sp500]
    except:
        return ["AAPL", "MSFT", "GOOGL"]

# Tu lista específica de activos poseídos o deseados
MIS_ACTIVOS_ESTRATEGICOS = [
    "VOO", "SCHD", "VGT", "VXUS", "VUG", "QQQ", "KO", "PEP", "WMT", "PG", 
    "O", "CVX", "JNJ", "MCD", "JPM", "XOM", "V", "ASML", "BHP", "ABBV", 
    "SBUX", "LOW", "AVGO", "NEE", "TXN", "GOOG", "MSFT"
]

@st.cache_data(ttl=3600)
def fetch_full_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y", interval="1d")
        if hist.empty or len(hist) < 252: return None
        
        info = stock.info
        
        # Cálculos Técnicos (Manteniendo MA125 y RSI 14)
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
        val_bbl = last[c_bbl]
        
        # Lógica de Alerta (RSI < 32 o Precio cerca de Banda Inferior 5%)
        cerca_banda_inf = price_now <= (val_bbl * 1.05)
        alerta_acecho = (last['RSI_14'] <= 32) or cerca_banda_inf
        
        def fmt_ma(val, price):
            icon = "🟢" if price > val else "🔴"
            return f"{icon} ${round(val, 2)}"

        return {
            "Ticker": ticker, 
            "Precio": round(price_now, 2), 
            "RSI(14)": round(last['RSI_14'], 2),
            "MACD": round(last['MACD_12_26_9'], 3),
            "MA50": fmt_ma(last['MA50'], price_now),
            "MA125": fmt_ma(last['MA125'], price_now), 
            "MA200": fmt_ma(last['MA200'], price_now),
            "Net Inc(B)": round(info.get('netIncomeToCommon', 0) / 1e9, 2),
            "D/E Ratio(%)": round(info.get('debtToEquity', 0), 2),
            "Alerta": "🚨 ACECHO" if alerta_acecho else "✅ OK",
            "df": hist
        }
    except: return None

# --- SECCIÓN 1: VIGILANCIA DE MI CARTERA ---
st.header("🎯 Mi Cartera Estratégica (Vigilancia Permanente)")
cartera_list = []
with st.spinner("Actualizando mi cartera..."):
    for t in MIS_ACTIVOS_ESTRATEGICOS:
        res = fetch_full_data(t)
        if res: cartera_list.append(res)

if cartera_list:
    df_cartera = pd.DataFrame(cartera_list).drop(columns=['df'])
    # Resaltar filas en zona de acecho
    def highlight_acecho(val):
        color = 'background-color: rgba(255, 75, 75, 0.2)' if val == "🚨 ACECHO" else ''
        return color
    st.dataframe(df_cartera.style.applymap(highlight_acecho, subset=['Alerta']), use_container_width=True)

# --- SECCIÓN 2: ESCANEO DE MERCADO ---
st.divider()
if st.checkbox("🚀 Iniciar Escaneo de Mercado (S&P 500 + Especiales)"):
    all_tickers = sorted(list(set(get_sp500_tickers() + MIS_ACTIVOS_ESTRATEGICOS)))
    data_list = []
    prog = st.progress(0)
    for i, t in enumerate(all_tickers):
        res = fetch_full_data(t)
        if res:
            if (res["RSI(14)"] <= rsi_limit and 
                res["Net Inc(B)"] >= min_net_income and 
                res["D/E Ratio(%)"] <= max_de_ratio):
                data_list.append(res)
        prog.progress((i + 1) / len(all_tickers))
    prog.empty()

    if data_list:
        df_view = pd.DataFrame(data_list).drop(columns=['df'])
        st.subheader(f"📋 Resultados del Filtro ({len(data_list)} activos)")
        st.dataframe(df_view, use_container_width=True)

# --- SECCIÓN 3: GRÁFICAS DETALLADAS ---
st.divider()
todos_disponibles = sorted(list(set([d['Ticker'] for d in cartera_list])))
seleccion = st.selectbox("📊 Ver Gráfica Detallada:", todos_disponibles)

if seleccion:
    item = next(i for i in cartera_list if i["Ticker"] == seleccion)
    df_p = item["df"].tail(252)
    last_p = df_p.iloc[-1]
    
    c_bbu = [c for c in df_p.columns if c.startswith('BBU')][0]
    c_bbl = [c for c in df_p.columns if c.startswith('BBL')][0]

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, 
                       row_heights=[0.5, 0.2, 0.3])
    
    # 1. PRECIO
    fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], 
                                 low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA50'], line=dict(color='cyan', width=1), name="MA50"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA125'], line=dict(color='orange', width=1), name="MA125"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red', width=2), name="MA200"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbu], line=dict(color='rgba(255,255,255,0.2)', dash='dot'), name="B.Sup"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbl], line=dict(color='rgba(255,255,255,0.2)', dash='dot'), name="B.Inf"), row=1, col=1)

    # Anotaciones escalonadas
    fig.add_annotation(x=df_p.index[-5], y=last_p['Close'], text=f"PRECIO: ${round(last_p['Close'],2)}", 
                       showarrow=True, arrowhead=1, row=1, col=1, font=dict(color="white"), bgcolor="black")
    fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbl], text=f"B.INF: ${round(last_p[c_bbl],2)}", 
                       showarrow=False, xanchor="left", xshift=10, row=1, col=1, font=dict(color="#00d4ff"))

    # 2. RSI (14)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_14'], line=dict(color='#C084FC', width=2), name="RSI(14)"), row=2, col=1)
    fig.add_hline(y=32, line_color="orange", line_dash="dash", row=2, col=1)
    fig.add_hline(y=70, line_color="red", line_dash="dash", row=2, col=1)

    # 3. MACD
    hist_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
    fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=hist_colors, name="Impulso"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'], line=dict(color='#2962ff'), name="MACD"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACDs_12_26_9'], line=dict(color='#ff6d00'), name="Señal"), row=3, col=1)

    fig.update_layout(height=1000, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(r=150))
    st.plotly_chart(fig, use_container_width=True)
