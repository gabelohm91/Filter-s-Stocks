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

# Estado para controlar el envío automático diario y no repetir correos
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

        st.markdown("### ⚡ RSI — Índice de Fuerza Relativa (período 50)")
        st.markdown("""
        Mide la **fuerza y velocidad** del movimiento del precio en una escala de 0 a 100.  
        Usando un período de 50 se elimina el ruido diario y se revela la **fuerza estructural** del último año.

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
        Es lo que la empresa **realmente gana** después de pagar todos sus costos, impuestos y deudas. Es el indicador más directo de salud financiera.

        | Valor | Señal |
        |-------|-------|
        | **> $5 Billones USD** | 🏆 Empresa élite. Generación de riqueza masiva y sostenida. |
        | **$1B – $5B USD** | ✅ Empresa sólida y rentable. Señal clara de fortaleza operativa. |
        | **$100M – $1B USD** | 🟡 Empresa rentable pero en escala media. Aceptable según el sector. |
        | **$0 – $100M USD** | ⚠️ Rentabilidad marginal. Revisar tendencia: ¿está creciendo o estancada? |
        | **Negativo (pérdidas)** | 🔴 La empresa está destruyendo capital. Solo válido si es una startup en expansión con plan claro. |

        > 💡 **Lo más importante no es solo el número actual, sino la tendencia:** ¿El Net Income crece año a año? Una empresa que pasa de $500M a $2B en 3 años es mucho más interesante que una estancada en $3B.
        """)

        st.divider()

        st.markdown("### ⚖️ Debt / Equity (Deuda sobre Patrimonio)")
        st.markdown("""
        Mide cuánta **deuda** usa la empresa en relación a su capital propio. Indica el nivel de riesgo financiero.

        | Ratio | Interpretación |
        |-------|----------------|
        | **< 0.5** | 🟢 Empresa muy sólida. Poca deuda, gran independencia financiera. |
        | **0.5 – 1.0** | ✅ Nivel saludable y común en empresas maduras. |
        | **1.0 – 2.0** | 🟡 Deuda elevada pero manejable si el flujo de caja es fuerte. |
        | **> 2.0** | 🔴 Riesgo alto. La empresa depende del crédito para operar. |
        | **Negativo** | ⚠️ El patrimonio es negativo — señal de crisis o modelo de negocio inusual (ej. buybacks extremos). |

        > ⚠️ El D/E varía mucho por sector: bancos y utilities naturalmente tienen D/E alto. Siempre comparar contra el promedio del sector, no contra un número universal.
        """)

    with tab3:
        st.markdown("## 🧭 Guía Rápida: Semáforo de Señales")
        st.markdown("Una referencia visual para evaluar de un vistazo si un activo merece atención.")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 🔴 Evitar / Precaución")
            st.markdown("""
            - RSI **> 70** (sobrecompra)
            - Precio **por debajo** de MA200
            - MACD cruza **a la baja**
            - Net Income **negativo o cayendo**
            - Debt/Equity **> 2.0**
            - Precio 52W **< -40%** sin explicación
            """)

        with col2:
            st.markdown("### 🟡 Vigilar / Analizar")
            st.markdown("""
            - RSI entre **35 – 50**
            - Precio cerca de MA50
            - Histograma MACD **acortándose**
            - Net Income **entre $100M – $1B**
            - Debt/Equity **entre 1.0 – 2.0**
            - Precio 52W entre **-10% y -30%**
            """)

        with col3:
            st.markdown("### 🟢 Señal Positiva")
            st.markdown("""
            - RSI **< 35** (sobreventa)
            - Precio **por encima** de MA200
            - MACD cruza **al alza desde cero**
            - Net Income **> $1B y creciendo**
            - Debt/Equity **< 1.0**
            - *Golden Cross* MA50 > MA200
            """)

        st.divider()
        st.info("💡 **Recuerda:** Ningún indicador funciona en aislamiento. La señal más poderosa es cuando **técnico y fundamental coinciden**: empresa sólida con RSI en sobreventa y MACD girando al alza.")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Parámetros de Ingeniería")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=20)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 400, 150)
rsi_limit = st.sidebar.slider("Filtro RSI (14) Máx", 10, 100, 65)

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
# Se agregaron ASML, BHP, DHR, COST y NEE a tu lista de confianza
MIS_ACTIVOS_FIJOS = [
    "VOO", "SCHD", "VGT", "VXUS", "VUG", "QQQ", "KO", "PEP", "WMT", "PG", 
    "O", "CVX", "JNJ", "MCD", "JPM", "XOM", "V", "ASML", "BHP", "ABBV", 
    "SBUX", "LOW", "AVGO", "NEE", "TXN", "GOOG", "MSFT", "DHR", "COST"
]

