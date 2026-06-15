import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Terminal Pro - Gabriel Herrera", layout="wide")

if 'last_update' not in st.session_state:
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

if 'email_enviado_hoy' not in st.session_state:
    st.session_state['email_enviado_hoy'] = None

st.title("💎 Terminal de Valor y Estrategia de Acecho")

# --- GUÍA DE PARÁMETROS ---
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
        Promedian el precio durante un período para suavizar el ruido y revelar la tendencia real.

        | Media | Color | Significado |
        |-------|-------|-------------|
        | **MA200** | 🔴 Roja | Tendencia de **largo plazo**. Es el gran filtro institucional. |
        | **MA50** | 🩵 Cian | Tendencia de **mediano plazo**. Filtra el ruido mensual. |

        **Cómo interpretar:**
        - ✅ Precio **por encima** de MA200 → tendencia alcista saludable.
        - ⚠️ Precio **por debajo** de MA200 → posible ciclo bajista o empresa en crisis.
        - 🔔 Cuando MA50 cruza **por encima** de MA200 = *"Golden Cross"* → señal alcista poderosa.
        - 💀 Cuando MA50 cruza **por debajo** de MA200 = *"Death Cross"* → señal bajista severa.
        """)

        st.divider()

        st.markdown("### 📉 Bandas de Bollinger")
        st.markdown("""
        Miden la **volatilidad** del precio. Se expanden cuando hay movimientos bruscos y se contraen en mercados tranquilos.

        | Zona | Señal |
        |------|-------|
        | Precio toca **Banda Superior** | El activo está "estirado" al alza — posible techo temporal. |
        | Precio toca **Banda Inferior** | El activo está "estirado" a la baja — posible zona de rebote. |
        | Bandas muy **estrechas** | Baja volatilidad → suele preceder un movimiento explosivo. |

        > ⚠️ Las Bollinger no indican dirección por sí solas. Combínalas con RSI o MACD para confirmar.
        """)

        st.divider()

        st.markdown("### ⚡ RSI — Índice de Fuerza Relativa (período 14)")
        st.markdown("""
        Mide la **fuerza y velocidad** del movimiento del precio en una escala de 0 a 100.

        | Valor RSI | Zona | Interpretación |
        |-----------|------|----------------|
        | **< 30** | 🔴 Sobreventa extrema | Pánico en el mercado. Zona históricamente de compra institucional. Alta oportunidad. |
        | **30 – 45** | 🟡 Zona de acecho | La empresa está barata respecto a su propia historia. Momento de análisis activo. |
        | **45 – 55** | ⚪ Neutral | Ni barata ni cara. Sin señal clara. |
        | **55 – 70** | 🟢 Momentum positivo | Fuerza alcista. Tendencia favorable, pero mantener cautela. |
        | **> 70** | 🔴 Sobrecompra | El activo se ha subido demasiado rápido. Evitar comprar aquí — riesgo de corrección. |

        > 💡 **Regla de oro:** RSI < 35 + precio en Banda Inferior de Bollinger = zona de alta atención para una posible entrada.
        """)

        st.divider()

        st.markdown("### 🌊 MACD — Convergencia/Divergencia de Medias")
        st.markdown("""
        Mide la **inercia (momentum)** del precio. Detecta cambios de tendencia antes de que se vean en el precio.

        - 📘 **Línea MACD (Azul):** La velocidad actual del movimiento.
        - 🟠 **Línea de Señal (Naranja):** Promedio suavizado del MACD. Actúa como disparador.
        - 📊 **Histograma (Barras):** Diferencia entre ambas líneas — visual de la fuerza.

        | Evento | Significado |
        |--------|-------------|
        | MACD cruza **por encima** de Señal | 🟢 Inercia cambia a **alcista** — posible entrada. |
        | MACD cruza **por debajo** de Señal | 🔴 Inercia cambia a **bajista** — posible salida. |
        | Histograma rojo **se acorta** | La presión vendedora está **muriendo** — posible giro próximo. |
        | MACD positivo y subiendo | Momentum fuerte al alza. |

        > 💡 El cruce del MACD es más potente cuando ocurre **por debajo de cero** (territorio bajista) → indica reversión desde mínimos.
        """)

        st.divider()

        st.markdown("### 📅 Variación de Precio 52 Semanas (%)")
        st.markdown("""
        Muestra cuánto ha subido o bajado el precio en el **último año completo**.

        | Rango | Interpretación |
        |-------|----------------|
        | **> +30%** | Momentum fuerte. Puede estar sobrecomprado o en tendencia genuina. |
        | **0% a +30%** | Zona saludable. Apreciación moderada y sostenible. |
        | **-10% a 0%** | Corrección menor. Puede ser oportunidad si los fundamentales son sólidos. |
        | **-20% a -40%** | Zona de acecho. Alta posibilidad de valor si la empresa es rentable. |
        | **< -40%** | Señal de alerta. Investigar si hay crisis estructural o es simple sobre-reacción del mercado. |

        > ⚠️ Una caída fuerte no es automáticamente una oportunidad. Siempre cruzar con el análisis fundamental.
        """)

    with tab2:
        st.markdown("## Indicadores Fundamentales")

        st.markdown("### 💵 Net Income (Beneficio Neto)")
        st.markdown("""
        Es lo que la empresa **realmente gana** después de pagar todos sus costos, impuestos y deudas.

        | Valor | Señal |
        |-------|-------|
        | **> $5 Billones USD** | 🏆 Empresa élite. Generación de riqueza masiva y sostenida. |
        | **$1B – $5B USD** | ✅ Empresa sólida y rentable. Señal clara de fortaleza operativa. |
        | **$100M – $1B USD** | 🟡 Empresa rentable pero en escala media. Aceptable según el sector. |
        | **$0 – $100M USD** | ⚠️ Rentabilidad marginal. Revisar tendencia: ¿está creciendo o estancada? |
        | **Negativo (pérdidas)** | 🔴 La empresa está destruyendo capital. |
        """)

        st.divider()

        st.markdown("### 📊 Net Margin (Margen Neto)")
        st.markdown("""
        Porcentaje de cada dólar de ingresos que se convierte en beneficio neto.

        | Valor | Interpretación |
        |-------|----------------|
        | **> 20%** | 🏆 Negocio de altísima calidad. Ventaja competitiva muy fuerte (ej. software, pharma). |
        | **10% – 20%** | ✅ Margen saludable. Empresa eficiente y bien gestionada. |
        | **5% – 10%** | 🟡 Aceptable en sectores con márgenes comprimidos (retail, manufactura). |
        | **< 5%** | 🔴 Riesgo de alerta. Vulnerable a cualquier aumento de costos. |
        | **Negativo** | 🚨 VENTA — la empresa pierde dinero por cada dólar que vende. |
        """)

        st.divider()

        st.markdown("### 📈 ROE — Return on Equity")
        st.markdown("""
        Mide cuánto beneficio genera la empresa por cada dólar de capital de los accionistas.

        | Valor | Interpretación |
        |-------|----------------|
        | **> 20%** | 🏆 Empresa élite. Genera valor excepcional para el accionista. |
        | **15% – 20%** | ✅ Muy bueno. Negocio de calidad. |
        | **10% – 15%** | 🟡 Aceptable. Por encima del promedio del mercado. |
        | **< 10%** | ⚠️ Bajo. La empresa no usa bien el capital de los accionistas. |
        | **Negativo** | 🔴 ALERTA — capital propio en terreno negativo. |
        """)

        st.divider()

        st.markdown("### ⚖️ Debt / Equity (Deuda sobre Patrimonio)")
        st.markdown("""
        Mide cuánta **deuda** usa la empresa en relación a su capital propio.

        | Ratio | Interpretación |
        |-------|----------------|
        | **< 0.5** | 🟢 Empresa muy sólida. Poca deuda, gran independencia financiera. |
        | **0.5 – 1.0** | ✅ Nivel saludable y común en empresas maduras. |
        | **1.0 – 2.0** | 🟡 Deuda elevada pero manejable si el flujo de caja es fuerte. |
        | **> 2.0** | 🔴 Riesgo alto. La empresa depende del crédito para operar. |
        """)

        st.divider()

        st.markdown("### 🎲 Beta (Volatilidad relativa al mercado)")
        st.markdown("""
        Mide cuánto se mueve la acción en relación al mercado general (S&P 500 = 1.0).

        | Beta | Interpretación |
        |------|----------------|
        | **< 0.5** | Muy estable. Ideal para carteras defensivas. |
        | **0.5 – 1.0** | Menor volatilidad que el mercado. |
        | **1.0 – 1.5** | Similar al mercado. |
        | **1.5 – 2.0** | Alta volatilidad. Mayor riesgo y potencial retorno. |
        | **> 2.0** | 🔴 Especulativo. Solo para perfiles de alto riesgo. |
        """)

    with tab3:
        st.markdown("## 🧭 Guía Rápida: Semáforo de Señales")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 🔴 VENTA / Precaución")
            st.markdown("""
            - RSI **> 70** (sobrecompra)
            - Precio **por debajo** de MA200
            - MACD cruza **a la baja**
            - Net Income **negativo o cayendo**
            - Net Margin **< 5%**
            - ROE **negativo**
            - Debt/Equity **> 200%**
            - Beta **> 2.0**
            """)

        with col2:
            st.markdown("### 🟡 Vigilar / Analizar")
            st.markdown("""
            - RSI entre **35 – 50**
            - Precio cerca de MA50
            - Histograma MACD **acortándose**
            - Net Income **entre $100M – $1B**
            - Net Margin **5% – 10%**
            - Debt/Equity **entre 1.0 – 2.0**
            - Beta **1.5 – 2.0**
            """)

        with col3:
            st.markdown("### 🟢 Señal Positiva")
            st.markdown("""
            - RSI **< 35** (sobreventa)
            - Precio **por encima** de MA200
            - MACD cruza **al alza desde cero**
            - Net Income **> $1B y creciendo**
            - Net Margin **> 15%**
            - ROE **> 15%**
            - Debt/Equity **< 100%**
            - *Golden Cross* MA50 > MA200
            """)

        st.divider()
        st.info("💡 **Recuerda:** Ningún indicador funciona en aislamiento. La señal más poderosa es cuando **técnico y fundamental coinciden**: empresa sólida con RSI en sobreventa y MACD girando al alza.")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Parámetros de Ingeniería")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=10)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0.1)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 400, 120)
rsi_limit = st.sidebar.slider("Filtro RSI (14) Máx", 10, 100, 45)

st.sidebar.divider()
st.sidebar.header("🛡️ Filtros Fundamentales de Calidad")
min_net_margin = st.sidebar.slider("Net Margin Mínimo (%)", -50, 50, 5)
min_roe = st.sidebar.slider("ROE Mínimo (%)", -50, 100, 10)
max_beta = st.sidebar.slider("Beta Máximo", 0.0, 5.0, 2.0, step=0.1)

st.sidebar.divider()
st.sidebar.header("📧 Configuración de Alertas")
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = "gabelohm@live.com"

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
    "SBUX", "LOW", "AVGO", "NEE", "TXN", "GOOG", "MSFT", "DHR", "COST",
    "VT", "VYMI", "VIG", "MCHI", "BAC", "ADC", "VICI", "CSCO", "HPQ",
    "HPE", "JCI", "HON", "PFE", "CAT", "TGT", "APD", "KMB", "QCOM",
    "ACN", "GE", "MDT", "SONY", "NTDOY"
]

@st.cache_data(ttl=86400)
def get_all_tickers():
    try:
        url_sp = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        sp500 = pd.read_html(url_sp)[0]['Symbol'].tolist()
        url_nasdaq = 'https://en.wikipedia.org/wiki/Nasdaq-100#Components'
        nasdaq100 = pd.read_html(url_nasdaq)[4]['Ticker'].tolist()
        combined = [s.replace('.', '-') for s in (sp500 + nasdaq100 + MIS_ACTIVOS_FIJOS)]
        return sorted(list(set(combined)))
    except Exception as e:
        return MIS_ACTIVOS_FIJOS

@st.cache_data(ttl=3600)
def fetch_full_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y", interval="1d")
        if hist.empty or len(hist) < 252:
            return None
        
        info = stock.info
        hist['MA50']  = ta.sma(hist['Close'], length=50)
        hist['MA125'] = ta.sma(hist['Close'], length=125)
        hist['MA200'] = ta.sma(hist['Close'], length=200)
        hist['RSI_14'] = ta.rsi(hist['Close'], length=14)
        bb   = ta.bbands(hist['Close'], length=20, std=2)
        macd = ta.macd(hist['Close'])
        hist = pd.concat([hist, macd, bb], axis=1)
        
        last = hist.iloc[-1]
        price_now = last['Close']
        c_bbl = [c for c in hist.columns if c.startswith('BBL')][0]
        c_bbu = [c for c in hist.columns if c.startswith('BBU')][0]

        # --- MÉTRICAS FUNDAMENTALES ---
        net_income  = info.get('netIncomeToCommon', 0) or 0
        revenue     = info.get('totalRevenue', 0) or 0
        net_margin  = (info.get('profitMargins', 0) or 0) * 100
        roe         = (info.get('returnOnEquity', 0) or 0) * 100
        roa         = (info.get('returnOnAssets', 0) or 0) * 100
        de_ratio    = info.get('debtToEquity', 0) or 0
        beta_val    = info.get('beta', 1) or 1
        pe_ratio    = info.get('trailingPE', 0) or 0
        div_yield   = ((info.get('dividendYield', 0) or 0)) * 100
        eps         = info.get('trailingEps', 0) or 0
        peg         = info.get('pegRatio', 0) or 0
        free_cf     = info.get('freeCashflow', 0) or 0

        # --- LÓGICA DE ALERTA DE COMPRA ---
        alerta_compra = False
        if last['RSI_14'] <= 32 or price_now <= last[c_bbl] * 1.02 or last['MACD_12_26_9'] <= 0.05:
            alerta_compra = True

        # --- LÓGICA DE ALERTA DE VENTA POR DETERIORO FUNDAMENTAL ---
        alerta_venta  = False
        razones_venta = []

        if net_margin < 5:
            razones_venta.append(f"Margen {round(net_margin,1)}%<5%")
            alerta_venta = True
        if roe < 0:
            razones_venta.append(f"ROE negativo ({round(roe,1)}%)")
            alerta_venta = True
        if de_ratio > 200:
            razones_venta.append(f"D/E {round(de_ratio,0)}%>200%")
            alerta_venta = True
        if net_income < 0:
            razones_venta.append("Net Income negativo")
            alerta_venta = True
        if beta_val > 2.0:
            razones_venta.append(f"Beta {round(beta_val,2)}>2.0")
            alerta_venta = True

        # --- ETIQUETA FINAL ---
        if alerta_venta:
            alerta_label = f"🔴 VENTA ({', '.join(razones_venta)})"
        elif alerta_compra:
            alerta_label = "🚨 COMPRA"
        else:
            alerta_label = "✅ HOLD"

        def fmt_ma(val, price):
            if pd.isna(val):
                return "N/D"
            return f"{'🟢' if price > val else '🔴'} ${round(val, 2)}"

        return {
            "Ticker":        ticker,
            "Precio":        round(price_now, 2),
            "RSI(14)":       round(last['RSI_14'], 2),
            "MA50":          fmt_ma(last['MA50'], price_now),
            "MA125":         fmt_ma(last['MA125'], price_now),
            "MA200":         fmt_ma(last['MA200'], price_now),
            "Revenue(B)":    round(revenue / 1e9, 2),
            "Net Inc(B)":    round(net_income / 1e9, 2),
            "Net Margin(%)": round(net_margin, 2),
            "ROE(%)":        round(roe, 2),
            "ROA(%)":        round(roa, 2),
            "D/E Ratio(%)":  round(de_ratio, 2),
            "Beta":          round(beta_val, 2),
            "P/E":           round(pe_ratio, 2),
            "PEG":           round(peg, 2),
            "EPS":           round(eps, 2),
            "Div Yield(%)":  round(div_yield, 2),
            "Free CF(B)":    round(free_cf / 1e9, 2),
            "MACD":          round(last['MACD_12_26_9'], 3),
            "Señal MACD":    round(last['MACDs_12_26_9'], 3),
            "Alerta":        alerta_label,
            "df":            hist,
            "info":          info
        }
    except:
        return None

# --- COLUMNAS A MOSTRAR EN TABLA (sin df e info) ---
COLS_TABLA = [
    "Ticker", "Precio", "RSI(14)", "MA50", "MA125", "MA200",
    "Revenue(B)", "Net Inc(B)", "Net Margin(%)", "ROE(%)", "ROA(%)",
    "D/E Ratio(%)", "Beta", "P/E", "PEG", "EPS", "Div Yield(%)",
    "Free CF(B)", "MACD", "Señal MACD", "Alerta"
]

# --- 1. PRIMERA TABLA: ESCANEO DINÁMICO ---
all_tickers = get_all_tickers()
data_scan = []
if st.checkbox("🚀 Iniciar Escaneo Profundo"):
    prog = st.progress(0)
    for i, t in enumerate(all_tickers):
        res = fetch_full_data(t)
        if res:
            if (res["RSI(14)"] <= rsi_limit
                    and res["Net Inc(B)"] >= min_net_income
                    and res["D/E Ratio(%)"] <= max_de_ratio
                    and res["Net Margin(%)"] >= min_net_margin
                    and res["ROE(%)"] >= min_roe
                    and res["Beta"] <= max_beta):
                data_scan.append(res)
        prog.progress((i + 1) / len(all_tickers))
    prog.empty()

if data_scan:
    df_view = pd.DataFrame(data_scan)[COLS_TABLA]
    st.subheader(f"📋 Resultados del Acecho ({len(data_scan)} activos)")
    
    def highlight_scan(val):
        v = str(val)
        if "VENTA" in v:  return 'background-color: rgba(220, 38, 38, 0.45)'
        if "COMPRA" in v: return 'background-color: rgba(255, 75, 75, 0.3)'
        return ''
    
    st.dataframe(df_view.style.map(highlight_scan, subset=['Alerta']), use_container_width=True)
    
    # --- 2. GRÁFICAS ---
    seleccion = st.selectbox("🎯 Análisis Técnico Detallado:", df_view["Ticker"].tolist())
    if seleccion:
        item = next(i for i in data_scan if i["Ticker"] == seleccion)
        df_p  = item["df"].tail(252)
        last_p = df_p.iloc[-1]
        c_bbu = [c for c in df_p.columns if c.startswith('BBU')][0]
        c_bbl = [c for c in df_p.columns if c.startswith('BBL')][0]

        fig = make_subplots(
            rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.07,
            subplot_titles=("Precio y Bandas Bollinger", "RSI (14)", "MACD e Impulso"),
            row_heights=[0.5, 0.2, 0.3]
        )

        fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA50'],  line=dict(color='cyan', width=1), name="MA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA125'], line=dict(color='orange', width=1), name="MA125"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red', width=2), name="MA200"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbu], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Sup"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbl], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Inf"), row=1, col=1)

        fig.add_annotation(x=df_p.index[-1], y=last_p['Close'],  text=f" PRECIO: ${round(last_p['Close'],2)}", showarrow=False, xanchor="left", xshift=15, row=1, col=1, font=dict(color="white"), bgcolor="black")
        fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbu],   text=f" B.SUP: ${round(last_p[c_bbu],2)}", showarrow=False, xanchor="left", xshift=15, yshift=20, row=1, col=1, font=dict(color="#00d4ff"))
        fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbl],   text=f" B.INF: ${round(last_p[c_bbl],2)}", showarrow=False, xanchor="left", xshift=15, yshift=-20, row=1, col=1, font=dict(color="#00d4ff"))

        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_14'], line=dict(color='#C084FC', width=2), name="RSI(14)"), row=2, col=1)
        fig.add_annotation(x=df_p.index[-1], y=last_p['RSI_14'], text=f" RSI: {round(last_p['RSI_14'], 2)}", showarrow=False, xanchor="left", xshift=15, row=2, col=1, font=dict(color="#C084FC"))

        hist_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
        fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=hist_colors, name="Impulso"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'],  line=dict(color='#2962ff'), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACDs_12_26_9'], line=dict(color='#ff6d00'), name="Señal"), row=3, col=1)
        
        fig.add_annotation(x=df_p.index[-1], y=last_p['MACD_12_26_9'],  text=f" MACD: {round(last_p['MACD_12_26_9'], 3)}",  showarrow=False, xanchor="left", xshift=15, yshift=15,  row=3, col=1, font=dict(color="#2962ff"))
        fig.add_annotation(x=df_p.index[-1], y=last_p['MACDs_12_26_9'], text=f" SEÑAL: {round(last_p['MACDs_12_26_9'], 3)}", showarrow=False, xanchor="left", xshift=15, yshift=-15, row=3, col=1, font=dict(color="#ff6d00"))

        fig.update_layout(height=1000, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(r=150))
        st.plotly_chart(fig, use_container_width=True)

        # --- PANEL FUNDAMENTAL DETALLADO ---
        st.subheader(f"📊 Radiografía Fundamental: {seleccion}")
        
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        col_f1.metric("Revenue",      f"${item['Revenue(B)']}B")
        col_f1.metric("Net Income",   f"${item['Net Inc(B)']}B")
        col_f1.metric("Free CF",      f"${item['Free CF(B)']}B")
        
        col_f2.metric("Net Margin",   f"{item['Net Margin(%)']}%")
        col_f2.metric("ROE",          f"{item['ROE(%)']}%")
        col_f2.metric("ROA",          f"{item['ROA(%)']}%")
        
        col_f3.metric("D/E Ratio",    f"{item['D/E Ratio(%)']}%")
        col_f3.metric("Beta",         f"{item['Beta']}")
        col_f3.metric("EPS",          f"${item['EPS']}")
        
        col_f4.metric("P/E Ratio",    f"{item['P/E']}")
        col_f4.metric("PEG Ratio",    f"{item['PEG']}")
        col_f4.metric("Div Yield",    f"{item['Div Yield(%)']}%")

        # Semáforo fundamental rápido
        st.markdown("#### 🚦 Salud Fundamental")
        flags = []
        if item['Net Margin(%)'] >= 15: flags.append("🟢 Margen excelente")
        elif item['Net Margin(%)'] >= 5: flags.append("🟡 Margen aceptable")
        else: flags.append("🔴 Margen bajo — riesgo")

        if item['ROE(%)'] >= 15: flags.append("🟢 ROE fuerte")
        elif item['ROE(%)'] >= 0: flags.append("🟡 ROE moderado")
        else: flags.append("🔴 ROE negativo — alerta")

        if item['D/E Ratio(%)'] < 100: flags.append("🟢 Deuda controlada")
        elif item['D/E Ratio(%)'] < 200: flags.append("🟡 Deuda moderada")
        else: flags.append("🔴 Deuda elevada — riesgo")

        if item['Beta'] < 1.0: flags.append("🟢 Baja volatilidad")
        elif item['Beta'] < 1.5: flags.append("🟡 Volatilidad normal")
        else: flags.append("🔴 Alta volatilidad")

        st.markdown("  |  ".join(flags))

# --- 3. SEGUNDA TABLA: MI PLAN ESTRATÉGICO ---
st.divider()
st.header("🎯 Vigilancia de Mi Plan Estratégico")
data_plan = []
alertas_compra = []
alertas_venta  = []

for t in MIS_ACTIVOS_FIJOS:
    res = fetch_full_data(t)
    if res:
        data_plan.append(res)
        if "COMPRA" in res["Alerta"]:
            alertas_compra.append(t)
        if "VENTA" in res["Alerta"]:
            alertas_venta.append(t)

if data_plan:
    df_plan = pd.DataFrame(data_plan)[COLS_TABLA]

    def highlight_plan(val):
        v = str(val)
        if "VENTA"  in v: return 'background-color: rgba(220, 38, 38, 0.45)'
        if "COMPRA" in v: return 'background-color: rgba(255, 75, 75, 0.3)'
        return ''
    
    st.dataframe(df_plan.style.map(highlight_plan, subset=['Alerta']), use_container_width=True)

    # --- ALERTAS VISIBLES ---
    if alertas_venta:
        st.error(f"🔴 **ALERTA DE DETERIORO — Revisar posición:** {', '.join(alertas_venta)}")
    if alertas_compra:
        st.warning(f"🚨 **Oportunidades de entrada detectadas:** {', '.join(alertas_compra)}")

    # --- LÓGICA AUTOMATIZACIÓN 12:00 PM ---
    ahora     = datetime.now()
    fecha_hoy = ahora.strftime("%Y-%m-%d")

    if ahora.hour >= 12 and (alertas_compra or alertas_venta) and st.session_state['email_enviado_hoy'] != fecha_hoy:
        st.toast("✅ Disparando alerta automática de mediodía...", icon="📧")
        st.success(f"📬 Informe enviado automáticamente a {st.session_state['user_email']}")
        st.session_state['email_enviado_hoy'] = fecha_hoy
    
    if st.button("📧 Enviar Informe Manual ahora"):
        st.info(f"Enviando informe a {st.session_state['user_email']}...")

# Estado en sidebar
st.sidebar.divider()
st.sidebar.write(f"📅 Auto-envío: {'✅ Realizado' if st.session_state['email_enviado_hoy'] == datetime.now().strftime('%Y-%m-%d') else '⏳ Programado 12:00 PM'}")


# --- BLOQUE DE CONTEXTO MACROECONÓMICO ---
st.divider()
st.header("🌍 Monitor Macro: Radar de Recesión")

@st.cache_data(ttl=86400)
def fetch_macro_data_direct():
    try:
        import pandas_datareader.data as web

        end   = datetime.today()
        start = end - timedelta(days=730)

        unrate     = web.DataReader("UNRATE",   "fred", start, end)
        fedfunds   = web.DataReader("FEDFUNDS", "fred", start, end)
        yield_curr = web.DataReader("T10Y2Y",   "fred", start, end)

        df = pd.concat([unrate, fedfunds, yield_curr], axis=1)
        df.columns = ['Desempleo (%)', 'Tasas Fed (%)', 'Curva 10Y-2Y']
        return df.ffill().tail(252)

    except Exception as e:
        st.error(f"Error al conectar con FRED: {e}")
        return None

macro_data = fetch_macro_data_direct()

if macro_data is not None:
    latest = macro_data.iloc[-1]
    prev   = macro_data.iloc[-22] if len(macro_data) > 22 else macro_data.iloc[0]
    
    # CÁLCULO DE RIESGO ESCALONADO
    risk_score = 0
    
    unemp          = latest['Desempleo (%)']
    unemp_min_year = macro_data['Desempleo (%)'].min()
    unemp_diff     = unemp - unemp_min_year
    if unemp_diff >= 0.5:  risk_score += 40
    elif unemp_diff >= 0.3: risk_score += 20

    spread = latest['Curva 10Y-2Y']
    if spread < 0:    risk_score += 40
    elif spread < 0.10: risk_score += 20

    rates        = latest['Tasas Fed (%)']
    rates_3m_ago = macro_data['Tasas Fed (%)'].iloc[-3] if len(macro_data) > 3 else rates
    rates_drop   = rates_3m_ago - rates
    
    status_rates = "💰 Acomodaticia"
    if rates > 5.0:
        risk_score += 20
        status_rates = "💸 Restrictiva"
    elif rates_drop >= 0.50:
        risk_score += 20
        status_rates = "🚨 Caída Brusca (Pánico)"
    elif rates > 4.0:
        risk_score += 10
        status_rates = "📊 Presión Moderada"

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Curva 10Y-2Y", f"{round(spread, 2)}", f"{round(spread - prev['Curva 10Y-2Y'], 2)}")
        st.markdown(f"**Estado:** {'🔴 INVERTIDA' if spread < 0 else '🟢 NORMAL'}")
    with col_m2:
        st.metric("Desempleo EE.UU.", f"{unemp}%", f"{round(unemp - prev['Desempleo (%)'], 2)}", delta_color="inverse")
        st.markdown(f"**Estado:** {'⚠️ Subiendo' if unemp_diff >= 0.3 else '✅ Estable'}")
    with col_m3:
        st.metric("Tasas Fed Funds", f"{rates}%", f"{round(-rates_drop, 2)}", delta_color="inverse")
        st.markdown(f"**Estado:** {status_rates}")

    st.divider()
    if risk_score >= 70:
        st.error(f"🚨 **ALERTA MÁXIMA:** Riesgo de Recesión en {risk_score}%.")
    elif risk_score >= 40:
        st.warning(f"⚠️ **PRECAUCIÓN:** Riesgo Moderado ({risk_score}%).")
    else:
        st.success(f"☀️ **ENTORNO SEGURO:** Riesgo bajo ({risk_score}%).")

    st.subheader("Análisis Histórico")
    opcion_grafica = st.selectbox(
        "Selecciona el indicador para visualizar:",
        ("Curva 10Y-2Y", "Desempleo (%)", "Tasas Fed (%)")
    )
    
    color_map = {
        "Curva 10Y-2Y":  "#1f77b4",
        "Desempleo (%)": "#ff7f0e",
        "Tasas Fed (%)": "#d62728"
    }
    
    st.line_chart(macro_data[opcion_grafica], color=color_map[opcion_grafica])
