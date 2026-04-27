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
rsi_anual_limit = st.sidebar.slider("Filtro RSI Anual Máx", 10, 100, 60)

if st.sidebar.button('🔄 Refrescar Datos'):
    st.cache_data.clear()
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

st.sidebar.success(f"✅ Sincronizado: {st.session_state['last_update']}")

# --- GESTIÓN DE ACTIVOS (DINÁMICA) ---
@st.cache_data(ttl=86400)
def get_all_tickers():
    # 1. Obtener S&P 500 desde Wikipedia
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        sp500 = pd.read_html(url)[0]['Symbol'].tolist()
        sp500 = [s.replace('.', '-') for s in sp500] # Limpieza para yfinance
    except:
        sp500 = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

    # 2. Selección Estratégica de Gabriel
    especiales = [
        "VOO", "SCHD", "VGT", "VXUS", "VUG", "QQQ", # ETFs
        "LOW", "ABBV", "SBUX", "TGT", "DHR", "NEE", # Valor
        "ASML", "AVGO", "TSM", "NVDA", "ARM",       # Tech
        "MCD", "KO", "PEP", "JNJ", "PG", "WMT",     # Consumo
        "V", "MA", "JPM", "BAC", "COST", "SNY", "MCHI"
    ]
    return sorted(list(set(sp500 + especiales)))

@st.cache_data(ttl=3600)
def fetch_full_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y") # Necesitamos 2 años para calcular MA200
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
        
        # Cálculo 52 Week Change %
        price_year_ago = hist.iloc[-252]['Close']
        change_52w = ((price_now - price_year_ago) / price_year_ago) * 100
        
        net_inc = info.get('netIncomeToCommon', 0)
        mkt_cap = info.get('marketCap', 0)
        de_ratio = info.get('debtToEquity', 0)

        return {
            "Ticker": ticker, 
            "Precio": round(price_now, 2),
            "52W Chg %": round(change_52w, 2),
            "RSI(50)": round(last['RSI_50'], 2),
            "MA50": "🟢" if price_now > last['MA50'] else "🔴",
            "MA125": "🟢" if price_now > last['MA125'] else "🔴",
            "MA200": "🟢" if price_now > last['MA200'] else "🔴",
            "Net Inc(B)": round(net_inc / 1e9, 2) if net_inc else 0,
            "D/E Ratio(%)": round(de_ratio, 2) if de_ratio else 0,
            "Mkt Cap(B)": round(mkt_cap / 1e9, 2) if mkt_cap else 0,
            "MACD": round(last['MACD_12_26_9'], 3),
            "df": hist
        }
    except: return None

# --- EJECUCIÓN DEL ESCANEO ---
all_tickers = get_all_tickers()
st.subheader(f"🔍 Escaneo del Mercado ({len(all_tickers)} activos)")

data_list = []
if st.checkbox("🚀 Iniciar Escaneo Profundo"):
    progress_bar = st.progress(0, text="Analizando activos...")
    for i, t in enumerate(all_tickers):
        res = fetch_full_data(t)
        if res:
            # Filtros aplicados
            if (res["Mkt Cap(B)"] >= market_cap_min and 
                res["RSI(50)"] <= rsi_anual_limit and 
                res["Net Inc(B)"] >= min_net_income and 
                res["D/E Ratio(%)"] <= max_de_ratio):
                data_list.append(res)
        progress_bar.progress((i + 1) / len(all_tickers))
    progress_bar.empty()

# --- RESULTADOS Y GRÁFICOS ---
if data_list:
    st.subheader(f"📋 Monitor de Oportunidades ({len(data_list)})")
    df_view = pd.DataFrame(data_list).drop(columns=['df'])
    
    # Mostrar tabla principal
    st.dataframe(df_view, use_container_width=True)

    seleccion = st.selectbox("🎯 Selección para Análisis de Acecho:", df_view["Ticker"].tolist())

    if seleccion:
        item = next(i for i in data_list if i["Ticker"] == seleccion)
        df_p = item["df"].tail(252) # Ver último año en gráfico
        last_p = df_p.iloc[-1]
        
        # Columnas Bollinger dinámicas
        col_bbu = [c for c in df_p.columns if c.startswith('BBU')][0]
        col_bbl = [c for c in df_p.columns if c.startswith('BBL')][0]

        fig = make_subplots(
            rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.07, 
            row_heights=[0.5, 0.2, 0.3],
            subplot_titles=("PRECIO Y MEDIAS ESTRUCTURALES", "RSI ANUAL (50)", "MOMENTUM (MACD)")
        )
        
        # Gráfico 1: Velas + MAs + Bollinger
        fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA50'], line=dict(color='cyan', width=1), name="MA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA125'], line=dict(color='orange', width=1.5), name="MA125"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red', width=2), name="MA200"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[col_bbu], line=dict(color='rgba(173,216,230,0.2)', width=1), name="B.Sup"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[col_bbl], line=dict(color='rgba(173,216,230,0.2)', width=1), fill='tonexty', name="B.Inf"), row=1, col=1)

        # Gráfico 2: RSI
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_50'], line=dict(color='#C084FC', width=2), name="RSI 50"), row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)

        # Gráfico 3: MACD
        h_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
        fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=h_colors, name="Hist"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'], line=dict(color='#2962ff', width=2), name="MACD"), row=3, col=1)

        fig.update_layout(height=900, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Activa el checkbox arriba para escanear oportunidades.")
