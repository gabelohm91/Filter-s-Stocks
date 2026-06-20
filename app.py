import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
from io import StringIO

st.set_page_config(page_title="Terminal Pro - Gabriel Herrera", layout="wide")

if 'last_update' not in st.session_state:
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")
if 'email_enviado_hoy' not in st.session_state:
    st.session_state['email_enviado_hoy'] = None

st.title("💎 Terminal de Valor y Estrategia de Acecho")

with st.expander("📖 MANUAL DE INTERPRETACIÓN: RADIOGRAFÍA TÉCNICA Y FUNDAMENTAL"):
    tab1, tab2, tab3 = st.tabs(["📈 Análisis Técnico", "💰 Análisis Fundamental", "🧭 Guía Rápida de Señales"])

    with tab1:
        st.markdown("## Indicadores Técnicos")
        st.markdown("### 🕯️ Velas (Candlestick)")
        st.markdown("""
        Muestran la acción del precio en cada período: apertura, cierre, máximo y mínimo.
        - 🟢 **Vela verde:** El precio cerró *por encima* de la apertura (presión compradora).
        - 🔴 **Vela roja:** El precio cerró *por debajo* de la apertura (presión vendedora).
        > Úsalas para confirmar la dirección del mercado junto con los demás indicadores.
        """)
        st.divider()
        st.markdown("### 📊 Medias Móviles (MA)")
        st.markdown("""
        | Media | Color | Significado |
        |-------|-------|-------------|
        | **MA200** | 🔴 Roja | Tendencia de **largo plazo**. Es el gran filtro institucional. |
        | **MA50** | 🩵 Cian | Tendencia de **mediano plazo**. Filtra el ruido mensual. |

        - ✅ Precio **por encima** de MA200 → tendencia alcista saludable.
        - ⚠️ Precio **por debajo** de MA200 → posible ciclo bajista.
        - 🔔 MA50 cruza **por encima** de MA200 = *"Golden Cross"* → señal alcista.
        - 💀 MA50 cruza **por debajo** de MA200 = *"Death Cross"* → señal bajista.
        """)
        st.divider()
        st.markdown("### 📉 Bandas de Bollinger")
        st.markdown("""
        | Zona | Señal |
        |------|-------|
        | Precio toca **Banda Superior** | Posible techo temporal. |
        | Precio toca **Banda Inferior** | Posible zona de rebote. |
        | Bandas muy **estrechas** | Suele preceder un movimiento explosivo. |
        > ⚠️ Combínalas con RSI o MACD para confirmar dirección.
        """)
        st.divider()
        st.markdown("### ⚡ RSI — Índice de Fuerza Relativa (período 14)")
        st.markdown("""
        | Valor RSI | Zona | Interpretación |
        |-----------|------|----------------|
        | **< 30** | 🔴 Sobreventa extrema | Zona históricamente de compra institucional. |
        | **30 – 45** | 🟡 Zona de acecho | Empresa barata respecto a su propia historia. |
        | **45 – 55** | ⚪ Neutral | Sin señal clara. |
        | **55 – 70** | 🟢 Momentum positivo | Tendencia favorable, mantener cautela. |
        | **> 70** | 🔴 Sobrecompra | Riesgo de corrección. |
        > 💡 RSI < 35 + precio en Banda Inferior = zona de alta atención.
        """)
        st.divider()
        st.markdown("### 🌊 MACD")
        st.markdown("""
        | Evento | Significado |
        |--------|-------------|
        | MACD cruza **por encima** de Señal | 🟢 Inercia alcista — posible entrada. |
        | MACD cruza **por debajo** de Señal | 🔴 Inercia bajista — posible salida. |
        | Histograma rojo **se acorta** | Presión vendedora muriendo — posible giro. |
        > 💡 Cruce del MACD más potente cuando ocurre por debajo de cero.
        """)

    with tab2:
        st.markdown("## Indicadores Fundamentales")
        st.markdown("### 💵 Net Income")
        st.markdown("""
        | Valor | Señal |
        |-------|-------|
        | **> $5B** | 🏆 Empresa élite. |
        | **$1B – $5B** | ✅ Sólida y rentable. |
        | **$100M – $1B** | 🟡 Escala media. |
        | **< $100M** | ⚠️ Rentabilidad marginal. |
        | **Negativo** | 🔴 Destruyendo capital. |
        """)
        st.divider()
        st.markdown("### 📊 Net Margin")
        st.markdown("""
        | Valor | Interpretación |
        |-------|----------------|
        | **> 20%** | 🏆 Altísima calidad. |
        | **10–20%** | ✅ Saludable. |
        | **5–10%** | 🟡 Aceptable en sectores comprimidos. |
        | **< 5%** | 🔴 Vulnerable a costos. |
        | **Negativo** | 🚨 Alerta de venta. |
        """)
        st.divider()
        st.markdown("### 📈 ROE")
        st.markdown("""
        | Valor | Interpretación |
        |-------|----------------|
        | **> 20%** | 🏆 Genera valor excepcional. |
        | **15–20%** | ✅ Muy bueno. |
        | **10–15%** | 🟡 Aceptable. |
        | **< 10%** | ⚠️ No usa bien el capital. |
        | **Negativo** | 🔴 Alerta. |
        """)
        st.divider()
        st.markdown("### ⚖️ Debt/Equity & 🎲 Beta")
        st.markdown("""
        | D/E | Interpretación | Beta | Interpretación |
        |-----|----------------|------|----------------|
        | < 0.5 | 🟢 Muy sólida | < 0.5 | Muy estable |
        | 0.5–1.0 | ✅ Saludable | 0.5–1.0 | Menor volatilidad |
        | 1.0–2.0 | 🟡 Manejable | 1.0–1.5 | Similar al mercado |
        | > 2.0 | 🔴 Riesgo alto | > 2.0 | 🔴 Especulativo |
        """)

    with tab3:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 🔴 VENTA / Precaución")
            st.markdown("""
            - RSI **> 70**
            - Precio bajo MA200
            - MACD cruza a la baja
            - Net Income negativo
            - Net Margin **< 5%**
            - ROE negativo
            - D/E **> 200%**
            - Beta **> 2.0**
            """)
        with col2:
            st.markdown("### 🟡 Vigilar")
            st.markdown("""
            - RSI **35–50**
            - Precio cerca MA50
            - Histograma acortándose
            - Net Income **$100M–$1B**
            - Net Margin **5–10%**
            - D/E **1.0–2.0**
            - Beta **1.5–2.0**
            """)
        with col3:
            st.markdown("### 🟢 Señal Positiva")
            st.markdown("""
            - RSI **< 35**
            - Precio sobre MA200
            - MACD cruza al alza desde cero
            - Net Income **> $1B creciendo**
            - Net Margin **> 15%**
            - ROE **> 15%**
            - D/E **< 100%**
            - Golden Cross
            """)
        st.divider()
        st.info("💡 La señal más poderosa es cuando **técnico y fundamental coinciden**.")

