import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Terminal de Acecho Pro", layout="wide")

st.title("🚀 Terminal de Inversión: Gabriel Herrera")

# --- BARRA LATERAL ---
st.sidebar.header("Configuración de Filtros")
market_cap_min = st.sidebar.number_input("Market Cap Mín (Billion $)", value=30)
rsi_limit = st.sidebar.slider("RSI Máximo (Alerta)", 10, 50, 35)

# Lista Maestra (Blue Chips y Solidez tipo KO/PEP)
tickers = ["KO", "PEP", "MCD", "JNJ", "DHR", "XOM", "CVX", "PG", "JPM", "MSFT", "AAPL", "TXN", "WMT", "COST", "V", "MA"]

def get_full_analysis(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="2y") # 2 años para calcular MA200 sin problemas
        
        # Indicadores Técnicos
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['MA125'] = ta.sma(df['Close'], length=125)
        df['MA200'] = ta.sma(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # MACD
        macd = ta.macd(df['Close'])
        df = pd.concat([df, macd], axis=1)
        
        # Datos para la tabla
        last = df.iloc[-1]
        prev = df.iloc[-2]
        info = stock.info
        
        return {
            "Acción": ticker,
            "Precio": round(last['Close'], 2),
            "RSI": round(last['RSI'], 2),
            "MA50": round(last['MA50'], 2),
            "MA125": round(last['MA125'], 2),
            "MA200": round(last['MA200'], 2),
            "MACD Hist": round(last['MACDh_12_26_9'], 3),
            "Inercia": "⬆️" if last['MACDh_12_26_9'] > prev['MACDh_12_26_9'] else "⬇️",
            "Cap. Mercado (B)": round(info.get('marketCap', 0) / 1e9, 2),
            "df_completo": df # Guardamos el DF para la gráfica
        }
    except: return None

# --- PROCESAMIENTO ---
all_data = []
for t in tickers:
    res = get_full_analysis(t)
    if res: all_data.append(res)

df_final = pd.DataFrame(all_data)

# Mostrar Tabla Principal
st.subheader("📋 Monitor de Acciones Sólidas")
# Solo mostramos columnas importantes en la tabla
cols_ver = ["Acción", "Precio", "RSI", "Inercia", "MA50", "MA125", "MA200", "Cap. Mercado (B)"]
st.dataframe(df_final[cols_ver], use_container_width=True)

# --- DETALLE GRÁFICO ---
st.divider()
st.subheader("🔍 Análisis Detallado Individual")
seleccion = st.selectbox("Seleccioná una acción para ver su gráfica técnica:", tickers)

if seleccion:
    # Buscar el dataframe de la acción seleccionada
    target_data = next(item for item in all_data if item["Acción"] == seleccion)
    df_plot = target_data["df_completo"].tail(252) # Último año
    
    # Calcular Bandas de Bollinger para el gráfico
    bbands = ta.bbands(df_plot['Close'], length=20, std=2)
    df_plot = pd.concat([df_plot, bbands], axis=1)

    # Crear Gráfico con Plotly
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_heights=[0.6, 0.2, 0.2])

    # 1. Velas y Bandas
    fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'],
                                low=df_plot['Low'], close=df_plot['Close'], name="Precio"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['BBU_20_2.0'], line=dict(color='gray', width=1), name="Bollinger Sup"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['BBL_20_2.0'], line=dict(color='gray', width=1), name="Bollinger Inf"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA200'], line=dict(color='red', width=2), name="MA200"), row=1, col=1)

    # 2. RSI
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'], name="RSI", line=dict(color='purple')), row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)

    # 3. MACD
    fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['MACDh_12_26_9'], name="MACD Hist"), row=3, col=1)

    fig.update_layout(height=800, xaxis_rangeslider_visible=False, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
