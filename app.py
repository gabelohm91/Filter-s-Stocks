import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

st.set_page_config(page_title="Terminal Pro - Gabriel Herrera", layout="wide")

if 'last_update' not in st.session_state:
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

st.title("💎 Terminal de Valor y Estrategia de Acecho")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Parámetros de Ingeniería")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=50)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 300, 120)
rsi_anual_limit = st.sidebar.slider("Filtro RSI Anual Máx", 10, 70, 45)

if st.sidebar.button('🔄 Refrescar Datos'):
    st.cache_data.clear()
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

st.sidebar.success(f"✅ Sincronizado: {st.session_state['last_update']}")

# --- GUÍA DE REFERENCIA AMPLIADA ---
with st.expander("📖 Manual de Estrategia y Parámetros"):
    st.markdown("""
    ### 🏗️ Fundamentales
    * **Debt/Equity:** Relación deuda/patrimonio. Buscamos valores < 120%. Si es mayor, la empresa está sobreendeudada.
    * **Net Income:** Solo empresas con ganancias reales (Net Income > 0).

    ### 📉 Indicadores de Acecho
    * **52 Week Price % Change (Distancia al Mínimo):**
        * **0%:** El precio actual es el **mínimo del año**. ¡Escenario de acecho máximo!
        * **0% a 5%:** Excelente oportunidad; compras casi al mismo precio que el suelo anual.
        * *Nota: No puede ser negativo. Si el precio cae más, se convierte en el nuevo 0%.*
    * **Medias Móviles (MA):**
        * **MA200 (Roja):** El soporte más fuerte. Comprar cerca de aquí es históricamente seguro en Blue Chips.
    * **RSI (14) Mensual:**
        * **< 35:** Sobreventa. Indica que el precio está "castigado" y listo para un posible rebote.
    """)

tickers = ["KO", "PEP", "MCD", "JNJ", "DHR", "XOM", "CVX", "PG", "JPM", "MSFT", "AAPL", "TXN", "WMT", "COST", "V", "MA", "SNY", "MCHI"]

@st.cache_data(ttl=3600)
def fetch_full_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y")
        info = stock.info
        hist['MA50'] = ta.sma(hist['Close'], length=50)
        hist['MA125'] = ta.sma(hist['Close'], length=125)
        hist['MA200'] = ta.sma(hist['Close'], length=200)
        hist['RSI_14'] = ta.rsi(hist['Close'], length=14)
        hist['RSI_50'] = ta.rsi(hist['Close'], length=50)
        bb = ta.bbands(hist['Close'], length=20, std=2)
        macd = ta.macd(hist['Close'])
        hist = pd.concat([hist, macd, bb], axis=1)
        last = hist.iloc[-1]
        min_52w = hist['Close'].tail(252).min()
        
        return {
            "Ticker": ticker, "Precio": round(last['Close'], 2),
            "RSI Mens": round(last['RSI_14'], 2), "RSI Anual": round(last['RSI_50'], 2),
            "MA50": round(last['MA50'], 2), "MA125": round(last['MA125'], 2), "MA200": round(last['MA200'], 2),
            "MACD": round(last['MACD_12_26_9'], 3), "Señal": round(last['MACDs_12_26_9'], 3),
            "Net Inc(B)": round(info.get('netIncomeToCommon', 0) / 1e9, 2),
            "D/E Ratio(%)": round(info.get('debtToEquity', 0), 2),
            "Mkt Cap(B)": round(info.get('marketCap', 0) / 1e9, 2),
            "52W Low %": round(((last['Close'] - min_52w) / min_52w) * 100, 2),
            "df": hist
        }
    except: return None

data_list = []
for t in tickers:
    res = fetch_full_data(t)
    if res and res["Mkt Cap(B)"] >= market_cap_min and res["Net Inc(B)"] >= min_net_income and res["D/E Ratio(%)"] <= max_de_ratio and res["RSI Anual"] <= rsi_anual_limit:
        data_list.append(res)

if data_list:
    st.subheader(f"📋 Monitor de Oportunidades ({len(data_list)})")
    st.dataframe(pd.DataFrame(data_list).drop(columns=['df']), use_container_width=True)

    st.divider()
    seleccion = st.selectbox("🎯 Análisis Técnico Detallado:", [d["Ticker"] for d in data_list])

    if seleccion:
        item = next(i for i in data_list if i["Ticker"] == seleccion)
        df_p = item["df"].tail(252)
        last_p = df_p.iloc[-1]
        col_bbu = [c for c in df_p.columns if c.startswith('BBU')][0]
        col_bbl = [c for c in df_p.columns if c.startswith('BBL')][0]

        # --- CONFIGURACIÓN DE SUBPLOTS CON AISLAMIENTO ---
        fig = make_subplots(rows=3, cols=1, 
                            shared_xaxes=True, 
                            vertical_spacing=0.1, # Aumentado para evitar choques
                            row_heights=[0.5, 0.2, 0.3],
                            subplot_titles=("PRECIO Y SOPORTES (MA/BB)", "RSI (TIMING)", "MACD (INERCIA)"))
        
        def add_lab(fig, y, text, color, row, col, offset=0):
            fig.add_annotation(x=df_p.index[-1], y=y, text=text, showarrow=False, xanchor="left",
                               xshift=15, yshift=offset, font=dict(size=14, color=color, family="Arial Black"), 
                               bgcolor="rgba(0,0,0,0.8)", row=row, col=col)

        # 1. PRECIO
        fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA50'], line=dict(color='cyan', width=1), name="MA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA125'], line=dict(color='yellow', width=1), name="MA125"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red', width=2), name="MA200"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[col_bbu], line=dict(color='rgba(173,216,230,0.2)', width=1), name="B.Sup"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[col_bbl], line=dict(color='rgba(173,216,230,0.2)', width=1), fill='tonexty', name="B.Inf"), row=1, col=1)
        add_lab(fig, last_p['Close'], f"<b>${item['Precio']}</b>", "white", 1, 1, 20)
        add_lab(fig, last_p[col_bbu], f"BS: {round(last_p[col_bbu],2)}", "lightblue", 1, 1, 10)
        add_lab(fig, last_p[col_bbl], f"BI: {round(last_p[col_bbl],2)}", "lightblue", 1, 1, -10)

        # 2. RSI (FORZADO A FILA 2)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_14'], line=dict(color='#C084FC', width=2), name="RSI"), row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        # Forzar el rango del eje Y del RSI para que no "herede" el del precio
        fig.update_yaxes(range=[0, 100], row=2, col=1)
        add_lab(fig, last_p['RSI_14'], f"<b>RSI: {item['RSI Mens']}</b>", "#C084FC", 2, 1)

        # 3. MACD (Row 3)
        h_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
        fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=h_colors, name="Hist"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'], line=dict(color='#2962ff', width=2), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACDs_12_26_9'], line=dict(color='#ff6d00', width=2), name="Señal"), row=3, col=1)
        add_lab(fig, last_p['MACD_12_26_9'], f"M: {item['MACD']}", "#2962ff", 3, 1, 15)
        add_lab(fig, last_p['MACDs_12_26_9'], f"S: {item['Señal']}", "#ff6d00", 3, 1, -15)

        fig.update_layout(height=1100, template="plotly_dark", xaxis_rangeslider_visible=True, margin=dict(r=170))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Sin resultados.")