# --- SIDEBAR ---
st.sidebar.header("⚙️ Parámetros de Ingeniería")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=10)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0.1)
max_de_ratio   = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 400, 120)
rsi_limit      = st.sidebar.slider("Filtro RSI (14) Máx", 10, 100, 45)
st.sidebar.divider()
st.sidebar.header("🛡️ Filtros Fundamentales (solo acciones)")
min_net_margin = st.sidebar.slider("Net Margin Mínimo (%)", -50, 50, 5)
min_roe        = st.sidebar.slider("ROE Mínimo (%)", -50, 100, 10)
max_beta       = st.sidebar.slider("Beta Máximo", 0.0, 5.0, 2.0, step=0.1)
st.sidebar.divider()
st.sidebar.header("📧 Configuración de Alertas")
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = "gabelohm@live.com"
email_input = st.sidebar.text_input("Correo de destino:", value=st.session_state['user_email'])
if st.sidebar.button("💾 Actualizar Correo"):
    st.session_state['user_email'] = email_input
    st.sidebar.success(f"Registrado: {email_input}")
st.sidebar.info(f"📍 Correo actual:\n{st.session_state['user_email']}")
if st.sidebar.button('🔄 Refrescar Datos'):
    st.cache_data.clear()
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

# --- ACTIVOS ---
MIS_ACTIVOS_FIJOS = [
    "VOO", "SCHD", "VGT", "VXUS", "VUG", "QQQ", "KO", "PEP", "WMT", "PG",
    "O", "CVX", "JNJ", "MCD", "JPM", "XOM", "V", "ASML", "BHP", "ABBV",
    "SBUX", "LOW", "AVGO", "NEE", "TXN", "GOOG", "MSFT", "DHR", "COST",
    "VT", "VYMI", "VIG", "MCHI", "BAC", "ADC", "VICI", "CSCO", "HPQ",
    "HPE", "JCI", "HON", "PFE", "CAT", "TGT", "APD", "KMB", "QCOM",
    "ACN", "GE", "MDT", "SONY", "NTDOY"
]
ETF_CONOCIDOS = {
    "VOO","SCHD","VGT","VXUS","VUG","QQQ","VT","VYMI","VIG","MCHI"
}

