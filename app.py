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
    * **MA50/125/200**: Tendencias de corto, mediano y largo plazo. Precio sobre MA200 = Salud estructural.
    * **RSI (14)**: Momentum. Cerca de 30 = Oportunidad.
    * **MACD & Señal**: Cruce alcista indica momentum de entrada.
    * **Debt/Equity**: Estabilidad financiera (apalancamiento).
    """)

# --- BARRA LATERAL: PARÁMETROS E INTERFAZ DE CORREO ---
st.sidebar.header("⚙️ Parámetros de Ingeniería")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=20)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 400, 150)
rsi_limit = st.sidebar.slider("Filtro RSI (14) Máx", 10, 100, 65)

st.sidebar.divider()
st.sidebar.header("📧 Configuración de Alertas")
# Lógica de actualización de correo
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = "gabriel.herrera@ejemplo.com"

nuevo_email = st.sidebar.text_input("Cambiar correo de destino:", value=st.session_state['user_email'])
if st.sidebar.button("💾 Actualizar Correo"):
    st.session_state['user_email'] = nuevo_email
    st.sidebar.success("Correo actualizado")

st.sidebar.info(f"📍 Correo configurado: \n{st.session_state['user_email']}")

if st.sidebar.button('🔄 Refrescar Datos'):
    st.cache_data.clear()
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

# --- LISTAS Y GESTIÓN DE ACTIVOS ---
MIS_ACTIVOS_PLAN = ["VOO", "SCHD", "VGT", "VXUS", "VUG", "KO", "PEP", "JPM", "PG"]

@st.cache_data(ttl=86400)
def get_all_tickers():
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        sp500 = pd.read_html(url)[0]['Symbol'].tolist()
        sp500 = [s.replace('.', '-') for s in sp500]
    except:
        sp500 = ["AAPL", "MSFT", "GOOGL"]
    especiales = ["SCHD", "VGT", "VXUS", "VUG", "DHR", "KO", "PEP", "COST", "JPM", "V", "PG", "WMT"]
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
        
        # Lógica de Estado (Mix Acecho/Vigilar)
        c_bbl = [c for c in hist.columns if c.startswith('BBL')][0]
        if last['RSI_14'] <= 32 or price_now <= last[c_bbl] * 1.05:
            estado = "🚨 ACECHO / COMPRAR"
        elif last['RSI_14'] >= 70:
            estado = "🚫 NO COMPRAR (ALTO)"
        elif last['MACD_12_26_9'] < last['MACDs_12_26_9']:
            estado = "⚠️ VIGILAR (BAJISTA)"
        else:
            estado = "✅ OK"

        def fmt_ma(val, price):
            return f"{'🟢' if price > val else '🔴'} ${round(val, 2)}"

        return {
            "Ticker": ticker, "Precio": round(price_now, 2), 
            "RSI(14)": round(last['RSI_14'], 2),
            "MA50": fmt_ma(last['MA50'], price_now),
            "MA125": fmt_ma(last['MA125'], price_now), 
            "MA200": fmt_ma(last['MA200'], price_now),
            "Net Inc(B)": round(info.get('netIncomeToCommon', 0) / 1e9, 2),
            "D/E Ratio(%)": round(info.get('debtToEquity', 0), 2),
            "MACD": round(last['MACD_12_26_9'], 3), 
            "Señal": round(last['MACDs_12_26_9'], 3),
            "Estado": estado, "df": hist
        }
    except: return None

# --- BLOQUE 1: ESCANEO DE MERCADO ---
st.header("🚀 Oportunidades del S&P 500 y Nasdaq")
all_tickers = get_all_tickers()
data_list = []
if st.checkbox("🔍 Iniciar Escaneo Profundo"):
    prog = st.progress(0)
    for i, t in enumerate(all_tickers):
        res = fetch_full_data(t)
        if res:
            if (res["RSI(14)"] <= rsi_limit and res["Net Inc(B)"] >= min_net_income and res["D/E Ratio(%)"] <= max_de_ratio):
                data_list.append(res)
        prog.progress((i + 1) / len(all_tickers))
    prog.empty()

if data_list:
    df_view = pd.DataFrame(data_list).drop(columns=['df'])
    st.subheader(f"📋 Posibles Oportunidades ({len(data_list)} activos)")
    st.dataframe(df_view, use_container_width=True)

# --- BLOQUE 2: GRÁFICAS (RESTAURADO SEGÚN CÓDIGO BASE) ---
st.divider()
st.header("📊 Análisis Técnico Detallado")
seleccion = st.selectbox("🎯 Seleccionar Activo para Gráfica:", sorted(list(set([d["Ticker"] for d in data_list] + MIS_ACTIVOS_PLAN))))

if seleccion:
    item = next((i for i in data_list if i["Ticker"] == seleccion), fetch_full_data(seleccion))
    if item:
        df_p = item["df"].tail(252)
        last_p = df_p.iloc[-1]
        c_bbu, c_bbl = [c for c in df_p.columns if c.startswith('BBU')][0], [c for c in df_p.columns if c.startswith('BBL')][0]

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.5, 0.2, 0.3],
                            subplot_titles=(f"Análisis de {seleccion}", "RSI (14)", "MACD & Impulso"))
        
        # 1. Panel Precio
        fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA50'], line=dict(color='cyan', width=1), name="MA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA125'], line=dict(color='orange', width=1), name="MA125"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red', width=2), name="MA200"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbu], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Sup"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbl], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Inf"), row=1, col=1)

        # Anotaciones de Precio y Bandas
        fig.add_annotation(x=df_p.index[-5], y=last_p['Close'], text=f"PRECIO: ${round(last_p['Close'],2)}", showarrow=True, arrowhead=1, row=1, col=1, font=dict(color="white"), bgcolor="black")
        fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbu], text=f"B.SUP: ${round(last_p[c_bbu],2)}", showarrow=False, xanchor="left", xshift=10, row=1, col=1, font=dict(color="#00d4ff", size=12), bgcolor="rgba(0,0,0,0.5)")
        fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbl], text=f"B.INF: ${round(last_p[c_bbl],2)}", showarrow=False, xanchor="left", xshift=10, row=1, col=1, font=dict(color="#00d4ff", size=12), bgcolor="rgba(0,0,0,0.5)")

        # 2. Panel RSI
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_14'], line=dict(color='#C084FC', width=2), name="RSI(14)"), row=2, col=1)
        fig.add_annotation(x=df_p.index[-1], y=last_p['RSI_14'], text=f"RSI(14): {round(last_p['RSI_14'],2)}", showarrow=False, xanchor="left", xshift=10, row=2, col=1, font=dict(color="#C084FC"))
        fig.add_hline(y=30, line_color="green", line_dash="dash", row=2, col=1)
        fig.add_hline(y=70, line_color="red", line_dash="dash", row=2, col=1)

        # 3. Panel MACD
        hist_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
        fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=hist_colors, name="Impulso"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'], line=dict(color='#2962ff'), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACDs_12_26_9'], line=dict(color='#ff6d00'), name="Señal"), row=3, col=1)
        fig.add_annotation(x=df_p.index[-1], y=last_p['MACD_12_26_9'], text=f"MACD: {round(last_p['MACD_12_26_9'],3)}", showarrow=False, xanchor="left", xshift=10, yshift=10, row=3, col=1, font=dict(color="#2962ff"))
        fig.add_annotation(x=df_p.index[-1], y=last_p['MACDs_12_26_9'], text=f"SEÑAL: {round(last_p['MACDs_12_26_9'],3)}", showarrow=False, xanchor="left", xshift=10, yshift=-10, row=3, col=1, font=dict(color="#ff6d00"))

        fig.update_layout(height=1100, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(r=150))
        st.plotly_chart(fig, use_container_width=True)

# --- BLOQUE 3: MI CARTERA (PLAN PERSONAL) ---
st.divider()
st.header("🎯 Mis Acciones (Estrategia y Plan)")
cartera_final = []
for t in MIS_ACTIVOS_PLAN:
    res = fetch_full_data(t)
    if res: cartera_final.append(res)

if cartera_final:
    df_cartera = pd.DataFrame(cartera_final).drop(columns=['df'])
    def style_estado(val):
        if "ACECHO" in val: return 'background-color: rgba(0, 255, 0, 0.1)'
        if "VIGILAR" in val: return 'background-color: rgba(255, 165, 0, 0.1)'
        if "NO COMPRAR" in val: return 'background-color: rgba(255, 0, 0, 0.1)'
        return ''
    
    st.dataframe(df_cartera.style.map(style_estado, subset=['Estado']), use_container_width=True)
