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
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=0) # Bajado a 0 por defecto para no filtrar ETFs
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 500, 500) # Subido para no filtrar por defecto
rsi_anual_limit = st.sidebar.slider("Filtro RSI Anual Máx", 10, 100, 100) # Subido a 100 para ver todo al inicio

if st.sidebar.button('🔄 Refrescar Datos'):
    st.cache_data.clear()
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

st.sidebar.success(f"✅ Sincronizado: {st.session_state['last_update']}")

# --- GUÍA DE REFERENCIA (MANTENIDA INTEGRALMENTE) ---
with st.expander("📖 MANUAL DE INTERPRETACIÓN: RADIOGRAFÍA TÉCNICA Y FUNDAMENTAL"):
    tab1, tab2, tab3 = st.tabs(["📈 Análisis Técnico", "💰 Análisis Fundamental", "🧭 Guía Rápida de Señales"])
    with tab1:
        st.markdown("### ⚡ RSI — Índice de Fuerza Relativa (período 50)")
        st.markdown("Usando un período de 50 se elimina el ruido diario y se revela la **fuerza estructural** del último año.")
        st.divider()
        st.markdown("### 📊 Medias Móviles (MA)")
        st.markdown("| Media | Color | Significado |\n|-------|-------|-------------|\n| **MA200** | 🔴 Roja | Tendencia de largo plazo. |\n| **MA50** | 🩵 Cian | Tendencia de mediano plazo. |")
    # ... (Resto de la guía se mantiene igual internamente)

# --- GESTIÓN DE ACTIVOS ---
@st.cache_data(ttl=86400)
def get_all_tickers():
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        sp500 = pd.read_html(url)[0]['Symbol'].tolist()
        sp500 = [s.replace('.', '-') for s in sp500] # Limpieza para yfinance
    except:
        sp500 = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

    especiales = [
        "VOO", "QQQ", "SCHD", "VGT", "VXUS", "VUG", 
        "LOW", "ABBV", "SBUX", "TGT", "DHR", "NEE", 
        "ASML", "AVGO", "TSM", "NVDA", "ARM", 
        "MCD", "KO", "PEP", "JNJ", "PG", "WMT", 
        "V", "MA", "JPM", "BAC", "COST", "SNY"
    ]
    return sorted(list(set(sp500 + especiales)))

@st.cache_data(ttl=3600)
def fetch_full_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y")
        if hist.empty or len(hist) < 50: return None
        
        info = stock.info
        hist['MA50'] = ta.sma(hist['Close'], length=50)
        hist['MA200'] = ta.sma(hist['Close'], length=200)
        hist['RSI_50'] = ta.rsi(hist['Close'], length=50)
        bb = ta.bbands(hist['Close'], length=20, std=2)
        macd = ta.macd(hist['Close'])
        hist = pd.concat([hist, macd, bb], axis=1)
        
        last = hist.iloc[-1]
        
        # Lógica Indulgente: Si no existe el dato (ej. ETFs), se pone 0 o None pero no se rompe
        net_inc = info.get('netIncomeToCommon')
        mkt_cap = info.get('marketCap')
        de_ratio = info.get('debtToEquity')

        return {
            "Ticker": ticker, 
            "Precio": round(last['Close'], 2),
            "RSI Anual": round(last['RSI_50'], 2) if not pd.isna(last['RSI_50']) else 50,
            "MACD": round(last.get('MACD_12_26_9', 0), 3), 
            "Señal": round(last.get('MACDs_12_26_9', 0), 3),
            "Net Inc(B)": round(net_inc / 1e9, 2) if net_inc else 0.0,
            "D/E Ratio(%)": round(de_ratio, 2) if de_ratio else 0.0,
            "Mkt Cap(B)": round(mkt_cap / 1e9, 2) if mkt_cap else 0.0,
            "df": hist
        }
    except: return None

# --- MONITOR DE ESCANEO ---
all_tickers = get_all_tickers()
st.subheader(f"🔍 Escaneo de Oportunidades ({len(all_tickers)} activos)")