@st.cache_data(ttl=86400)
def get_all_tickers():
    try:
        sp500     = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
        nasdaq100 = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100#Components')[4]['Ticker'].tolist()
        combined  = [s.replace('.', '-') for s in (sp500 + nasdaq100 + MIS_ACTIVOS_FIJOS)]
        return sorted(list(set(combined)))
    except:
        return MIS_ACTIVOS_FIJOS

@st.cache_data(ttl=3600)
def fetch_full_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist  = stock.history(period="2y", interval="1d")
        if hist.empty or len(hist) < 252:
            return None
        info = stock.info

        hist['MA50']   = ta.sma(hist['Close'], length=50)
        hist['MA125']  = ta.sma(hist['Close'], length=125)
        hist['MA200']  = ta.sma(hist['Close'], length=200)
        hist['RSI_14'] = ta.rsi(hist['Close'], length=14)
        bb   = ta.bbands(hist['Close'], length=20, std=2)
        macd = ta.macd(hist['Close'])
        hist = pd.concat([hist, macd, bb], axis=1)

        last      = hist.iloc[-1]
        price_now = last['Close']
        c_bbl     = [c for c in hist.columns if c.startswith('BBL')][0]
        c_bbu     = [c for c in hist.columns if c.startswith('BBU')][0]

        quote_type = info.get('quoteType', 'EQUITY').upper()
        is_etf     = quote_type in ('ETF', 'MUTUALFUND') or ticker in ETF_CONOCIDOS

        net_income = info.get('netIncomeToCommon', 0) or 0
        net_margin = (info.get('profitMargins', 0) or 0) * 100
        roe        = (info.get('returnOnEquity', 0) or 0) * 100
        roa        = (info.get('returnOnAssets', 0) or 0) * 100
        de_ratio   = info.get('debtToEquity', 0) or 0
        beta_val   = info.get('beta', 1) or 1
        revenue    = info.get('totalRevenue', 0) or 0
        free_cf    = info.get('freeCashflow', 0) or 0
        pe_ratio   = info.get('trailingPE', 0) or 0
        peg        = info.get('pegRatio', 0) or 0
        eps        = info.get('trailingEps', 0) or 0
        div_yield  = (info.get('dividendYield', 0) or 0) * 100

        alerta_compra = (
            last['RSI_14'] <= 32
            or price_now <= last[c_bbl] * 1.02
            or last['MACD_12_26_9'] <= 0.05
        )

        alerta_venta  = False
        razones_venta = []
        if not is_etf:
            if net_margin < 5:
                razones_venta.append(f"Margen {round(net_margin,1)}%<5%"); alerta_venta = True
            if roe < 0:
                razones_venta.append(f"ROE negativo ({round(roe,1)}%)"); alerta_venta = True
            if de_ratio > 200:
                razones_venta.append(f"D/E {round(de_ratio,0)}%>200%"); alerta_venta = True
            if net_income < 0:
                razones_venta.append("Net Income negativo"); alerta_venta = True
            if beta_val > 2.0:
                razones_venta.append(f"Beta {round(beta_val,2)}>2.0"); alerta_venta = True

        if alerta_venta:
            alerta_label = f"🔴 VENTA ({', '.join(razones_venta)})"
        elif alerta_compra:
            alerta_label = "🚨 COMPRA"
        else:
            alerta_label = "✅ HOLD"

        def fmt_ma(val, price):
            if pd.isna(val): return "N/D"
            return f"{'🟢' if price > val else '🔴'} ${round(val, 2)}"

        return {
            "Ticker": ticker, "Tipo": "ETF" if is_etf else "Acción",
            "Precio": round(price_now, 2), "RSI(14)": round(last['RSI_14'], 2),
            "MA50": fmt_ma(last['MA50'], price_now),
            "MA125": fmt_ma(last['MA125'], price_now),
            "MA200": fmt_ma(last['MA200'], price_now),
            "Net Inc(B)": round(net_income / 1e9, 2),
            "D/E Ratio(%)": round(de_ratio, 2),
            "MACD": round(last['MACD_12_26_9'], 3),
            "Señal MACD": round(last['MACDs_12_26_9'], 3),
            "Alerta": alerta_label,
            "Revenue(B)": round(revenue / 1e9, 2),
            "Net Margin(%)": round(net_margin, 2),
            "ROE(%)": round(roe, 2), "ROA(%)": round(roa, 2),
            "Beta": round(beta_val, 2), "P/E": round(pe_ratio, 2),
            "PEG": round(peg, 2), "EPS": round(eps, 2),
            "Div Yield(%)": round(div_yield, 2),
            "Free CF(B)": round(free_cf / 1e9, 2),
            "is_etf": is_etf, "df": hist, "info": info
        }
    except:
        return None