@st.cache_data(ttl=86400)
def get_all_tickers():
    try:
        # 1. Obtener S&P 500
        url_sp = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        sp500 = pd.read_html(url_sp)[0]['Symbol'].tolist()
        
        # 2. Obtener NASDAQ-100 (Para cubrir el QQQ completo)
        url_nasdaq = 'https://en.wikipedia.org/wiki/Nasdaq-100#Components'
        nasdaq100 = pd.read_html(url_nasdaq)[4]['Ticker'].tolist()
        
        # Limpieza de símbolos (puntos por guiones para yfinance)
        combined = [s.replace('.', '-') for s in (sp500 + nasdaq100 + MIS_ACTIVOS_FIJOS)]
        
        # Eliminar duplicados y ordenar
        return sorted(list(set(combined)))
    except Exception as e:
        # En caso de error de conexión, usamos al menos tus activos fijos
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
    
    # --- 2. GRÁFICAS (CON TEXTOS AJUSTADOS SIN SOBREPOSICIÓN) ---
    seleccion = st.selectbox("🎯 Análisis Técnico Detallado:", df_view["Ticker"].tolist())
    if seleccion:
        item = next(i for i in data_scan if i["Ticker"] == seleccion)
        df_p = item["df"].tail(252)
        last_p = df_p.iloc[-1]
        c_bbu, c_bbl = [c for c in df_p.columns if c.startswith('BBU')][0], [c for c in df_p.columns if c.startswith('BBL')][0]

        fig = make_subplots(
            rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.07,
            subplot_titles=("Precio y Bandas Bollinger", "RSI (14)", "MACD e Impulso"),
            row_heights=[0.5, 0.2, 0.3]
        )

        # Panel 1: Precio y Bandas
        fig.add_trace(go.Candlestick(x=df_p.index, open=df_p['Open'], high=df_p['High'], low=df_p['Low'], close=df_p['Close'], name="Precio"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA50'], line=dict(color='cyan', width=1), name="MA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA125'], line=dict(color='orange', width=1), name="MA125"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red', width=2), name="MA200"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbu], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Sup"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p[c_bbl], line=dict(color='rgba(255,255,255,0.3)', dash='dot'), name="B.Inf"), row=1, col=1)

        # VALORES PANEL 1: Separados mediante yshift para evitar traslape
        fig.add_annotation(x=df_p.index[-1], y=last_p['Close'], text=f" PRECIO: ${round(last_p['Close'],2)}", showarrow=False, xanchor="left", xshift=15, row=1, col=1, font=dict(color="white"), bgcolor="black")
        fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbu], text=f" B.SUP: ${round(last_p[c_bbu],2)}", showarrow=False, xanchor="left", xshift=15, yshift=20, row=1, col=1, font=dict(color="#00d4ff"))
        fig.add_annotation(x=df_p.index[-1], y=last_p[c_bbl], text=f" B.INF: ${round(last_p[c_bbl],2)}", showarrow=False, xanchor="left", xshift=15, yshift=-20, row=1, col=1, font=dict(color="#00d4ff"))

        # Panel 2: RSI
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['RSI_14'], line=dict(color='#C084FC', width=2), name="RSI(14)"), row=2, col=1)
        fig.add_annotation(x=df_p.index[-1], y=last_p['RSI_14'], text=f" RSI: {round(last_p['RSI_14'], 2)}", showarrow=False, xanchor="left", xshift=15, row=2, col=1, font=dict(color="#C084FC"))

        # Panel 3: MACD + SEÑAL (VALORES RECUPERADOS)
        hist_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
        fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=hist_colors, name="Impulso"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'], line=dict(color='#2962ff'), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACDs_12_26_9'], line=dict(color='#ff6d00'), name="Señal"), row=3, col=1)
        
        # VALORES PANEL 3: Uso de yshift positivo y negativo para legibilidad total
        fig.add_annotation(x=df_p.index[-1], y=last_p['MACD_12_26_9'], text=f" MACD: {round(last_p['MACD_12_26_9'], 3)}", showarrow=False, xanchor="left", xshift=15, yshift=15, row=3, col=1, font=dict(color="#2962ff"))
        fig.add_annotation(x=df_p.index[-1], y=last_p['MACDs_12_26_9'], text=f" SEÑAL: {round(last_p['MACDs_12_26_9'], 3)}", showarrow=False, xanchor="left", xshift=15, yshift=-15, row=3, col=1, font=dict(color="#ff6d00"))

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
    def highlight_alerts(val):
        return 'background-color: rgba(255, 75, 75, 0.3)' if val == "🚨 COMPRA" else ''
    
    st.dataframe(df_plan.style.map(highlight_alerts, subset=['Alerta']), use_container_width=True)

    # --- LÓGICA DE AUTOMATIZACIÓN A LAS 12:00 PM ---
    ahora = datetime.now()
    fecha_hoy = ahora.strftime("%Y-%m-%d")
    
    # Si son las 12:00 PM o más, hay alertas, y no se ha enviado hoy:
    if ahora.hour >= 12 and alertas_detectadas and st.session_state['email_enviado_hoy'] != fecha_hoy:
        st.toast(f"✅ Disparando alerta automática de mediodía...", icon="📧")
        # Simulación de envío automático
        st.success(f"📬 Informe enviado automáticamente a {st.session_state['user_email']}")
        # Registro para no repetir el envío hasta el día siguiente
        st.session_state['email_enviado_hoy'] = fecha_hoy
    
    if alertas_detectadas:
        st.warning(f"⚠️ Oportunidades detectadas: {', '.join(alertas_detectadas)}")
        if st.button("📧 Enviar Informe Manual ahora"):
            st.info(f"Enviando informe a {st.session_state['user_email']}...")

