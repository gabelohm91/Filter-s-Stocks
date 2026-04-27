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

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Parámetros de Ingeniería")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billones $)", value=10)
min_net_income = st.sidebar.number_input("Net Income Mínimo (Billones $)", value=0)
max_de_ratio   = st.sidebar.slider("Debt/Equity Máximo (%)", 0, 300, 200)
rsi_anual_limit = st.sidebar.slider("Filtro RSI Anual Máx", 10, 70, 65)
debug_mode     = st.sidebar.toggle("🐛 Modo Debug", value=False)

if st.sidebar.button("🔄 Refrescar Datos"):
    st.cache_data.clear()
    st.session_state["last_update"] = datetime.now().strftime("%H:%M:%S")

st.sidebar.success(f"✅ Sincronizado: {st.session_state['last_update']}")

# --- MANUAL ---
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
        - ⚠️ Precio **por debajo** de MA200 → posible ciclo bajista o empresa en crisis.
        - 🔔 MA50 cruza **por encima** de MA200 = *"Golden Cross"* → señal alcista poderosa.
        - 💀 MA50 cruza **por debajo** de MA200 = *"Death Cross"* → señal bajista severa.
        """)
        st.divider()
        st.markdown("### 📉 Bandas de Bollinger")
        st.markdown("""
        | Zona | Señal |
        |------|-------|
        | Precio toca **Banda Superior** | Activo "estirado" al alza — posible techo temporal. |
        | Precio toca **Banda Inferior** | Activo "estirado" a la baja — posible zona de rebote. |
        | Bandas muy **estrechas** | Baja volatilidad → suele preceder un movimiento explosivo. |
        > ⚠️ Las Bollinger no indican dirección por sí solas. Combínalas con RSI o MACD para confirmar.
        """)
        st.divider()
        st.markdown("### ⚡ RSI — Índice de Fuerza Relativa (período 50)")
        st.markdown("""
        | Valor RSI | Zona | Interpretación |
        |-----------|------|----------------|
        | **< 30** | 🔴 Sobreventa extrema | Pánico. Zona de compra institucional histórica. |
        | **30 – 45** | 🟡 Zona de acecho | La empresa está barata respecto a su propia historia. |
        | **45 – 55** | ⚪ Neutral | Sin señal clara. |
        | **55 – 70** | 🟢 Momentum positivo | Fuerza alcista. Mantener cautela. |
        | **> 70** | 🔴 Sobrecompra | Evitar comprar aquí — riesgo de corrección. |
        > 💡 **Regla de oro:** RSI < 35 + precio en Banda Inferior = zona de alta atención para entrada.
        """)
        st.divider()
        st.markdown("### 🌊 MACD — Convergencia/Divergencia de Medias")
        st.markdown("""
        | Evento | Significado |
        |--------|-------------|
        | MACD cruza **por encima** de Señal | 🟢 Inercia cambia a **alcista** — posible entrada. |
        | MACD cruza **por debajo** de Señal | 🔴 Inercia cambia a **bajista** — posible salida. |
        | Histograma rojo **se acorta** | Presión vendedora muriendo — posible giro próximo. |
        > 💡 El cruce es más potente cuando ocurre **por debajo de cero** → reversión desde mínimos.
        """)
        st.divider()
        st.markdown("### 📅 Variación de Precio 52 Semanas (%)")
        st.markdown("""
        | Rango | Interpretación |
        |-------|----------------|
        | **> +30%** | Momentum fuerte. Puede estar sobrecomprado o en tendencia genuina. |
        | **0% a +30%** | Zona saludable. Apreciación moderada y sostenible. |
        | **-10% a 0%** | Corrección menor. Oportunidad si los fundamentales son sólidos. |
        | **-20% a -40%** | Zona de acecho. Alta posibilidad de valor si la empresa es rentable. |
        | **< -40%** | Alerta. Investigar si es crisis estructural o sobre-reacción del mercado. |
        """)

    with tab2:
        st.markdown("## Indicadores Fundamentales")
        st.markdown("### 💵 Net Income (Beneficio Neto)")
        st.markdown("""
        | Valor | Señal |
        |-------|-------|
        | **> $5B USD** | 🏆 Empresa élite. Generación de riqueza masiva y sostenida. |
        | **$1B – $5B USD** | ✅ Empresa sólida y rentable. Fortaleza operativa clara. |
        | **$100M – $1B USD** | 🟡 Rentable en escala media. Aceptable según sector. |
        | **$0 – $100M USD** | ⚠️ Rentabilidad marginal. Revisar si la tendencia es creciente. |
        | **Negativo** | 🔴 Destruye capital. Solo válido en startups con plan claro de expansión. |
        > 💡 **Lo más importante es la tendencia:** ¿Crece año a año?
        """)
        st.divider()
        st.markdown("### ⚖️ Debt / Equity (Deuda sobre Patrimonio)")
        st.markdown("""
        | Ratio | Interpretación |
        |-------|----------------|
        | **< 0.5** | 🟢 Muy sólida. Poca deuda, gran independencia financiera. |
        | **0.5 – 1.0** | ✅ Nivel saludable y común en empresas maduras. |
        | **1.0 – 2.0** | 🟡 Deuda elevada pero manejable con buen flujo de caja. |
        | **> 2.0** | 🔴 Riesgo alto. Depende del crédito para operar. |
        | **Negativo** | ⚠️ Patrimonio negativo — crisis o buybacks extremos. |
        > ⚠️ El D/E varía por sector. Bancos y utilities tienen D/E alto de forma natural.
        """)

    with tab3:
        st.markdown("## 🧭 Guía Rápida: Semáforo de Señales")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("### 🔴 Evitar / Precaución")
            st.markdown("""
            - RSI **> 70** (sobrecompra)
            - Precio **por debajo** de MA200
            - MACD cruza **a la baja**
            - Net Income **negativo o cayendo**
            - Debt/Equity **> 2.0**
            - Precio 52W **< -40%** sin explicación
            """)
        with c2:
            st.markdown("### 🟡 Vigilar / Analizar")
            st.markdown("""
            - RSI entre **35 – 50**
            - Precio cerca de MA50
            - Histograma MACD **acortándose**
            - Net Income **$100M – $1B**
            - Debt/Equity **1.0 – 2.0**
            - Precio 52W entre **-10% y -30%**
            """)
        with c3:
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
        st.info("💡 La señal más poderosa es cuando **técnico y fundamental coinciden**: empresa sólida con RSI en sobreventa y MACD girando al alza.")


# ─────────────────────────────────────────────
# UNIVERSO DE ACTIVOS
# ─────────────────────────────────────────────
@st.cache_data(ttl=86400)
def get_all_tickers():
    """Combina S&P 500 + componentes QQQ + lista de valor y ETFs."""

    # 1. S&P 500 desde Wikipedia
    sp500 = []
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        sp500 = pd.read_html(url)[0]["Symbol"].tolist()
        # Wikipedia usa puntos en algunos tickers (BRK.B → BRK-B para yfinance)
        sp500 = [t.replace(".", "-") for t in sp500]
    except Exception as e:
        st.sidebar.warning(f"S&P500 Wikipedia falló: {e}")

    # 2. Componentes QQQ desde Wikipedia
    qqq = []
    try:
        url_qqq = "https://en.wikipedia.org/wiki/Invesco_QQQ_Trust"
        tables = pd.read_html(url_qqq)
        for tbl in tables:
            for col in tbl.columns:
                if "ticker" in str(col).lower() or "symbol" in str(col).lower():
                    qqq = tbl[col].dropna().tolist()
                    break
            if qqq:
                break
    except:
        pass  # Si falla, no importa — la mayoría ya estarán en S&P500

    # 3. Lista curada: valor, dividendos, ETFs y globales
    curados = [
        # ETFs de calidad
        "VOO", "QQQ", "SCHD", "VGT", "VXUS", "VUG", "VYM", "DGRO",
        "NOBL", "HDV", "JEPI", "DIVO", "SPLG", "IVV", "SPY",
        # Valor clásico y aristócratas del dividendo
        "KO", "PEP", "WMT", "PG", "JNJ", "MCD", "CVX", "XOM",
        "JPM", "V", "MA", "TXN", "ABBV", "LOW", "SBUX", "NEE",
        "O",   # Realty Income — REIT de dividendo mensual
        "DHR", "MMM", "EMR", "ITW", "GPC", "SWK", "CLX", "MKC",
        # Tecnología y semiconductores
        "MSFT", "AAPL", "NVDA", "AVGO", "ASML", "TSM", "ARM", "QCOM",
        "AMAT", "LRCX", "KLAC", "MRVL",
        # Globales y ADRs
        "BHP", "SNY", "MCHI", "NVO", "SAP", "TM", "UL", "DEO",
        # Growth de calidad
        "COST", "AMZN", "GOOGL", "META", "CRM", "NOW", "ADBE",
    ]

    universo = sorted(list(set(sp500 + qqq + curados)))
    return universo


# ─────────────────────────────────────────────
# DESCARGA Y CÁLCULO DE INDICADORES
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_full_data(ticker):
    """Retorna (dict_con_datos, None) o (None, motivo_str)."""
    try:
        stock = yf.Ticker(ticker)
        hist  = stock.history(period="2y")

        if hist is None or hist.empty:
            return None, "Sin datos históricos"
        if len(hist) < 200:
            return None, f"Historial corto ({len(hist)} días)"

        info = stock.info

        hist["MA50"]   = ta.sma(hist["Close"], length=50)
        hist["MA200"]  = ta.sma(hist["Close"], length=200)
        hist["RSI_50"] = ta.rsi(hist["Close"], length=50)
        bb   = ta.bbands(hist["Close"], length=20, std=2)
        macd = ta.macd(hist["Close"])
        hist = pd.concat([hist, macd, bb], axis=1)

        last = hist.iloc[-1]

        # Validar que los indicadores calcularon
        if pd.isna(last.get("RSI_50")) or pd.isna(last.get("MACD_12_26_9")):
            return None, "Indicadores NaN"

        # Fundamentales — proteger contra None
        net_inc  = info.get("netIncomeToCommon", 0) or 0
        mkt_cap  = info.get("marketCap", 0) or 0
        de_ratio = info.get("debtToEquity", 0) or 0

        # Variación 52 semanas
        precio_52w = hist["Close"].iloc[-252] if len(hist) >= 252 else hist["Close"].iloc[0]
        cambio_52w = round(((last["Close"] - precio_52w) / precio_52w) * 100, 2)

        return {
            "Ticker":       ticker,
            "Precio":       round(last["Close"], 2),
            "RSI Anual":    round(last["RSI_50"], 2),
            "MACD":         round(last["MACD_12_26_9"], 3),
            "Señal MACD":   round(last["MACDs_12_26_9"], 3),
            "Net Inc(B)":   round(net_inc / 1e9, 2),
            "D/E Ratio(%)": round(de_ratio, 2),
            "Mkt Cap(B)":   round(mkt_cap / 1e9, 2),
            "52W %":        cambio_52w,
            "df":           hist,
        }, None

    except Exception as e:
        return None, str(e)


# ─────────────────────────────────────────────
# ESCANEO
# ─────────────────────────────────────────────
all_tickers = get_all_tickers()
st.subheader(f"🔍 Escaneo de Oportunidades — {len(all_tickers)} activos en universo")

data_list  = []
log_debug  = []
stats      = {"procesados": 0, "ok": 0, "sin_datos": 0, "filtrados": 0}

if st.checkbox("🚀 Iniciar Escaneo (S&P 500 + QQQ + Valor)"):
    barra = st.progress(0, text="Iniciando...")

    for i, t in enumerate(all_tickers):
        barra.progress((i + 1) / len(all_tickers), text=f"[{i+1}/{len(all_tickers)}] {t}")
        res, err = fetch_full_data(t)
        stats["procesados"] += 1

        if res is None:
            stats["sin_datos"] += 1
            log_debug.append(f"❌ {t}: {err}")
            continue

        stats["ok"] += 1

        # ── Filtros ──────────────────────────────────────────────────────
        # Los ETFs devuelven D/E = 0 (no aplica), dejarlos pasar siempre
        es_etf = res["D/E Ratio(%)"] == 0 and res["Net Inc(B)"] == 0
        de_ok  = es_etf or (res["D/E Ratio(%)"] <= max_de_ratio)
        cap_ok = res["Mkt Cap(B)"] >= market_cap_min
        rsi_ok = res["RSI Anual"] <= rsi_anual_limit
        inc_ok = es_etf or (res["Net Inc(B)"] >= min_net_income)

        if cap_ok and rsi_ok and inc_ok and de_ok:
            data_list.append(res)
        else:
            stats["filtrados"] += 1
            motivos = []
            if not cap_ok: motivos.append(f"Cap={res['Mkt Cap(B)']}B < {market_cap_min}B")
            if not rsi_ok: motivos.append(f"RSI={res['RSI Anual']} > {rsi_anual_limit}")
            if not inc_ok: motivos.append(f"NetInc={res['Net Inc(B)']}B < {min_net_income}B")
            if not de_ok:  motivos.append(f"D/E={res['D/E Ratio(%)']}% > {max_de_ratio}%")
            log_debug.append(f"⚠️ {t}: {' | '.join(motivos)}")

    barra.empty()

    # Métricas resumen
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📊 Procesados",      stats["procesados"])
    m2.metric("✅ Con datos",        stats["ok"])
    m3.metric("🎯 Pasaron filtros",  len(data_list))
    m4.metric("🚫 Sin datos/Error",  stats["sin_datos"])

    if debug_mode and log_debug:
        with st.expander(f"🐛 Log ({len(log_debug)} entradas)"):
            for line in log_debug[:200]:
                st.text(line)

    if not data_list:
        st.error("❌ Ningún activo pasó los filtros.")
        st.markdown(f"""
        | Filtro | Valor actual | Sugerido |
        |--------|-------------|----------|
        | RSI Máx | **{rsi_anual_limit}** | Sube a **70** |
        | Mkt Cap Mín | **{market_cap_min}B** | Baja a **5** |
        | Net Income Mín | **{min_net_income}B** | Deja en **0** |
        | D/E Máx | **{max_de_ratio}%** | Sube a **300%** |
        """)
        st.info("Activa **Modo Debug** en la barra lateral para ver el detalle de cada ticker.")
        st.stop()


# ─────────────────────────────────────────────
# TABLA + GRÁFICO
# ─────────────────────────────────────────────
if data_list:
    st.subheader(f"📋 Resultados del Acecho — {len(data_list)} activos")
    st.dataframe(
        pd.DataFrame(data_list).drop(columns=["df"]),
        use_container_width=True
    )

    seleccion = st.selectbox(
        "🎯 Selección para Análisis Detallado:",
        [d["Ticker"] for d in data_list],
        key="ticker_seleccionado"
    )

    if seleccion:
        item   = next(i for i in data_list if i["Ticker"] == seleccion)
        df_p   = item["df"].tail(252).copy()
        last_p = df_p.iloc[-1]

        bbu_cols = [c for c in df_p.columns if c.startswith("BBU")]
        bbl_cols = [c for c in df_p.columns if c.startswith("BBL")]
        if not bbu_cols or not bbl_cols:
            st.error("Columnas Bollinger no encontradas — presiona 🔄 Refrescar Datos.")
            st.stop()

        col_bbu, col_bbl = bbu_cols[0], bbl_cols[0]

        fig = make_subplots(
            rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.07,
            row_heights=[0.5, 0.2, 0.3],
            subplot_titles=(
                "PRECIO Y SOPORTES ESTRUCTURALES",
                "RSI ANUAL (50) — TIMING",
                "INERCIA (MACD)"
            )
        )

        def add_lab(fig, y, text, color, row, offset=0):
            yref_map = {1: "y", 2: "y2", 3: "y3"}
            xref_map = {1: "x", 2: "x2", 3: "x3"}
            fig.add_annotation(
                x=df_p.index[-1], y=float(y) + offset, text=text,
                showarrow=False, xanchor="left", xshift=15,
                font=dict(size=12, color=color, family="Arial Black"),
                bgcolor="rgba(0,0,0,0.8)",
                xref=xref_map[row], yref=yref_map[row]
            )

        # 1 ── PRECIO
        fig.add_trace(go.Candlestick(
            x=df_p.index, open=df_p["Open"], high=df_p["High"],
            low=df_p["Low"], close=df_p["Close"], name="Precio"
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_p.index, y=df_p["MA50"],
            line=dict(color="cyan", width=1), name="MA50"
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_p.index, y=df_p["MA200"],
            line=dict(color="red", width=2), name="MA200"
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_p.index, y=df_p[col_bbu],
            line=dict(color="rgba(173,216,230,0.3)", width=1), name="B.Sup"
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_p.index, y=df_p[col_bbl],
            line=dict(color="rgba(173,216,230,0.3)", width=1),
            fill="tonexty", fillcolor="rgba(173,216,230,0.05)", name="B.Inf"
        ), row=1, col=1)

        add_lab(fig, last_p["Close"],   f" PRECIO: ${item['Precio']}", "white",     1)
        add_lab(fig, last_p[col_bbu],   f" BS: {round(float(last_p[col_bbu]),2)}",  "lightblue", 1)
        add_lab(fig, last_p[col_bbl],   f" BI: {round(float(last_p[col_bbl]),2)}",  "lightblue", 1)

        # 2 ── RSI
        fig.add_trace(go.Scatter(
            x=df_p.index, y=df_p["RSI_50"],
            line=dict(color="#C084FC", width=2), name="RSI 50"
        ), row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green",
                      annotation_text="Sobreventa 30", row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red",
                      annotation_text="Sobrecompra 70", row=2, col=1)
        fig.update_yaxes(range=[0, 100], row=2, col=1)
        add_lab(fig, last_p["RSI_50"], f" RSI(50): {item['RSI Anual']}", "#C084FC", 2)

        # 3 ── MACD
        h_colors = ["#26a69a" if v >= 0 else "#ef5350" for v in df_p["MACDh_12_26_9"]]
        fig.add_trace(go.Bar(
            x=df_p.index, y=df_p["MACDh_12_26_9"],
            marker_color=h_colors, name="Histograma"
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df_p.index, y=df_p["MACD_12_26_9"],
            line=dict(color="#2962ff", width=2), name="MACD"
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df_p.index, y=df_p["MACDs_12_26_9"],
            line=dict(color="#ff6d00", width=2), name="Señal"
        ), row=3, col=1)

        add_lab(fig, last_p["MACD_12_26_9"],  f" M: {item['MACD']}",       "#2962ff", 3)
        add_lab(fig, last_p["MACDs_12_26_9"], f" S: {item['Señal MACD']}", "#ff6d00", 3)

        fig.update_layout(
            height=1000, template="plotly_dark",
            xaxis_rangeslider_visible=False,
            margin=dict(r=180),
            title=dict(text=f"📊 {seleccion} — Radiografía Técnica", font=dict(size=18))
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    if not st.session_state.get("ticker_seleccionado"):
        st.info("Activa el checkbox de arriba para escanear el mercado.")