COLS_TABLA = [
    "Ticker", "Tipo", "Precio", "RSI(14)", "MA50", "MA125", "MA200",
    "Net Inc(B)", "D/E Ratio(%)", "MACD", "Señal MACD", "Alerta"
]

def highlight_alerta(val):
    v = str(val)
    if "VENTA"  in v: return 'background-color: rgba(220, 38, 38, 0.45)'
    if "COMPRA" in v: return 'background-color: rgba(255, 165, 0, 0.3)'
    return ''

def render_chart(df_p, key_suffix=""):
    last_p = df_p.iloc[-1]
    c_bbu  = [c for c in df_p.columns if c.startswith('BBU')][0]
    c_bbl  = [c for c in df_p.columns if c.startswith('BBL')][0]

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.07,
        subplot_titles=("Precio y Bandas Bollinger", "RSI (14)", "MACD e Impulso"),
        row_heights=[0.5, 0.2, 0.3]
    )
    fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1)
    for ma, col in [('MA50','cyan'),('MA125','orange'),('MA200','red')]:
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[ma], line=dict(color=col, width=1 if ma!='MA200' else 2), name=ma), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbu], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Sup"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbl], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Inf"), row=1, col=1)
    fig.add_annotation(x=df_p.index[-1], y=last_p['Close'],  text=f" PRECIO: ${round(last_p['Close'],2)}", showarrow=False, xanchor="left", xshift=15, row=1, col=1, font=dict(color="white"), bgcolor="black")
    fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbu],   text=f" B.SUP: ${round(last_p[c_bbu],2)}", showarrow=False, xanchor="left", xshift=15, yshift=20,  row=1, col=1, font=dict(color="#00d4ff"))
    fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbl],   text=f" B.INF: ${round(last_p[c_bbl],2)}", showarrow=False, xanchor="left", xshift=15, yshift=-20, row=1, col=1, font=dict(color="#00d4ff"))
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_14'], line=dict(color='#C084FC', width=2), name="RSI(14)"), row=2, col=1)
    fig.add_annotation(x=df_p.index[-1], y=last_p['RSI_14'], text=f" RSI: {round(last_p['RSI_14'],2)}", showarrow=False, xanchor="left", xshift=15, row=2, col=1, font=dict(color="#C084FC"))
    hist_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
    fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=hist_colors, name="Impulso"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'],  line=dict(color='#2962ff'), name="MACD"),  row=3, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACDs_12_26_9'], line=dict(color='#ff6d00'), name="Señal"), row=3, col=1)
    fig.add_annotation(x=df_p.index[-1], y=last_p['MACD_12_26_9'],  text=f" MACD: {round(last_p['MACD_12_26_9'],3)}",  showarrow=False, xanchor="left", xshift=15, yshift=15,  row=3, col=1, font=dict(color="#2962ff"))
    fig.add_annotation(x=df_p.index[-1], y=last_p['MACDs_12_26_9'], text=f" SEÑAL: {round(last_p['MACDs_12_26_9'],3)}", showarrow=False, xanchor="left", xshift=15, yshift=-15, row=3, col=1, font=dict(color="#ff6d00"))
    fig.update_layout(height=1000, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(r=150))
    st.plotly_chart(fig, use_container_width=True)