# Indicador de estado en la barra lateral
st.sidebar.divider()
st.sidebar.write(f"📅 Auto-envío: {'✅ Realizado' if st.session_state['email_enviado_hoy'] == datetime.now().strftime('%Y-%m-%d') else '⏳ Programado 12:00 PM'}")


# --- BLOQUE DE CONTEXTO MACROECONÓMICO (DIRECTO DESDE FRED) ---
st.divider()
st.header("🌍 Monitor Macro: Radar de Recesión")

@st.cache_data(ttl=86400)
def fetch_macro_data_direct():
    try:
        # URLs directas de descarga de FRED para evitar librerías obsoletas
        base_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
        
        # Descargamos las 3 series clave
        unrate = pd.read_csv(f"{base_url}UNRATE", index_col=0, parse_dates=True)
        fedfunds = pd.read_csv(f"{base_url}FEDFUNDS", index_col=0, parse_dates=True)
        yield_curr = pd.read_csv(f"{base_url}T10Y2Y", index_col=0, parse_dates=True)
        
        # Combinamos todo en un solo DataFrame
        df = pd.concat([unrate, fedfunds, yield_curr], axis=1)
        df.columns = ['Desempleo (%)', 'Tasas Fed (%)', 'Curva 10Y-2Y']
        return df.ffill().tail(252) # Último año de datos
    except Exception as e:
        st.error(f"Error al conectar con FRED: {e}")
        return None

macro_data = fetch_macro_data_direct()

if macro_data is not None:
    latest = macro_data.iloc[-1]
    # Comparamos contra el valor de hace ~30 días para la métrica
    prev = macro_data.iloc[-22] if len(macro_data) > 22 else macro_data.iloc[0]
    
    col_m1, col_m2, col_m3 = st.columns(3)
    
    with col_m1:
        spread = latest['Curva 10Y-2Y']
        st.metric("Curva 10Y-2Y", f"{round(spread, 2)}", f"{round(spread - prev['Curva 10Y-2Y'], 2)}")
        st.markdown(f"**Estado:** {'🔴 INVERTIDA' if spread < 0 else '🟢 NORMAL'}")

    with col_m2:
        unemp = latest['Desempleo (%)']
        diff_unemp = unemp - prev['Desempleo (%)']
        st.metric("Desempleo EE.UU.", f"{unemp}%", f"{round(diff_unemp, 2)}", delta_color="inverse")
        st.markdown(f"**Estado:** {'⚠️ Subiendo' if diff_unemp > 0.2 else '✅ Estable'}")

    with col_m3:
        rates = latest['Tasas Fed (%)']
        st.metric("Tasas Fed Funds", f"{rates}%", f"{round(rates - prev['Tasas Fed (%)'], 2)}", delta_color="inverse")
        st.markdown(f"**Estado:** {'💸 Restrictiva' if rates > 4 else '💰 Acomodaticia'}")

    # Lógica de Riesgo (40/40/20)
    risk_score = 0
    if spread < 0: risk_score += 40
    if (unemp - macro_data['Desempleo (%)'].min()) > 0.3: risk_score += 40
    if rates > 5: risk_score += 20

    st.divider()
    if risk_score >= 70:
        st.error(f"🚨 **ALERTA MÁXIMA:** Riesgo de Recesión en {risk_score}%. Protege capital.")
    elif risk_score >= 40:
        st.warning(f"⚠️ **PRECAUCIÓN:** Riesgo Moderado ({risk_score}%).")
    else:
        st.success(f"☀️ **ENTORNO SEGURO:** Riesgo bajo ({risk_score}%).")

    st.subheader("Evolución de la Curva (10Y - 2Y)")
    st.line_chart(macro_data['Curva 10Y-2Y'])
