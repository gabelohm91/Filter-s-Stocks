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
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=50)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 300, 120)
rsi_anual_limit = st.sidebar.slider("Filtro RSI Anual Máx", 10, 70, 50)

if st.sidebar.button('🔄 Refrescar Datos'):
    st.cache_data.clear()
    st.session_state['last_update'] = datetime.now().strftime("%H:%M:%S")

st.sidebar.success(f"✅ Sincronizado: {st.session_state['last_update']}")

# --- GUÍA DE REFERENCIA ---
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

# --- GESTIÓN DE ACTIVOS (S&P 500 + SELECCIÓN ESTRATÉGICA) ---
@st.cache_data(ttl=86400)
def get_all_tickers():
    # 1. Obtener S&P 500 desde Wikipedia
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        sp500 = pd.read_html(url)[0]['Symbol'].tolist()
    except:
        sp500 = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"] # Fallback

    # 2. Tu selección de Valor, ETFs y Prospectos
    especiales = [
        "VOO", "QQQ", "SCHD", "VGT", "VXUS", "VUG", # ETFs Calidad
        "LOW", "ABBV", "SBUX", "TGT", "DHR", "NEE", # Valor y Aristócratas
        "ASML", "AVGO", "TSM", "NVDA", "ARM",       # Tecnología y Futuro
        "MCD", "KO", "PEP", "JNJ", "PG", "WMT",     # Consumo Defensivo
        "V", "MA", "JPM", "BAC", "COST", "SNY"      # Líderes Globales
    ]
    return sorted(list(set(sp500 + especiales)))

all_tickers = get_all_tickers()

@st.cache_data(ttl=3600)
def fetch_full_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y")
        if hist.empty or len(hist) < 200: return None
        
        info = stock.info
        hist['MA50'] = ta.sma(hist['Close'], length=50)
        hist['MA200'] = ta.sma(hist['Close'], length=200)
        hist['RSI_50'] = ta.rsi(hist['Close'], length=50)
        bb = ta.bbands(hist['Close'], length=20, std=2)
        macd = ta.macd(hist['Close'])
        hist = pd.concat([hist, macd, bb], axis=1)
        
        last = hist.iloc[-1]
        net_inc = info.get('netIncomeToCommon', 0)
        mkt_cap = info.get('marketCap', 0)
        de_ratio = info.get('debtToEquity', 0)

        return {
            "Ticker": ticker, "Precio": round(last['Close'], 2),
            "RSI Anual": round(last['RSI_50'], 2),
            "MACD": round(last['MACD_12_26_9'], 3), "Señal": round(last['MACDs_12_26_9'], 3),
            "Net Inc(B)": round(net_inc / 1e9, 2) if net_inc else 0,
            "D/E Ratio(%)": round(de_ratio, 2) if de_ratio else 0,
            "Mkt Cap(B)": round(mkt_cap / 1e9, 2) if mkt_cap else 0,
            "df": hist
        }
    except: return None

# --- MONITOR DE ESCANEO ---
st.subheader(f"🔍 Escaneo de Oportunidades ({len(all_tickers)} activos)")

data_list = []
if st.checkbox("🚀 Iniciar Escaneo Profundo (S&P 500 + Especiales)"):
    progress_text = "Analizando mercado..."
    progress_bar = st.progress(0, text=progress_text)
    
    for i, t in enumerate(all_tickers):
        res = fetch_full_data(t)
        if res:
            # Aplicar filtros de la barra lateral
            if (res["Mkt Cap(B)"] >= market_cap_min and 
                res["RSI Anual"] <= rsi_anual_limit and 
                res["Net Inc(B)"] >= min_net_income and 
                res["D/E Ratio(%)"] <= max_de_ratio):
                data_list.append(res)
        progress_bar.progress((i + 1) / len(all_tickers))
    progress_bar.empty()

if data_list:
    st.subheader(f"📋 Resultados del Acecho ({len(data_list)})")
    st.dataframe(pd.DataFrame(data_list).drop(columns=['df']), use_container_width=True)

    seleccion = st.selectbox("🎯 Selección para Análisis Detallado:", [d["Ticker"] for d in data_list])

    if seleccion:
        item = next(i for i in data_list if i["Ticker"] == seleccion)
        df_p = item["df"].tail(252)
        last_p = df_p.iloc[-1]
        col_bbu = [c for c in df_p.columns if c.startswith('BBU')][0]
        col_bbl = [c for c in df_p.columns if c.startswith('BBL')][0]

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
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA50'], line=dict(color='cyan', width=1), name="MA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MA200'], line=dict(color='red', width=2), name="MA200"), row=1, col=1)
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
        h_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_p['MACDh_12_26_9']]
        fig.add_trace(go.Bar(x=df_p.index, y=df_p['MACDh_12_26_9'], marker_color=h_colors, name="Hist"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACD_12_26_9'], line=dict(color='#2962ff', width=2), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p['MACDs_12_26_9'], line=dict(color='#ff6d00', width=2), name="Señal"), row=3, col=1)
        
        add_lab(fig, last_p['MACD_12_26_9'], f" M: {item['MACD']}", "#2962ff", 3, 1, 12)
        add_lab(fig, last_p['MACDs_12_26_9'], f" S: {item['Señal']}", "#ff6d00", 3, 1, -12)

        fig.update_layout(height=1000, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(r=160))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Utiliza el checkbox de arriba para escanear el mercado.")