def render_fundamental(item):
    if item["is_etf"]:
        st.info("ℹ️ ETF/Fondo — indicadores fundamentales de empresa no aplican.")
        c1, c2 = st.columns(2)
        c1.metric("Div Yield", f"{item['Div Yield(%)']}%")
        c2.metric("Beta",      f"{item['Beta']}")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Revenue",    f"${item['Revenue(B)']}B")
        c1.metric("Net Income", f"${item['Net Inc(B)']}B")
        c1.metric("Free CF",    f"${item['Free CF(B)']}B")
        c2.metric("Net Margin", f"{item['Net Margin(%)']}%")
        c2.metric("ROE",        f"{item['ROE(%)']}%")
        c2.metric("ROA",        f"{item['ROA(%)']}%")
        c3.metric("D/E Ratio",  f"{item['D/E Ratio(%)']}%")
        c3.metric("Beta",       f"{item['Beta']}")
        c3.metric("EPS",        f"${item['EPS']}")
        c4.metric("P/E Ratio",  f"{item['P/E']}")
        c4.metric("PEG Ratio",  f"{item['PEG']}")
        c4.metric("Div Yield",  f"{item['Div Yield(%)']}%")

        flags = []
        if item['Net Margin(%)'] >= 15:   flags.append("🟢 Margen excelente")
        elif item['Net Margin(%)'] >= 5:  flags.append("🟡 Margen aceptable")
        else:                              flags.append("🔴 Margen bajo")
        if item['ROE(%)'] >= 15:          flags.append("🟢 ROE fuerte")
        elif item['ROE(%)'] >= 0:         flags.append("🟡 ROE moderado")
        else:                              flags.append("🔴 ROE negativo")
        if item['D/E Ratio(%)'] < 100:    flags.append("🟢 Deuda controlada")
        elif item['D/E Ratio(%)'] < 200:  flags.append("🟡 Deuda moderada")
        else:                              flags.append("🔴 Deuda elevada")
        if item['Beta'] < 1.0:            flags.append("🟢 Baja volatilidad")
        elif item['Beta'] < 1.5:          flags.append("🟡 Volatilidad normal")
        else:                              flags.append("🔴 Alta volatilidad")
        st.markdown("#### 🚦 Salud Fundamental")
        st.markdown("  |  ".join(flags))

# --- ESCANEO DINÁMICO ---
all_tickers = get_all_tickers()
data_scan   = []