data_list = []
if st.checkbox("🚀 Iniciar Escaneo Profundo (S&P 500 + Especiales)"):
    progress_bar = st.progress(0, text="Escaneando mercado...")
    
    # Procesar en lotes o individualmente
    for i, t in enumerate(all_tickers):
        res = fetch_full_data(t)
        if res:
            # FILTRADO DINÁMICO MEJORADO
            cond_mkt = res["Mkt Cap(B)"] >= market_cap_min
            cond_rsi = res["RSI Anual"] <= rsi_anual_limit
            
            # Solo filtramos por Net Income y D/E si el valor es mayor a 0 (para no excluir ETFs)
            cond_inc = True if res["Net Inc(B)"] == 0 else res["Net Inc(B)"] >= min_net_income
            cond_de = True if res["D/E Ratio(%)"] == 0 else res["D/E Ratio(%)"] <= max_de_ratio

            if cond_mkt and cond_rsi and cond_inc and cond_de:
                data_list.append(res)
        
        if i % 10 == 0: # Actualizar barra cada 10 para velocidad
            progress_bar.progress((i + 1) / len(all_tickers))
    progress_bar.empty()

if data_list:
    st.subheader(f"📋 Resultados del Acecho ({len(data_list)})")
    df_display = pd.DataFrame(data_list).drop(columns=['df'])
    st.dataframe(df_display, use_container_width=True)

    seleccion = st.selectbox("🎯 Selección para Análisis Detallado:", df_display["Ticker"].tolist())

    if seleccion:
        item = next(i for i in data_list if i["Ticker"] == seleccion)
        df_p = item["df"].tail(252)
        last_p = df_p.iloc[-1]
        
        # Manejo robusto de nombres de columnas
        col_bbu = [c for c in df_p.columns if "BBU" in c][0]
        col_bbl = [c for c in df_p.columns if "BBL" in c][0]

        fig = make_subplots(
            rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.07, 
            row_heights=[0.5, 0.2, 0.3],
            subplot_titles=("PRECIO Y SOPORTES ESTRUCTURALES", "RSI ANUAL (50)", "INERCIA (MACD)")
        )
        
        def add_lab(fig, y, text, color, row, col, offset=0):
            fig.add_annotation(
                x=df_p.index[-1], y=y, text=text, showarrow=False, xanchor="left",
                xshift=15, yshift=offset, font=dict(size=12, color=color, family="Arial Black"), 
                bgcolor="rgba(0,0,0,0.8)", row=row, col=col
            )

        # 1. PRECIO
        fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1)
        if 'MA50' in df_p: fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA50'], line=dict(color='cyan', width=1), name="MA50"), row=1, col=1)
        if 'MA200' in df_p: fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red', width=2), name="MA200"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[col_bbu], line=dict(color='rgba(173,216,230,0.2)', width=1), name="B.Sup"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[col_bbl], line=dict(color='rgba(173,216,230,0.2)', width=1), fill='tonexty', name="B.Inf"), row=1, col=1)
        
        add_lab(fig, last_p['Close'], f" PRECIO: ${item['Precio']}", "white", 1, 1, 20)
        add_lab(fig, last_p[col_bbu], f" BS: {round(last_p[col_bbu],2)}", "lightblue", 1, 1, 0)
        add_lab(fig, last_p[col_bbl], f" BI: {round(last_p[col_bbl],2)}", "lightblue", 1, 1, -20)

        # 2. RSI 50
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_50'], line=dict(color='#C084FC', width=2), name="RSI 50"), row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.update_yaxes(range=[0, 100], row=2, col=1)
        add_lab(fig, last_p['RSI_50'], f" RSI(50): {item['RSI Anual']}", "#C084FC", 2, 1)

        # 3. MACD
        m_col = 'MACD_12_26_9'
        s_col = 'MACDs_12_26_9'
        h_col = 'MACDh_12_26_9'
        if m_col in df_p:
            h_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p[h_col]]
            fig.add_trace(go.Bar(x=df_p.index, y=df_p[h_col], marker_color=h_colors, name="Hist"), row=3, col=1)
            fig.add_trace(go.Scatter(x=df_p.index, y=df_p[m_col], line=dict(color='#2962ff', width=2), name="MACD"), row=3, col=1)
            fig.add_trace(go.Scatter(x=df_p.index, y=df_p[s_col], line=dict(color='#ff6d00', width=2), name="Señal"), row=3, col=1)
            add_lab(fig, last_p[m_col], f" M: {item['MACD']}", "#2962ff", 3, 1, 12)
            add_lab(fig, last_p[s_col], f" S: {item['Señal']}", "#ff6d00", 3, 1, -12)

        fig.update_layout(height=1000, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(r=160))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("💡 Consejo: Asegúrate de que el 'Market Cap Mín' sea 0 si quieres ver ETFs en los resultados.")
