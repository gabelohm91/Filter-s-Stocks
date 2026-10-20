import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests
from io import StringIO
 
st.set_page_config(page_title="Terminal Pro - Gabriel Herrera", layout="wide")
 
if 'last_update' not in st.session_state:
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")
 
st.title("💎 Terminal de Valor y Estrategia de Acecho")
 
with st.expander("📖 MANUAL DE INTERPRETACIÓN: RADIOGRAFÍA TÉCNICA Y FUNDAMENTAL"):
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Análisis Técnico", "💰 Análisis Fundamental", "🧭 Guía Rápida de Señales", "🌍 Contexto Macro"])
 
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
        | **< 30** | 🔴 Sobreventa | Fuerte presión vendedora reciente. No implica que haya tocado fondo. |
        | **30 – 45** | 🟡 Zona de acecho | Caída reciente notable. No mide si la empresa está barata. |
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
        | **Negativo** | 🚨 Revisar fundamentos. |
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
        st.markdown("### ⚖️ Debt/Equity (%) & 🎲 Beta")
        st.markdown("""
        | D/E (%) | Interpretación | Beta | Interpretación |
        |---------|----------------|------|----------------|
        | < 50% | 🟢 Muy sólida | < 0.5 | Muy estable |
        | 50–100% | ✅ Saludable | 0.5–1.0 | Menor volatilidad |
        | 100–200% | 🟡 Manejable | 1.0–1.5 | Similar al mercado |
        | > 200% | 🔴 Riesgo alto | > 2.0 | 🔴 Especulativo |
        """)
        st.divider()
        st.markdown("### 💸 FCF Yield & Deuda Neta/EBITDA")
        st.markdown("""
        - **FCF Yield** = Flujo de caja libre / Market Cap. Cuánto efectivo libre genera la empresa por cada $100 pagados por ella. Más alto = más barata en términos de caja.
        - **Deuda Neta/EBITDA** = (Deuda total − Efectivo) / EBITDA. Años de EBITDA necesarios para pagar la deuda. Negativo = más efectivo que deuda. Comparar solo dentro del mismo sector.
        """)
 
    with tab3:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 🔴 REVISAR / Precaución")
            st.markdown("""
            - RSI **> 70**
            - Precio bajo MA200
            - MACD cruza a la baja
            - Net Income negativo
            - FCF negativo
            - Net Margin **negativo**
            - ROE negativo
            - D/E **> 200%**
            """)
        with col2:
            st.markdown("### 🟡 Vigilar")
            st.markdown("""
            - RSI **35–50**
            - Precio cerca MA50
            - Histograma acortándose
            - Net Income **$100M–$1B**
            - Net Margin **5–10%**
            - D/E **100–200%**
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
        st.info("💡 La señal más poderosa es cuando **técnico y fundamental coinciden**. "
                "La alerta COMPRA exige zona de precio (RSI bajo o banda inferior) **y** confirmación de impulso MACD.")
 
    with tab4:
        st.markdown("## 🌍 Indicadores Macroeconómicos")
 
        st.markdown("### 📉 Curva 10Y-3M (Spread de Tasas)")
        st.markdown("""
        Mide la diferencia entre el rendimiento del Bono del Tesoro a 10 años y la Letra del Tesoro a 3 meses.
        Es el indicador oficial usado por el **Banco de la Reserva Federal de Nueva York** en su modelo de probabilidad de recesión — más fiable históricamente que el spread 10Y-2Y.
 
        | Valor | Interpretación |
        |-------|----------------|
        | **> 0.5%** | 🟢 Curva normal. Crecimiento saludable esperado. |
        | **0.10% – 0.5%** | 🟡 Aplanamiento. Empieza a descontarse menor crecimiento. |
        | **0% – 0.10%** | 🟠 Zona de alerta. Inversión inminente. |
        | **< 0%** | 🔴 **Curva invertida.** El mercado espera que la Fed recorte tasas porque anticipa desaceleración. |
 
        **Cómo leerla en el tiempo (lo más importante):**
        - 🔻 **Cruce a negativo:** Señal de alerta temprana. Históricamente precede una recesión entre **6 y 18 meses** después — no es inmediato.
        - 🔺 **Rebote de negativo a positivo ("un-inversión"):** ⚠️ Contraintuitivo — esto **no significa que el peligro pasó**. Suele coincidir con el inicio real de la recesión, porque ocurre cuando la Fed empieza a recortar tasas agresivamente ante un deterioro económico que ya está en marcha. Este es históricamente uno de los mejores momentos para *comprar* activos de calidad a precios deprimidos, no para confiarse.
        - 📊 La curva mide *probabilidad* de recesión, no su severidad ni duración.
        """)
 
        st.divider()
 
        st.markdown("### 👷 Desempleo (Tasa de Desempleo EE.UU.)")
        st.markdown("""
        Mide el porcentaje de la fuerza laboral sin trabajo. Es un indicador **rezagado**: sube *después* de que la economía ya se debilitó, no antes.
 
        Se calcula de forma aproximada a la **Regla de Sahm**: promedio móvil de 3 meses del desempleo, comparado con el mínimo de ese promedio en los 12 meses previos.
 
        | Comportamiento | Interpretación |
        |-----------------|----------------|
        | **Estable o bajando** | ✅ Mercado laboral fuerte. Consumo sostenido. |
        | **Sube +0.3 puntos** | 🟡 Primeras señales de debilitamiento. |
        | **Sube +0.5 puntos** | 🔴 Señal de Sahm activada (recesión probablemente en curso). |
 
        > 💡 El desempleo no predice la recesión — la **confirma**.
        """)
 
        st.divider()
 
        st.markdown("### 💰 Tasas Fed (proxy: Letra del Tesoro a 3 meses)")
        st.markdown("""
        Refleja de cerca la tasa de referencia actual de la Reserva Federal (Fed Funds Rate).
 
        | Estado | Interpretación |
        |--------|----------------|
        | **💰 Acomodaticia (< 4%)** | Política expansiva. Favorece el crecimiento y los activos de riesgo. |
        | **📊 Presión Moderada (4% – 5%)** | Política neutral a restrictiva. Encarece el crédito gradualmente. |
        | **💸 Restrictiva (> 5%)** | Política dura. Busca enfriar la inflación, puede frenar el crecimiento. |
        | **🚨 Caída Brusca (Pánico)** | Recorte de +0.50% en pocos meses. Generalmente reacción a un deterioro económico repentino, no buena noticia per se. |
 
        > ⚠️ Una caída rápida de tasas no siempre es alcista para acciones — a menudo significa que la Fed está respondiendo a una crisis ya en marcha.
        """)
 
        st.divider()
        st.info("💡 **Síntesis:** Curva invertida = alerta temprana. Desempleo subiendo = confirmación. Tasas cayendo de golpe = la Fed ya está reaccionando a un problema real. "
                "Los tres juntos dan un **índice interno de 0 a 100**. No es una probabilidad estadística de recesión.")
 
# --- SIDEBAR ---
st.sidebar.header("⚙️ Parámetros de Ingeniería")
market_cap_min = st.sidebar.number_input("Market Cap Mín (miles de millones $)", value=10)
min_net_income = st.sidebar.number_input("Net Income Mínimo (miles de millones $)", value=0.1)
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
    try:
        st.session_state['user_email'] = st.secrets.get("ALERT_EMAIL", "")
    except Exception:
        st.session_state['user_email'] = ""
email_input = st.sidebar.text_input("Correo de destino:", value=st.session_state['user_email'])
if st.sidebar.button("💾 Actualizar Correo"):
    st.session_state['user_email'] = email_input
    st.sidebar.success(f"Registrado: {email_input}")
st.sidebar.info(f"📍 Correo actual:\n{st.session_state['user_email'] or '(sin configurar)'}")
if st.sidebar.button('🔄 Refrescar Datos'):
    st.cache_data.clear()
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")
st.sidebar.caption(f"Última actualización: {st.session_state['last_update']}")
 
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
    "VOO", "SCHD", "VGT", "VXUS", "VUG", "QQQ", "VT", "VYMI", "VIG", "MCHI"
}
 
# Fuentes oficiales de componentes (sin Wikipedia)
URL_NASDAQ100 = "https://api.nasdaq.com/api/quote/list-type/nasdaq100"
URL_SP500_IVV = ("https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/"
                 "1467271812596.ajax?fileType=csv&fileName=IVV_holdings&dataType=fund")
HEADERS_WEB = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json, text/csv, */*'}
CORRECCIONES_TICKER = {"BRKB": "BRK-B", "BFB": "BF-B"}
 
 
def _normalizar_ticker(s):
    s = str(s).strip().upper()
    s = CORRECCIONES_TICKER.get(s, s)
    return s.replace('.', '-')
 
 
def _tickers_nasdaq100():
    r = requests.get(URL_NASDAQ100, headers=HEADERS_WEB, timeout=15)
    r.raise_for_status()
    rows = r.json()['data']['data']['rows']
    return [_normalizar_ticker(x['symbol']) for x in rows if x.get('symbol')]
 
 
def _tickers_sp500():
    r = requests.get(URL_SP500_IVV, headers=HEADERS_WEB, timeout=20)
    r.raise_for_status()
    lineas = [l.lstrip('\ufeff') for l in r.text.splitlines()]
    inicio = next((i for i, l in enumerate(lineas)
                   if l.replace('"', '').startswith("Ticker,")), None)
    if inicio is None:
        raise ValueError(f"Encabezado no encontrado. Primeras líneas: {lineas[:12]}")
    df = pd.read_csv(StringIO("\n".join(lineas[inicio:])))
    df = df[df['Asset Class'] == 'Equity']
    return [_normalizar_ticker(t) for t in df['Ticker'].dropna().tolist()
            if str(t).strip() not in ('-', '')]
 
 
@st.cache_data(ttl=86400)
def get_all_tickers():
    """Devuelve (lista_de_tickers, mensaje_de_estado)."""
    fuentes_ok, fallos = [], []
    tickers = list(MIS_ACTIVOS_FIJOS)
    for nombre, fn in (("S&P 500 (iShares)", _tickers_sp500), ("Nasdaq-100 (Nasdaq)", _tickers_nasdaq100)):
        try:
            tickers += fn()
            fuentes_ok.append(nombre)
        except Exception as e:
            fallos.append(f"{nombre}: {e}")
    tickers = sorted(set(_normalizar_ticker(t) for t in tickers))
    msg = ""
    if fallos:
        msg = "No se pudo cargar: " + " | ".join(fallos) + ". Se usan solo los activos disponibles."
    return tickers, msg
 
 
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
        prev      = hist.iloc[-2]
        price_now = last['Close']
        c_bbl     = [c for c in hist.columns if c.startswith('BBL')][0]
 
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
        fwd_pe     = info.get('forwardPE', 0) or 0
        peg        = info.get('pegRatio', 0) or 0
        eps        = info.get('trailingEps', 0) or 0
        div_yield  = (info.get('dividendYield', 0) or 0) * 100
        market_cap = info.get('marketCap', 0) or 0
        total_debt = info.get('totalDebt')
        total_cash = info.get('totalCash')
        ebitda     = info.get('ebitda')
 
        # --- Métricas derivadas (None si no hay datos) ---
        fcf_yield = (free_cf / market_cap * 100) if market_cap > 0 and free_cf else None
        nd_ebitda = None
        if total_debt is not None and total_cash is not None and ebitda and ebitda > 0:
            nd_ebitda = (total_debt - total_cash) / ebitda
 
        # --- Alerta de compra: zona de precio Y confirmación de impulso ---
        rsi_bajo        = last['RSI_14'] <= 32
        cerca_bbl       = price_now <= last[c_bbl] * 1.02
        macd_cruce_alza = (prev['MACD_12_26_9'] <= prev['MACDs_12_26_9']
                           and last['MACD_12_26_9'] > last['MACDs_12_26_9'])
        hist_mejora     = last['MACDh_12_26_9'] > prev['MACDh_12_26_9']
        alerta_compra   = (rsi_bajo or cerca_bbl) and (macd_cruce_alza or hist_mejora)
 
        # --- Alerta de revisión fundamental (varias señales, no una sola) ---
        puntos_rojos  = 0
        razones_venta = []
        if not is_etf:
            if net_income < 0:
                puntos_rojos += 2; razones_venta.append("Net Income negativo")
            if free_cf < 0:
                puntos_rojos += 2; razones_venta.append("FCF negativo")
            if net_margin < 0:
                puntos_rojos += 2; razones_venta.append(f"Margen {round(net_margin,1)}%")
            if roe < 0:
                puntos_rojos += 1; razones_venta.append(f"ROE {round(roe,1)}%")
            if de_ratio > 200:
                puntos_rojos += 1; razones_venta.append(f"D/E {round(de_ratio,0)}%")
        alerta_venta = puntos_rojos >= 3
 
        if alerta_venta:
            alerta_label = f"🔴 REVISAR ({', '.join(razones_venta)})"
        elif alerta_compra:
            alerta_label = "🚨 COMPRA"
        else:
            alerta_label = "✅ HOLD"
 
        def fmt_ma(val, price):
            if pd.isna(val): return "N/D"
            return f"{'🟢' if price > val else '🔴'} ${round(val, 2)}"
 
        return {
            "Ticker": ticker, "Tipo": "ETF" if is_etf else "Acción",
            "Market Cap(B)": round(market_cap / 1e9, 2),
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
            "Fwd P/E": round(fwd_pe, 2),
            "PEG": round(peg, 2), "EPS": round(eps, 2),
            "Div Yield(%)": round(div_yield, 2),
            "Free CF(B)": round(free_cf / 1e9, 2),
            "FCF Yield(%)": None if fcf_yield is None else round(fcf_yield, 2),
            "NetDebt/EBITDA": None if nd_ebitda is None else round(nd_ebitda, 2),
            "is_etf": is_etf, "df": hist, "info": info
        }
    except Exception as e:
        return {"Ticker": ticker, "error": f"{type(e).__name__}: {e}"}
 
 
def es_valido(res):
    return bool(res) and "error" not in res
 
 
COLS_TABLA = [
    "Ticker", "Tipo", "Precio", "RSI(14)", "MA50", "MA125", "MA200",
    "Net Inc(B)", "D/E Ratio(%)", "MACD", "Señal MACD", "Alerta"
]
 
 
def highlight_alerta(val):
    v = str(val)
    if "REVISAR" in v: return 'background-color: rgba(220, 38, 38, 0.45)'
    if "COMPRA"  in v: return 'background-color: rgba(255, 165, 0, 0.3)'
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
    for ma, col in [('MA50', 'cyan'), ('MA125', 'orange'), ('MA200', 'red')]:
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[ma], line=dict(color=col, width=1 if ma != 'MA200' else 2), name=ma), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbu], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Sup"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbl], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Inf"), row=1, col=1)
    fig.add_annotation(x=df_p.index[-1], y=last_p['Close'], text=f" PRECIO: ${round(last_p['Close'],2)}", showarrow=False, xanchor="left", xshift=15, row=1, col=1, font=dict(color="white"), bgcolor="black")
    fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbu], text=f" B.SUP: ${round(last_p[c_bbu],2)}", showarrow=False, xanchor="left", xshift=15, yshift=20, row=1, col=1, font=dict(color="#00d4ff"))
    fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbl], text=f" B.INF: ${round(last_p[c_bbl],2)}", showarrow=False, xanchor="left", xshift=15, yshift=-20, row=1, col=1, font=dict(color="#00d4ff"))
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_14'], line=dict(color='#C084FC', width=2), name="RSI(14)"), row=2, col=1)
    fig.add_annotation(x=df_p.index[-1], y=last_p['RSI_14'], text=f" RSI: {round(last_p['RSI_14'],2)}", showarrow=False, xanchor="left", xshift=15, row=2, col=1, font=dict(color="#C084FC"))
    hist_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
    fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=hist_colors, name="Impulso"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'], line=dict(color='#2962ff'), name="MACD"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACDs_12_26_9'], line=dict(color='#ff6d00'), name="Señal"), row=3, col=1)
    fig.add_annotation(x=df_p.index[-1], y=last_p['MACD_12_26_9'], text=f" MACD: {round(last_p['MACD_12_26_9'],3)}", showarrow=False, xanchor="left", xshift=15, yshift=15, row=3, col=1, font=dict(color="#2962ff"))
    fig.add_annotation(x=df_p.index[-1], y=last_p['MACDs_12_26_9'], text=f" SEÑAL: {round(last_p['MACDs_12_26_9'],3)}", showarrow=False, xanchor="left", xshift=15, yshift=-15, row=3, col=1, font=dict(color="#ff6d00"))
    fig.update_layout(height=1000, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(r=150))
    st.plotly_chart(fig, use_container_width=True)
 
 
def _fmt(v, suf=""):
    return "N/D" if v is None else f"{v}{suf}"
 
 
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
        c4.metric("Fwd P/E",    f"{item['Fwd P/E']}")
        c4.metric("PEG Ratio",  f"{item['PEG']}")
 
        c5, c6, c7, c8 = st.columns(4)
        c5.metric("FCF Yield",       _fmt(item['FCF Yield(%)'], "%"))
        c6.metric("Deuda Neta/EBITDA", _fmt(item['NetDebt/EBITDA'], "x"))
        c7.metric("Div Yield",       f"{item['Div Yield(%)']}%")
        c8.metric("Market Cap",      f"${item['Market Cap(B)']}B")
 
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
all_tickers, aviso_tickers = get_all_tickers()
if aviso_tickers:
    st.warning(f"⚠️ {aviso_tickers}")
data_scan     = []
errores_scan  = []
 
if st.checkbox("🚀 Iniciar Escaneo Profundo"):
    prog = st.progress(0)
    for i, t in enumerate(all_tickers):
        res = fetch_full_data(t)
        if res and "error" in res:
            errores_scan.append({"Ticker": res["Ticker"], "Error": res["error"]})
        elif res:
            passes = (
                res["is_etf"] or (
                    res["Market Cap(B)"] >= market_cap_min
                    and res["Net Inc(B)"] >= min_net_income
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
 
if errores_scan:
    with st.expander(f"⚠️ Errores durante el escaneo: {len(errores_scan)}"):
        st.dataframe(pd.DataFrame(errores_scan), use_container_width=True)
 
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
data_plan, alertas_compra, alertas_venta, errores_plan = [], [], [], []
 
for t in MIS_ACTIVOS_FIJOS:
    res = fetch_full_data(t)
    if res and "error" in res:
        errores_plan.append({"Ticker": res["Ticker"], "Error": res["error"]})
    elif res:
        data_plan.append(res)
        if "COMPRA"  in res["Alerta"]: alertas_compra.append(t)
        if "REVISAR" in res["Alerta"]: alertas_venta.append(t)
 
if errores_plan:
    with st.expander(f"⚠️ Errores en el plan: {len(errores_plan)}"):
        st.dataframe(pd.DataFrame(errores_plan), use_container_width=True)
 
if data_plan:
    df_plan = pd.DataFrame(data_plan)[COLS_TABLA]
    st.dataframe(df_plan.style.map(highlight_alerta, subset=['Alerta']), use_container_width=True)
 
    if alertas_venta:
        st.error(f"🔴 **Revisar fundamentos:** {', '.join(alertas_venta)}")
    if alertas_compra:
        st.warning(f"🚨 **Oportunidades detectadas:** {', '.join(alertas_compra)}")
 
    if st.button("📧 Enviar Informe Manual ahora"):
        st.warning("Envío de correo aún no implementado.")
 
# --- MONITOR MACRO ---
st.divider()
st.header("🌍 Monitor Macro: Radar de Recesión")
 
 
def normalizar_yield(s):
    """^TNX / ^IRX: algunas versiones devuelven x10. Se detecta por magnitud."""
    return s / 10 if s.dropna().tail(60).median() > 15 else s
 
 
@st.cache_data(ttl=86400)
def fetch_macro_data_direct():
    try:
        t10y = yf.Ticker("^TNX").history(period="2y")['Close'].rename("T10Y")
        t3m  = yf.Ticker("^IRX").history(period="2y")['Close'].rename("T3M")
        t10y_m = normalizar_yield(t10y).resample('ME').last()
        t3m_m  = normalizar_yield(t3m).resample('ME').last()
        t10y_m.index = t10y_m.index.tz_localize(None)
        t3m_m.index  = t3m_m.index.tz_localize(None)
        curva    = (t10y_m - t3m_m).rename('Curva 10Y-3M')
        fed_rate = t3m_m.rename('Tasas Fed (%)')
 
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
 
if macro_data is not None and len(macro_data) >= 14:
    latest = macro_data.iloc[-1]
    prev   = macro_data.iloc[-12] if len(macro_data) > 12 else macro_data.iloc[0]
 
    risk_score = 0
    unemp      = latest['Desempleo (%)']
    # Aproximación a la Regla de Sahm: media móvil 3m vs. mínimo de los 12 meses previos
    u3         = macro_data['Desempleo (%)'].rolling(3).mean()
    unemp_diff = u3.iloc[-1] - u3.iloc[-13:-1].min()
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
        st.markdown(f"**Sahm (aprox.):** {round(unemp_diff,2)} pts — {'⚠️ Subiendo' if unemp_diff >= 0.3 else '✅ Estable'}")
    with col_m3:
        st.metric("Tasas (3M Treasury)", f"{round(rates,2)}%", f"{round(-rates_drop,2)}", delta_color="inverse")
        st.markdown(f"**Estado:** {status_rates}")
 
    st.divider()
    if risk_score >= 70:
        st.error(f"🚨 **ALERTA MACRO ALTA:** índice interno {risk_score}/100.")
    elif risk_score >= 40:
        st.warning(f"⚠️ **PRECAUCIÓN:** índice interno {risk_score}/100.")
    else:
        st.success(f"☀️ **ENTORNO ESTABLE:** índice interno {risk_score}/100.")
    st.caption("Índice propio basado en reglas fijas. No es una probabilidad estadística de recesión.")
 
    st.subheader("Análisis Histórico")
    opcion = st.selectbox("Selecciona indicador:", ("Curva 10Y-3M", "Desempleo (%)", "Tasas Fed (%)"))
    color_map = {"Curva 10Y-3M": "#1f77b4", "Desempleo (%)": "#ff7f0e", "Tasas Fed (%)": "#d62728"}
    st.line_chart(macro_data[opcion], color=color_map[opcion])
elif macro_data is not None:
    st.warning("Datos macro insuficientes para calcular el índice.")