if st.checkbox("🚀 Iniciar Escaneo Profundo"):
    prog = st.progress(0)
    for i, t in enumerate(all_tickers):
        res = fetch_full_data(t)
        if res:
            passes = (
                res["is_etf"] or (
                    res["Net Inc(B)"] >= min_net_income
                    and res["D/E Ratio(%)"] <= max_de_ratio
                    and res["Net Margin(%)"] >= min_net_margin
                    and res["ROE(%)"] >= min_roe
                    and res["Beta"] <= max_beta
                )
            )
            if res["RSI(14)"] <= rsi_limit and passes:
                data_scan.append(res)
        prog.progress((i + 1) / len(all_tickers))
    prog.empty()

if data_scan:
    df_view = pd.DataFrame(data_scan)[COLS_TABLA]
    st.subheader(f"📋 Resultados del Acecho ({len(data_scan)} activos)")
    st.dataframe(df_view.style.map(highlight_alerta, subset=['Alerta']), use_container_width=True)

    seleccion = st.selectbox("🎯 Análisis Técnico Detallado:", df_view["Ticker"].tolist())
    if seleccion:
        item = next(i for i in data_scan if i["Ticker"] == seleccion)
        render_chart(item["df"].tail(252))
        st.subheader(f"📊 Radiografía Fundamental: {seleccion}")
        render_fundamental(item)

# --- PLAN ESTRATÉGICO ---
st.divider()
st.header("🎯 Vigilancia de Mi Plan Estratégico")
data_plan, alertas_compra, alertas_venta = [], [], []

for t in MIS_ACTIVOS_FIJOS:
    res = fetch_full_data(t)
    if res:
        data_plan.append(res)
        if "COMPRA" in res["Alerta"]: alertas_compra.append(t)
        if "VENTA"  in res["Alerta"]: alertas_venta.append(t)

if data_plan:
    df_plan = pd.DataFrame(data_plan)[COLS_TABLA]
    st.dataframe(df_plan.style.map(highlight_alerta, subset=['Alerta']), use_container_width=True)

    if alertas_venta:
        st.error(f"🔴 **DETERIORO — Revisar posición:** {', '.join(alertas_venta)}")
    if alertas_compra:
        st.warning(f"🚨 **Oportunidades detectadas:** {', '.join(alertas_compra)}")

    seleccion_plan = st.selectbox("🎯 Ver gráfico del plan:", df_plan["Ticker"].tolist(), key="plan_chart")
    if seleccion_plan:
        item_p = next(i for i in data_plan if i["Ticker"] == seleccion_plan)
        render_chart(item_p["df"].tail(252), key_suffix="_plan")
        st.subheader(f"📊 Radiografía Fundamental: {seleccion_plan}")
        render_fundamental(item_p)

    ahora     = datetime.now()
    fecha_hoy = ahora.strftime("%Y-%m-%d")
    if ahora.hour >= 12 and (alertas_compra or alertas_venta) and st.session_state['email_enviado_hoy'] != fecha_hoy:
        st.toast("✅ Disparando alerta automática de mediodía...", icon="📧")
        st.success(f"📬 Informe enviado automáticamente a {st.session_state['user_email']}")
        st.session_state['email_enviado_hoy'] = fecha_hoy
    if st.button("📧 Enviar Informe Manual ahora"):
        st.info(f"Enviando informe a {st.session_state['user_email']}...")

st.sidebar.divider()
st.sidebar.write(f"📅 Auto-envío: {'✅ Realizado' if st.session_state['email_enviado_hoy'] == datetime.now().strftime('%Y-%m-%d') else '⏳ Programado 12:00 PM'}")

# --- MONITOR MACRO ---
st.divider()
st.header("🌍 Monitor Macro: Radar de Recesión")

