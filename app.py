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

# --- BARRA LATERAL: PARÁMETROS DE INGENIERÍA ---
st.sidebar.header("⚙️ Parámetros de Ingeniería")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=20)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 400, 150)
rsi_anual_limit = st.sidebar.slider("Filtro RSI Anual Máx", 10, 100, 65)

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
    
    especiales = ["SCHD", "VGT", "VXUS", "VUG", "DHR", "KO", "PEP", "COST", "MCHI", "SNY"]
    return sorted(list(set(sp500 + especiales)))

@st.cache_data(ttl=3600)
def fetch_full_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y")
        if hist.empty or len(hist) < 252: return None
        
        info = stock.info
        
        # Indicadores Técnicos
        hist['MA50'] = ta.sma(hist['Close'], length=50)
        hist['MA125'] = ta.sma(hist['Close'], length=125)
        hist['MA200'] = ta.sma(hist['Close'], length=200)
        hist['RSI_50'] = ta.rsi(hist['Close'], length=50)
        bb = ta.bbands(hist['Close'], length=20, std=2)
        macd = ta.macd(hist['Close'])
        hist = pd.concat([hist, macd, bb], axis=1)
        
        last = hist.iloc[-1]
        price_now = last['Close']
        
        # 52 Week Change %
        price_year_ago = hist.iloc[-252]['Close']
        change_52w = ((price_now - price_year_ago) / price_year_ago) * 100
        
        # Formateo de Medias para Tabla
        def fmt_ma(val, price):
            icon = "🟢" if price > val else "🔴"
            return f"{icon} ${round(val, 2)}"

        return {
            "Ticker": ticker, 
            "Precio": round(price_now, 2),
            "52W Chg %": round(change_52w, 2),
            "RSI(50)": round(last['RSI_50'], 2),
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

# --- ESCANEO ---
all_tickers = get_all_tickers()
data_list = []
if st.checkbox("🚀 Iniciar Escaneo de Oportunidades"):
    prog = st.progress(0)
    for i, t in enumerate(all_tickers):
        res = fetch_full_data(t)
        if res and res["RSI(50)"] <= rsi_anual_limit:
            data_list.append(res)
        prog.progress((i + 1) / len(all_tickers))

if data_list:
    df_view = pd.DataFrame(data_list).drop(columns=['df'])
    st.dataframe(df_view, use_container_width=True)
    
    seleccion = st.selectbox("🎯 Análisis de Acecho:", df_view["Ticker"].tolist())
    
    if seleccion:
        item = next(i for i in data_list if i["Ticker"] == seleccion)
        df_p = item["df"].tail(252)
        last_p = df_p.iloc[-1]
        
        # Dinámica de nombres de columnas Bollinger
        c_bbu = [c for c in df_p.columns if c.startswith('BBU')][0]
        c_bbl = [c for c in df_p.columns if c.startswith('BBL')][0]

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.5, 0.2, 0.3])
        
        # Auxiliar para etiquetas en gráfico
        def add_v_lab(fig, y, text, color, row, offset=0):
            fig.add_annotation(x=df_p.index[-1], y=y, text=text, showarrow=False, xanchor="left", xshift=10, 
                               yshift=offset, font=dict(color=color, size=11), bgcolor="rgba(0,0,0,0.6)", row=row, col=1)

        # 1. PRECIO + MAs + BOLLINGER
        fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA50'], line=dict(color='cyan', width=1), name="MA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red', width=1.5), name="MA200"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbu], line=dict(color='gray', dash='dot'), name="B.Sup"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbl], line=dict(color='gray', dash='dot'), name="B.Inf"), row=1, col=1)
        
        add_v_lab(fig, last_p['Close'], f"Precio: ${round(last_p['Close'],2)}", "white", 1, 20)
        add_v_lab(fig, last_p[c_bbu], f"B.Sup: ${round(last_p[c_bbu],2)}", "gray", 1, 0)
        add_v_lab(fig, last_p[c_bbl], f"B.Inf: ${round(last_p[c_bbl],2)}", "gray", 1, -20)

        # 2. RSI
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_50'], line=dict(color='#C084FC'), name="RSI"), row=2, col=1)
        add_v_lab(fig, last_p['RSI_50'], f"RSI: {round(last_p['RSI_50'],2)}", "#C084FC", 2)
        fig.add_hline(y=30, line_color="green", line_dash="dash", row=2, col=1)
        fig.add_hline(y=70, line_color="red", line_dash="dash", row=2, col=1)

        # 3. MACD + SEÑAL
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'], line=dict(color='#2962ff'), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACDs_12_26_9'], line=dict(color='#ff6d00'), name="Señal"), row=3, col=1)
        add_v_lab(fig, last_p['MACD_12_26_9'], f"MACD: {round(last_p['MACD_12_26_9'],3)}", "#2962ff", 3, 10)
        add_v_lab(fig, last_p['MACDs_12_26_9'], f"Señal: {round(last_p['MACDs_12_26_9'],3)}", "#ff6d00", 3, -10)

        fig.update_layout(height=900, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(r=150))
        st.plotly_chart(fig, use_container_width=True)