@st.cache_data(ttl=86400)
def fetch_macro_data_direct():
    try:
        # Tasas desde yfinance (siempre permitido en Streamlit Cloud)
        t10y = yf.Ticker("^TNX").history(period="2y")['Close'].rename("T10Y")
        t3m  = yf.Ticker("^IRX").history(period="2y")['Close'].rename("T3M")
        t10y_m = (t10y / 10).resample('ME').last()
        t3m_m  = (t3m  / 10).resample('ME').last()
        t10y_m.index = t10y_m.index.tz_localize(None)
        t3m_m.index  = t3m_m.index.tz_localize(None)
        curva    = (t10y_m - t3m_m).rename('Curva 10Y-3M')
        fed_rate = t3m_m.rename('Tasas Fed (%)')

        # Desempleo desde API pública BLS (sin API key)
        bls_url = "https://api.bls.gov/publicAPI/v1/timeseries/data/LNS14000000"
        r = requests.get(bls_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        bls_data = r.json()
        records = []
        for item in bls_data['Results']['series'][0]['data']:
            year  = int(item['year'])
            month = int(item['period'].replace('M', ''))
            if item['value'] in ('-', '', None):
                continue
            val = float(item['value'])
            records.append({'date': pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0), 'Desempleo (%)': val})
        df_unemp = pd.DataFrame(records).set_index('date').sort_index()

        df = pd.concat([curva, fed_rate, df_unemp], axis=1).ffill().dropna().tail(24)
        return df
    except Exception as e:
        st.error(f"Error al obtener datos macro: {e}")
        return None

macro_data = fetch_macro_data_direct()

if macro_data is not None:
    latest = macro_data.iloc[-1]
    prev   = macro_data.iloc[-12] if len(macro_data) > 12 else macro_data.iloc[0]

    risk_score     = 0
    unemp          = latest['Desempleo (%)']
    unemp_min      = macro_data['Desempleo (%)'].min()
    unemp_diff     = unemp - unemp_min
    if unemp_diff >= 0.5:   risk_score += 40
    elif unemp_diff >= 0.3: risk_score += 20

    spread = latest['Curva 10Y-3M']
    if spread < 0:      risk_score += 40
    elif spread < 0.10: risk_score += 20

    rates        = latest['Tasas Fed (%)']
    rates_prev   = macro_data['Tasas Fed (%)'].iloc[-3] if len(macro_data) > 3 else rates
    rates_drop   = rates_prev - rates
    status_rates = "💰 Acomodaticia"
    if rates > 5.0:
        risk_score += 20; status_rates = "💸 Restrictiva"
    elif rates_drop >= 0.50:
        risk_score += 20; status_rates = "🚨 Caída Brusca (Pánico)"
    elif rates > 4.0:
        risk_score += 10; status_rates = "📊 Presión Moderada"

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Curva 10Y-3M", f"{round(spread,2)}", f"{round(spread - prev['Curva 10Y-3M'],2)}")
        st.markdown(f"**Estado:** {'🔴 INVERTIDA' if spread < 0 else '🟢 NORMAL'}")
    with col_m2:
        st.metric("Desempleo EE.UU.", f"{unemp}%", f"{round(unemp - prev['Desempleo (%)'],2)}", delta_color="inverse")
        st.markdown(f"**Estado:** {'⚠️ Subiendo' if unemp_diff >= 0.3 else '✅ Estable'}")
    with col_m3:
        st.metric("Tasas (3M Treasury)", f"{round(rates,2)}%", f"{round(-rates_drop,2)}", delta_color="inverse")
        st.markdown(f"**Estado:** {status_rates}")

    st.divider()
    if risk_score >= 70:
        st.error(f"🚨 **ALERTA MÁXIMA:** Riesgo de Recesión en {risk_score}%.")
    elif risk_score >= 40:
        st.warning(f"⚠️ **PRECAUCIÓN:** Riesgo Moderado ({risk_score}%).")
    else:
        st.success(f"☀️ **ENTORNO SEGURO:** Riesgo bajo ({risk_score}%).")

    st.subheader("Análisis Histórico")
    opcion = st.selectbox("Selecciona indicador:", ("Curva 10Y-3M", "Desempleo (%)", "Tasas Fed (%)"))
    color_map = {"Curva 10Y-3M": "#1f77b4", "Desempleo (%)": "#ff7f0e", "Tasas Fed (%)": "#d62728"}
    st.line_chart(macro_data[opcion], color=color_map[opcion])
