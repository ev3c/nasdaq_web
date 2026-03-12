"""
NASDAQ Magnificent Seven Tracker
Aplicación para monitorear las 7 grandes tecnológicas del NASDAQ
"""

import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import os
import base64
import pytz
import calendar

# Configuración de la página
st.set_page_config(
    page_title="NASDAQ Magnificent 7 Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"  # Colapsado por defecto (mejor para móviles)
)

# Colores para incrementos y decrementos
COLORS = {
    "up": "#4CAF50",        # Verde para incrementos
    "down": "#E53935",      # Rojo para decrementos
    "up_light": "#C8E6C9",  # Verde claro
    "down_light": "#FFCDD2" # Rojo claro
}

# CSS personalizado para un diseño moderno con colores pastel - RESPONSIVE
st.markdown("""
<style>
    /* Fuentes personalizadas */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
    
    /* Variables de color - Tema pastel suave */
    :root {
        --bg-primary: #FDF6F0;
        --bg-secondary: #FFFFFF;
        --bg-card: #FFFFFF;
        --accent-lavender: #E6D5F2;
        --accent-mint: #D5F0E3;
        --accent-peach: #FFDDC1;
        --accent-sky: #D4EAF7;
        --accent-rose: #FFE4E6;
        --color-up: #4CAF50;
        --color-up-light: #C8E6C9;
        --color-up-bg: #E8F5E9;
        --color-down: #E53935;
        --color-down-light: #FFCDD2;
        --color-down-bg: #FFEBEE;
        --text-primary: #37474F;
        --text-secondary: #78909C;
        --border-color: #ECEFF1;
        --shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
    }
    
    /* Fondo principal con gradiente pastel */
    .stApp {
        background: linear-gradient(135deg, #FDF6F0 0%, #F5EBE0 25%, #FAF3E8 50%, #F8F0E5 75%, #FDF6F0 100%);
        font-family: 'Nunito', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important;
        color: #37474F !important;
        -webkit-text-fill-color: #37474F !important;
    }
    
    h1 {
        background: linear-gradient(120deg, #B39DDB 0%, #90CAF9 50%, #80CBC4 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-weight: 800 !important;
    }
    
    /* Métricas personalizadas */
    [data-testid="stMetricValue"] {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important;
    }
    
    /* Delta colors */
    [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Up"] {
        color: #4CAF50 !important;
    }
    
    [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Down"] {
        color: #E53935 !important;
    }
    
    /* Metric containers - compactos */
    [data-testid="stMetric"] {
        background: white;
        padding: 0.6rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        border: 1px solid #ECEFF1;
    }
    
    /* Reducir espaciado general */
    .block-container {
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Ocultar sidebar completamente */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        flex-wrap: wrap;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 12px;
        border: 2px solid #ECEFF1;
        color: var(--text-secondary);
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        font-size: 0.9rem;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        border-color: #B39DDB;
        background: #F3E5F5;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #B39DDB 0%, #90CAF9 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(179, 157, 219, 0.4);
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, #B39DDB 0%, #90CAF9 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-family: 'Nunito', sans-serif;
        font-weight: 700;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(179, 157, 219, 0.35);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(179, 157, 219, 0.5);
    }
    
    /* Inputs */
    .stNumberInput input, .stTextInput input, .stSelectbox > div > div {
        background: white !important;
        border: 2px solid #ECEFF1 !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    .stNumberInput input:focus, .stTextInput input:focus {
        border-color: #B39DDB !important;
        box-shadow: 0 0 0 3px rgba(179, 157, 219, 0.2) !important;
    }
    
    /* DataFrames */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--shadow);
        border: 1px solid #ECEFF1;
    }
    
    /* Alertas personalizadas - Verde para subidas */
    .alert-up {
        background: linear-gradient(90deg, #E8F5E9 0%, rgba(232, 245, 233, 0.4) 100%);
        border-left: 4px solid #4CAF50;
        padding: 0.8rem 1rem;
        border-radius: 0 12px 12px 0;
        margin: 0.5rem 0;
        color: var(--text-primary);
        font-size: 0.9rem;
    }
    
    /* Alertas personalizadas - Rojo para bajadas */
    .alert-down {
        background: linear-gradient(90deg, #FFEBEE 0%, rgba(255, 235, 238, 0.4) 100%);
        border-left: 4px solid #E53935;
        padding: 0.8rem 1rem;
        border-radius: 0 12px 12px 0;
        margin: 0.5rem 0;
        color: var(--text-primary);
        font-size: 0.9rem;
    }
    
    /* Header principal compacto */
    .main-header {
        text-align: center;
        padding: 0.5rem 0;
        margin-bottom: 0.5rem;
    }
    
    .stock-card {
        background: white;
        border: 2px solid #ECEFF1;
        border-radius: 16px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
    }
    
    .stock-card:hover {
        border-color: #B39DDB;
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(179, 157, 219, 0.2);
    }
    
    /* Colores de incremento/decremento */
    .positive {
        color: #4CAF50 !important;
        font-weight: 700;
    }
    
    .negative {
        color: #E53935 !important;
        font-weight: 700;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 12px;
        border: 2px solid #ECEFF1;
        font-weight: 600;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 12px;
        border: none;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #B39DDB !important;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Radio buttons horizontales como pills */
    [data-testid="stRadio"] > div {
        flex-wrap: wrap;
        gap: 0.4rem;
    }
    
    [data-testid="stRadio"] label {
        background: white;
        border: 2px solid #ECEFF1;
        border-radius: 20px;
        padding: 0.4rem 0.8rem;
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        min-width: 40px;
        text-align: center;
    }
    
    [data-testid="stRadio"] label:hover {
        border-color: #B39DDB;
        background: #F3E5F5;
    }
    
    [data-testid="stRadio"] label[data-checked="true"] {
        background: linear-gradient(135deg, #B39DDB 0%, #90CAF9 100%);
        color: white;
        border-color: transparent;
    }
    
    /* Ocultar el círculo del radio */
    [data-testid="stRadio"] input {
        display: none;
    }
    
    /* Botones de período más compactos */
    .period-selector [data-testid="stRadio"] > div {
        gap: 0.25rem;
    }
    
    .period-selector [data-testid="stRadio"] label {
        padding: 0.25rem 0.5rem;
        font-size: 0.75rem;
        min-width: 32px;
        border-radius: 14px;
        border-width: 1.5px;
    }
    
    /* ============================================
       RESPONSIVE - MOBILE STYLES (< 768px)
       ============================================ */
    @media (max-width: 768px) {
        /* Contenedor principal más compacto */
        .block-container {
            padding-top: 0.5rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            max-width: 100% !important;
        }
        
        /* Header más pequeño */
        h1 {
            font-size: 1.3rem !important;
        }
        
        h2, h3 {
            font-size: 1.1rem !important;
        }
        
        /* Métricas más compactas en móvil */
        [data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
        }
        
        [data-testid="stMetricDelta"] {
            font-size: 0.8rem !important;
        }
        
        [data-testid="stMetric"] {
            padding: 0.4rem;
            border-radius: 10px;
        }
        
        /* Columnas horizontales en móvil - Grid de 2x4 o scroll horizontal */
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.3rem !important;
        }
        
        [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
            flex: 0 0 calc(50% - 0.2rem) !important;
            min-width: calc(50% - 0.2rem) !important;
        }
        
        /* Tabs compactas en móvil */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            justify-content: center;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px;
            font-size: 0.75rem;
            border-radius: 10px;
            flex: 1;
            min-width: 0;
            text-align: center;
        }
        
        /* Radio buttons más compactos en móvil */
        [data-testid="stRadio"] label {
            padding: 0.35rem 0.6rem;
            font-size: 0.75rem;
            min-width: 35px;
            border-radius: 16px;
        }
        
        /* Botones de período aún más pequeños en móvil */
        .period-selector [data-testid="stRadio"] label {
            padding: 0.2rem 0.4rem;
            font-size: 0.65rem;
            min-width: 28px;
            border-radius: 12px;
        }
        
        /* Botones más pequeños */
        .stButton > button {
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
            border-radius: 10px;
        }
        
        /* Alertas más compactas */
        .alert-up, .alert-down {
            padding: 0.6rem 0.8rem;
            font-size: 0.8rem;
            border-radius: 0 10px 10px 0;
            margin: 0.4rem 0;
        }
        
        /* Stock cards más pequeñas */
        .stock-card {
            padding: 0.8rem;
            border-radius: 12px;
            margin: 0.3rem 0;
        }
        
        /* DataFrames con scroll horizontal */
        .stDataFrame {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch;
        }
        
        /* Gráficos responsive */
        [data-testid="stPlotlyChart"] {
            width: 100% !important;
        }
        
        /* Selectbox y inputs más grandes para touch */
        .stSelectbox > div > div,
        .stNumberInput input,
        .stTextInput input {
            min-height: 44px !important;
            font-size: 16px !important; /* Evita zoom en iOS */
        }
        
        /* Expanders más compactos */
        .streamlit-expanderHeader {
            font-size: 0.85rem;
            padding: 0.5rem;
        }
        
        /* Leyenda de colores más compacta */
        .color-legend {
            font-size: 0.75rem !important;
        }
    }
    
    /* ============================================
       EXTRA SMALL SCREENS (< 480px)
       ============================================ */
    @media (max-width: 480px) {
        h1 {
            font-size: 1.1rem !important;
        }
        
        /* Métricas en columna única si es muy pequeño */
        [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
            flex: 0 0 calc(50% - 0.15rem) !important;
            min-width: calc(50% - 0.15rem) !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.7rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 6px 8px;
            font-size: 0.7rem;
        }
        
        .alert-up, .alert-down {
            padding: 0.5rem 0.6rem;
            font-size: 0.75rem;
        }
    }
    
    /* ============================================
       TABLET STYLES (768px - 1024px)
       ============================================ */
    @media (min-width: 769px) and (max-width: 1024px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.3rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 10px 16px;
            font-size: 0.85rem;
        }
    }
    
    /* Touch-friendly improvements */
    @media (hover: none) and (pointer: coarse) {
        /* Disable hover effects on touch devices */
        .stock-card:hover {
            transform: none;
        }
        
        .stButton > button:hover {
            transform: none;
        }
        
        /* Larger touch targets */
        .stSelectbox,
        .stNumberInput,
        .stTextInput {
            min-height: 48px;
        }
    }
    
    /* ============================================
       CALENDARIO RESPONSIVE
       ============================================ */
    
    /* Contenedor del calendario */
    .calendar-container {
        background: white;
        border-radius: 12px;
        padding: 12px;
        border: 1px solid #ECEFF1;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    /* Botones del calendario más compactos */
    .calendar-container .stButton > button {
        padding: 4px 2px !important;
        min-height: 36px !important;
        font-size: 0.85rem !important;
        border-radius: 8px !important;
    }
    
    /* Header del calendario */
    .calendar-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    
    /* Días de la semana header */
    .calendar-weekdays {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 2px;
        text-align: center;
        margin-bottom: 4px;
    }
    
    .calendar-weekdays div {
        font-weight: 700;
        color: #78909C;
        font-size: 0.7rem;
        padding: 4px 2px;
    }
    
    /* Mobile: Calendario ocupa todo el ancho */
    @media (max-width: 768px) {
        /* Botones del calendario más pequeños en móvil */
        .calendar-container .stButton > button {
            padding: 2px 1px !important;
            min-height: 32px !important;
            font-size: 0.75rem !important;
            border-radius: 6px !important;
        }
        
        /* Navegación del mes compacta */
        .calendar-nav .stButton > button {
            padding: 4px 8px !important;
            min-height: 28px !important;
            font-size: 0.9rem !important;
        }
        
        /* Columnas del calendario sin gap */
        .calendar-days [data-testid="stHorizontalBlock"] {
            gap: 2px !important;
        }
        
        .calendar-days [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
            flex: 1 !important;
            min-width: 0 !important;
            padding: 1px !important;
        }
        
        /* Métricas del histórico compactas */
        .history-metrics [data-testid="stMetric"] {
            padding: 6px !important;
        }
        
        .history-metrics [data-testid="stMetricValue"] {
            font-size: 0.95rem !important;
        }
        
        .history-metrics [data-testid="stMetricLabel"] {
            font-size: 0.7rem !important;
        }
        
        /* Cards de ganancia más compactas */
        .history-card {
            padding: 8px !important;
            margin-top: 6px !important;
        }
        
        .history-card span:first-child {
            font-size: 0.75rem !important;
        }
        
        .history-card span:last-child {
            font-size: 0.95rem !important;
        }
    }
    
    /* Extra small screens */
    @media (max-width: 480px) {
        .calendar-container .stButton > button {
            padding: 1px 0px !important;
            min-height: 28px !important;
            font-size: 0.7rem !important;
            border-radius: 4px !important;
        }
        
        .calendar-weekdays div {
            font-size: 0.6rem;
            padding: 2px 1px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Definición de las acciones Magnificent Seven con colores únicos y distintivos
MAGNIFICENT_SEVEN = {
    "GOOGL": {"name": "Alphabet (Google)", "emoji": "🔍", "color": "#5C9CE5"},  # Azul Google
    "AMZN": {"name": "Amazon", "emoji": "📦", "color": "#FF9F43"},              # Naranja Amazon
    "AAPL": {"name": "Apple", "emoji": "🍎", "color": "#A3A8B8"},               # Gris elegante Apple
    "META": {"name": "Meta (Facebook)", "emoji": "👤", "color": "#0A84FF"},     # Azul Meta
    "MSFT": {"name": "Microsoft", "emoji": "🪟", "color": "#00D2D3"},           # Turquesa Microsoft
    "NVDA": {"name": "NVIDIA", "emoji": "🎮", "color": "#78C850"},              # Verde NVIDIA
    "TSLA": {"name": "Tesla", "emoji": "🚗", "color": "#E84545"}                # Rojo Tesla
}

# Top 5 Criptomonedas
TOP_CRYPTO = {
    "BTC-USD": {"name": "Bitcoin", "emoji": "₿", "color": "#F7931A"},           # Naranja Bitcoin
    "ETH-USD": {"name": "Ethereum", "emoji": "⟠", "color": "#627EEA"},          # Azul Ethereum
    "BNB-USD": {"name": "Binance Coin", "emoji": "🔶", "color": "#F3BA2F"},     # Amarillo Binance
    "XRP-USD": {"name": "XRP (Ripple)", "emoji": "💧", "color": "#00AAE4"},     # Azul Ripple
    "SOL-USD": {"name": "Solana", "emoji": "◎", "color": "#9945FF"}             # Púrpura Solana
}

PORTFOLIO_FILE = "portfolio.json"
ALERTS_FILE = "alerts.json"
PORTFOLIO_HISTORY_FILE = "portfolio_history.json"


def load_portfolio():
    """Cargar portfolio desde archivo JSON"""
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_portfolio(portfolio):
    """Guardar portfolio en archivo JSON"""
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=2)


def load_portfolio_history():
    """Cargar histórico del portfolio desde archivo JSON"""
    if os.path.exists(PORTFOLIO_HISTORY_FILE):
        with open(PORTFOLIO_HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_portfolio_history(history):
    """Guardar histórico del portfolio en archivo JSON"""
    with open(PORTFOLIO_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def save_daily_snapshot(total_invested, total_current, total_gain, total_gain_pct, daily_gain, daily_pct):
    """Guardar snapshot diario del portfolio"""
    today = datetime.now().strftime("%Y-%m-%d")
    history = load_portfolio_history()
    
    history[today] = {
        "invested": total_invested,
        "current_value": total_current,
        "total_gain": total_gain,
        "total_gain_pct": total_gain_pct,
        "daily_gain": daily_gain,
        "daily_gain_pct": daily_pct,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    save_portfolio_history(history)


def load_alerts():
    """Cargar alertas desde archivo JSON"""
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_alerts(alerts):
    """Guardar alertas en archivo JSON"""
    with open(ALERTS_FILE, 'w') as f:
        json.dump(alerts, f, indent=2)


def create_download_link(data, filename, text):
    """Crear enlace de descarga para datos JSON"""
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    b64 = base64.b64encode(json_str.encode()).decode()
    return f'<a href="data:application/json;base64,{b64}" download="{filename}" style="text-decoration: none;">{text}</a>'


def export_data_button(data, filename, button_text, key):
    """Botón para exportar datos como JSON"""
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    st.download_button(
        label=button_text,
        data=json_str,
        file_name=filename,
        mime="application/json",
        key=key,
        use_container_width=True
    )


@st.cache_data(ttl=300)  # Cache de 5 minutos
def get_stock_data(symbols, period="1mo"):
    """Obtener datos de acciones"""
    data = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            
            # Para períodos cortos, usar intervalos intradía
            if period == "1d":
                # Obtener datos intradía con intervalo de 5 minutos
                hist = ticker.history(period="1d", interval="5m")
                # Si no hay datos del día actual (mercado cerrado), obtener último día de trading
                if len(hist) == 0:
                    hist = ticker.history(period="5d", interval="5m")
                    # Filtrar para mostrar solo el último día con datos
                    if len(hist) > 0:
                        last_date = hist.index[-1].date()
                        hist = hist[hist.index.date == last_date]
            elif period == "5d":
                # Para 5 días, usar intervalo de 15 minutos
                hist = ticker.history(period="5d", interval="15m")
            else:
                hist = ticker.history(period=period)
            
            info = ticker.info
            data[symbol] = {
                "history": hist,
                "info": info,
                "current_price": hist['Close'].iloc[-1] if len(hist) > 0 else 0,
                "prev_close": info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else 0),
                "market_cap": info.get('marketCap', 0),
                "volume": info.get('volume', 0),
                "pe_ratio": info.get('trailingPE', 0),
                "52w_high": info.get('fiftyTwoWeekHigh', 0),
                "52w_low": info.get('fiftyTwoWeekLow', 0)
            }
        except Exception as e:
            st.error(f"Error obteniendo datos de {symbol}: {e}")
            data[symbol] = None
    return data


def calculate_change(current, previous):
    """Calcular cambio porcentual"""
    if previous and previous != 0:
        return ((current - previous) / previous) * 100
    return 0


@st.cache_data(ttl=3600)
def get_historical_prices(symbols, target_date):
    """Obtener precios de cierre históricos para una fecha específica"""
    prices = {}
    target = datetime.strptime(target_date, "%Y-%m-%d")
    start_date = target - timedelta(days=5)
    end_date = target + timedelta(days=1)
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
            
            if len(hist) > 0:
                hist.index = hist.index.tz_localize(None) if hist.index.tz else hist.index
                target_prices = hist[hist.index.date <= target.date()]
                
                if len(target_prices) > 0:
                    close_price = target_prices['Close'].iloc[-1]
                    prev_close = target_prices['Close'].iloc[-2] if len(target_prices) > 1 else close_price
                    actual_date = target_prices.index[-1].strftime("%Y-%m-%d")
                    
                    prices[symbol] = {
                        "close": close_price,
                        "prev_close": prev_close,
                        "actual_date": actual_date
                    }
                else:
                    prices[symbol] = None
            else:
                prices[symbol] = None
        except Exception as e:
            prices[symbol] = None
    
    return prices


def format_market_cap(value):
    """Formatear capitalización de mercado"""
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    elif value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    return f"${value:,.0f}"


def get_change_color(change):
    """Obtener color basado en el cambio: verde para positivo, rojo para negativo"""
    return COLORS["up"] if change >= 0 else COLORS["down"]


def create_price_chart(data, symbols, title="Evolución de Precios", period="1mo"):
    """Crear gráfico de evolución de precios - Color único por acción"""
    fig = go.Figure()
    
    has_data = False
    reference_date = None
    spain_tz = pytz.timezone('Europe/Madrid')
    
    for symbol in symbols:
        if data[symbol] and len(data[symbol]["history"]) > 0:
            has_data = True
            hist = data[symbol]["history"].copy()
            first_price = hist['Close'].iloc[0]
            last_price = hist['Close'].iloc[-1]
            change = ((last_price - first_price) / first_price) * 100
            # Usar el color único de cada acción
            line_color = MAGNIFICENT_SEVEN[symbol]['color']
            # Indicador de subida/bajada en el nombre
            arrow = "▲" if change >= 0 else "▼"
            
            # Convertir a hora española para períodos cortos
            if period in ["1d", "5d"]:
                hist.index = hist.index.tz_convert(spain_tz)
            
            # Guardar fecha de referencia para el rango del eje X
            if reference_date is None and period == "1d":
                reference_date = hist.index[-1].date()
            
            # Formato de hover según período
            if period in ["1d", "5d"]:
                hover_template = (f"<b>{symbol}</b><br>" +
                                 "Hora: %{x|%H:%M}<br>" +
                                 "Precio: $%{y:.2f}<extra></extra>")
            else:
                hover_template = (f"<b>{symbol}</b><br>" +
                                 "Fecha: %{x|%d/%m/%Y}<br>" +
                                 "Precio: $%{y:.2f}<extra></extra>")
            
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['Close'],
                mode='lines',
                name=f"{symbol} {arrow} {change:+.1f}%",
                line=dict(color=line_color, width=3),
                hovertemplate=hover_template
            ))
    
    # Configurar formato del eje X según período
    if period == "1d":
        # Para 1D: mostrar rango completo 15:30-22:00 hora España
        if reference_date:
            # Rango en hora española
            market_open = datetime.combine(reference_date, datetime.strptime("15:30", "%H:%M").time())
            market_close = datetime.combine(reference_date, datetime.strptime("22:00", "%H:%M").time())
            market_open = spain_tz.localize(market_open)
            market_close = spain_tz.localize(market_close)
            
            xaxis_config = dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(0,0,0,0.06)',
                tickfont=dict(color='#78909C', family='Nunito', size=9),
                tickformat="%H:%M",
                nticks=8,  # Número fijo de marcas para evitar overflow
                range=[market_open, market_close],
                fixedrange=True,  # Evitar zoom/pan que cause scroll
                constrain='domain',
            )
        else:
            xaxis_config = dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(0,0,0,0.06)',
                tickfont=dict(color='#78909C', family='Nunito', size=9),
                tickformat="%H:%M",
                nticks=8,
                fixedrange=True,
                constrain='domain',
            )
    elif period == "5d":
        xaxis_config = dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.06)',
            tickfont=dict(color='#78909C', family='Nunito', size=9),
            tickformat="%d/%m %H:%M",
            nticks=10,
            fixedrange=True,
            constrain='domain',
        )
    else:
        xaxis_config = dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.06)',
            tickfont=dict(color='#78909C', family='Nunito', size=10)
        )
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#37474F', family='Nunito')),
        template='plotly_white',
        paper_bgcolor='rgba(255,255,255,0)',
        plot_bgcolor='rgba(253,246,240,0.5)',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color='#37474F', size=9, family='Nunito'),
            itemwidth=30
        ),
        xaxis=xaxis_config,
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.06)',
            tickfont=dict(color='#78909C', family='Nunito', size=10),
            tickprefix="$"
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        autosize=True
    )
    
    # Mensaje si no hay datos
    if not has_data:
        fig.add_annotation(
            text="No hay datos disponibles para este período.<br>El mercado NASDAQ opera de 15:30 a 22:00 (hora España).",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color='#78909C'),
            align="center"
        )
    
    return fig


def create_comparison_chart(data, symbols, period="1mo"):
    """Crear gráfico de comparación normalizado - Color único por acción"""
    fig = go.Figure()
    
    has_data = False
    reference_date = None
    spain_tz = pytz.timezone('Europe/Madrid')
    
    for symbol in symbols:
        if data[symbol] and len(data[symbol]["history"]) > 0:
            has_data = True
            hist = data[symbol]["history"].copy()
            # Normalizar a porcentaje desde el inicio
            normalized = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
            final_change = normalized.iloc[-1]
            
            # Convertir a hora española para períodos cortos
            if period in ["1d", "5d"]:
                hist.index = hist.index.tz_convert(spain_tz)
            
            # Guardar fecha de referencia para el rango del eje X
            if reference_date is None and period == "1d":
                reference_date = hist.index[-1].date()
            
            # Usar el color único de cada acción
            line_color = MAGNIFICENT_SEVEN[symbol]['color']
            # Crear color de relleno con transparencia
            hex_color = line_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            fill_color = f"rgba({r}, {g}, {b}, 0.15)"
            
            arrow = "▲" if final_change >= 0 else "▼"
            
            # Formato de hover según período
            if period in ["1d", "5d"]:
                hover_template = (f"<b>{symbol}</b><br>" +
                                 "Hora: %{x|%H:%M}<br>" +
                                 "Cambio: %{y:.2f}%<extra></extra>")
            else:
                hover_template = (f"<b>{symbol}</b><br>" +
                                 "Fecha: %{x|%d/%m/%Y}<br>" +
                                 "Cambio: %{y:.2f}%<extra></extra>")
            
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=normalized,
                mode='lines',
                name=f"{symbol} {arrow} {final_change:+.1f}%",
                line=dict(color=line_color, width=3),
                fill='tozeroy',
                fillcolor=fill_color,
                hovertemplate=hover_template
            ))
    
    # Configurar formato del eje X según período
    if period == "1d":
        # Para 1D: mostrar rango completo 15:30-22:00 hora España
        if reference_date:
            # Rango en hora española
            market_open = datetime.combine(reference_date, datetime.strptime("15:30", "%H:%M").time())
            market_close = datetime.combine(reference_date, datetime.strptime("22:00", "%H:%M").time())
            market_open = spain_tz.localize(market_open)
            market_close = spain_tz.localize(market_close)
            
            xaxis_config = dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(0,0,0,0.06)',
                tickfont=dict(color='#78909C', family='Nunito', size=9),
                tickformat="%H:%M",
                nticks=8,
                range=[market_open, market_close],
                fixedrange=True,
                constrain='domain',
            )
        else:
            xaxis_config = dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(0,0,0,0.06)',
                tickfont=dict(color='#78909C', family='Nunito', size=9),
                tickformat="%H:%M",
                nticks=8,
                fixedrange=True,
                constrain='domain',
            )
    elif period == "5d":
        xaxis_config = dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.06)',
            tickfont=dict(color='#78909C', family='Nunito', size=9),
            tickformat="%d/%m %H:%M",
            nticks=10,
            fixedrange=True,
            constrain='domain',
        )
    else:
        xaxis_config = dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.06)',
            tickfont=dict(color='#78909C', family='Nunito', size=10)
        )
    
    fig.update_layout(
        title=dict(text="📊 Comparativa (%)", font=dict(size=16, color='#37474F', family='Nunito')),
        template='plotly_white',
        paper_bgcolor='rgba(255,255,255,0)',
        plot_bgcolor='rgba(253,246,240,0.5)',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color='#37474F', size=9, family='Nunito'),
            itemwidth=30
        ),
        xaxis=xaxis_config,
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.06)',
            tickfont=dict(color='#78909C', family='Nunito', size=10),
            ticksuffix="%",
            zeroline=True,
            zerolinecolor='rgba(0,0,0,0.15)',
            zerolinewidth=2
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        autosize=True
    )
    
    # Mensaje si no hay datos
    if not has_data:
        fig.add_annotation(
            text="No hay datos disponibles para este período.<br>El mercado NASDAQ opera de 15:30 a 22:00 (hora España).",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color='#78909C'),
            align="center"
        )
    
    return fig


def create_market_cap_chart(data, symbols):
    """Crear gráfico de capitalización de mercado con color único por acción"""
    caps = []
    names = []
    colors = []
    
    for symbol in symbols:
        if data[symbol] and data[symbol]["market_cap"]:
            caps.append(data[symbol]["market_cap"] / 1e12)  # En trillones
            names.append(symbol)
            # Usar el color único de cada acción
            colors.append(MAGNIFICENT_SEVEN[symbol]['color'])
    
    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=caps,
            marker_color=colors,
            marker_line=dict(color='rgba(255,255,255,0.8)', width=2),
            text=[f"${c:.2f}T" for c in caps],
            textposition='outside',
            textfont=dict(color='#37474F', size=12, family='Nunito')
        )
    ])
    
    fig.update_layout(
        title=dict(text="💰 Cap. de Mercado (T USD)", font=dict(size=16, color='#37474F', family='Nunito')),
        template='plotly_white',
        paper_bgcolor='rgba(255,255,255,0)',
        plot_bgcolor='rgba(253,246,240,0.5)',
        xaxis=dict(
            tickfont=dict(color='#78909C', family='Nunito', size=10),
            showgrid=False,
            tickangle=-45
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.06)',
            tickfont=dict(color='#78909C', family='Nunito', size=10),
            tickprefix="$",
            ticksuffix="T"
        ),
        margin=dict(l=10, r=10, t=50, b=60),
        autosize=True
    )
    
    return fig


def check_alerts(data, alerts_config):
    """Verificar alertas configuradas"""
    triggered_alerts = []
    
    for symbol, config in alerts_config.items():
        if data.get(symbol) and data[symbol]:
            current_price = data[symbol]["current_price"]
            
            if "upper" in config and current_price >= config["upper"]:
                triggered_alerts.append({
                    "symbol": symbol,
                    "type": "upper",
                    "price": current_price,
                    "threshold": config["upper"]
                })
            
            if "lower" in config and current_price <= config["lower"]:
                triggered_alerts.append({
                    "symbol": symbol,
                    "type": "lower",
                    "price": current_price,
                    "threshold": config["lower"]
                })
            
            if "change_percent" in config:
                change = calculate_change(current_price, data[symbol]["prev_close"])
                if abs(change) >= config["change_percent"]:
                    triggered_alerts.append({
                        "symbol": symbol,
                        "type": "change",
                        "price": current_price,
                        "change": change,
                        "threshold": config["change_percent"]
                    })
            
            if "change_up" in config:
                change = calculate_change(current_price, data[symbol]["prev_close"])
                if change >= config["change_up"]:
                    triggered_alerts.append({
                        "symbol": symbol,
                        "type": "change_up",
                        "price": current_price,
                        "change": change,
                        "threshold": config["change_up"]
                    })
            
            if "change_down" in config:
                change = calculate_change(current_price, data[symbol]["prev_close"])
                if change <= -config["change_down"]:
                    triggered_alerts.append({
                        "symbol": symbol,
                        "type": "change_down",
                        "price": current_price,
                        "change": change,
                        "threshold": config["change_down"]
                    })
    
    return triggered_alerts


def main():
    # Header principal responsive
    st.markdown("""
    <div class="main-header-responsive" style="text-align: center; padding: 0.3rem 0; margin-bottom: 0.3rem;">
        <h1 style="font-size: clamp(1.1rem, 4vw, 1.6rem) !important; margin: 0 !important; line-height: 1.2;">
            NASDAQ Magnificent 7 <span style="font-size: 0.6em; color: #9E9E9E; font-weight: 400;">v1.0</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Usar todas las acciones por defecto
    selected_symbols = list(MAGNIFICENT_SEVEN.keys())
    
    # Obtener datos con período por defecto (1 mes) para métricas
    with st.spinner("📡 Obteniendo datos del mercado..."):
        stock_data = get_stock_data(selected_symbols, "1mo")
    
    # Inicializar estado de pestaña activa y período seleccionado
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "📊 Dashboard"
    
    if "selected_period" not in st.session_state:
        st.session_state.selected_period = "1M"  # Por defecto 1 mes
    
    # Navegación por pestañas (mantiene el estado)
    tabs_options = ["📊 Dashboard", "🪙 Crypto", "📈 Comparativas", "🔔 Alertas", "💰 Portfolio"]
    
    selected_tab = st.radio(
        "Navegación",
        options=tabs_options,
        index=tabs_options.index(st.session_state.active_tab),
        horizontal=True,
        key="tab_selector",
        label_visibility="collapsed"
    )
    
    # Actualizar estado
    st.session_state.active_tab = selected_tab
    
    # Leer estado de auto-refresh desde query params
    query_params = st.query_params
    auto_refresh_default = query_params.get("autorefresh", "0") == "1"
    
    # Checkbox de auto-actualización con cuenta atrás en la misma línea
    if auto_refresh_default:
        # Mostrar checkbox y cuenta atrás juntos
        st.markdown("""
        <style>
        .auto-refresh-container {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Inicializar estado del sonido
    if "sound_enabled" not in st.session_state:
        st.session_state.sound_enabled = False
    
    # CSS para botón de sonido pequeño y centrado
    st.markdown("""
    <style>
    .sound-button-container {
        display: flex;
        justify-content: center;
        margin: 0.3rem 0;
    }
    .sound-button-container [data-testid="stButton"] button {
        padding: 4px 16px !important;
        min-height: 32px !important;
        font-size: 0.85rem !important;
        white-space: nowrap !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Fila 1: Auto-refresh y countdown
    col_check, col_countdown, col_space = st.columns([1.1, 0.35, 4.55])
    
    with col_check:
        auto_refresh = st.checkbox("🔄 Actualizar cada 5 minutos", value=auto_refresh_default, key="auto_refresh")
    
    # Fila 2: Botón de sonido alineado a la derecha
    col_space, col_sound = st.columns([4, 1])
    with col_sound:
        if st.button("🔊 ON" if st.session_state.sound_enabled else "🔇 OFF", key="toggle_sound", use_container_width=True):
            st.session_state.sound_enabled = not st.session_state.sound_enabled
            if st.session_state.sound_enabled:
                # Reproducir beep de prueba para activar el audio
                components.html("""
                <script>
                    try {
                        var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                        var oscillator = audioCtx.createOscillator();
                        var gainNode = audioCtx.createGain();
                        oscillator.connect(gainNode);
                        gainNode.connect(audioCtx.destination);
                        oscillator.frequency.value = 880;
                        oscillator.type = 'square';
                        gainNode.gain.value = 0.2;
                        oscillator.start();
                        oscillator.stop(audioCtx.currentTime + 0.1);
                    } catch(e) {}
                </script>
                """, height=0)
            st.rerun()
    
    # Actualizar query params según el estado del checkbox
    if auto_refresh:
        st.query_params["autorefresh"] = "1"
        
        with col_countdown:
            # Limpiar caché para obtener datos frescos en cada ciclo
            st.cache_data.clear()
            
            # Cuenta atrás
            components.html("""
            <div style="display: flex; align-items: center; justify-content: flex-start; font-family: 'Nunito', sans-serif; height: 38px;">
                <span id="countdown" style="color: #B39DDB; font-weight: bold; font-size: 0.95rem; 
                      background: white; padding: 4px 12px; border-radius: 12px; border: 2px solid #ECEFF1;">5:00</span>
            </div>
            <script>
                var seconds = 300;
                var countdownEl = document.getElementById('countdown');
                var reloading = false;
                
                var timer = setInterval(function() {
                    if (reloading) return;
                    
                    seconds--;
                    if (countdownEl) {
                        var mins = Math.floor(seconds / 60);
                        var secs = seconds % 60;
                        countdownEl.textContent = mins + ':' + (secs < 10 ? '0' : '') + secs;
                        if (seconds <= 30) {
                            countdownEl.style.color = '#E53935';
                            countdownEl.style.borderColor = '#FFCDD2';
                        }
                    }
                    if (seconds <= 0) {
                        reloading = true;
                        clearInterval(timer);
                        countdownEl.textContent = '⟳';
                        
                        // Forzar recarga de la página
                        try {
                            window.parent.location.reload(true);
                        } catch(e) {
                            window.top.location.reload(true);
                        }
                    }
                }, 1000);
            </script>
            """, height=38)
    elif "autorefresh" in query_params:
        del st.query_params["autorefresh"]
    
    st.markdown("---")
    
    # TAB 1: Dashboard
    if selected_tab == "📊 Dashboard":
        st.markdown("### 💹 Resumen")
        
        # Métricas principales en una sola línea horizontal
        items_html = []
        for symbol in selected_symbols:
            if stock_data[symbol]:
                current = stock_data[symbol]["current_price"]
                prev = stock_data[symbol]["prev_close"]
                change = calculate_change(current, prev)
                change_color = COLORS["up"] if change >= 0 else COLORS["down"]
                arrow = "▲" if change >= 0 else "▼"
                
                item = f'<div style="display:flex;flex-direction:column;align-items:center;background:white;padding:8px 10px;border-radius:10px;border:1px solid #ECEFF1;box-shadow:0 2px 8px rgba(0,0,0,0.04);min-width:80px;"><span style="font-weight:700;color:#37474F;font-size:0.85rem;">{symbol}</span><span style="font-family:monospace;font-weight:600;color:#37474F;font-size:0.9rem;">${current:.2f}</span><span style="font-family:monospace;font-weight:600;color:{change_color};font-size:0.8rem;">{arrow}{change:+.2f}%</span></div>'
                items_html.append(item)
            else:
                item = f'<div style="display:flex;flex-direction:column;align-items:center;background:white;padding:8px 10px;border-radius:10px;border:1px solid #ECEFF1;min-width:80px;"><span style="font-weight:700;color:#37474F;font-size:0.85rem;">{symbol}</span><span style="color:#78909C;">Error</span></div>'
                items_html.append(item)
        
        html_content = '<div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:flex-start;">' + ''.join(items_html) + '</div>'
        st.markdown(html_content, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Selector de período para gráfico de precios
        period_options = {
            "1D": "1d", "5D": "5d", "1M": "1mo", "3M": "3mo", 
            "6M": "6mo", "1A": "1y", "2A": "2y", "5A": "5y"
        }
        
        st.markdown("#### 📈 Evolución de Precios")
        
        # Contenedor con clase para estilos compactos
        st.markdown('<div class="period-selector">', unsafe_allow_html=True)
        period_price = st.radio(
            "Período",
            options=list(period_options.keys()),
            index=list(period_options.keys()).index(st.session_state.selected_period),
            key="period_price",
            horizontal=True,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Guardar período seleccionado
        st.session_state.selected_period = period_price
        
        # Obtener datos con el período seleccionado
        period_value = period_options[period_price]
        with st.spinner(""):
            chart_data = get_stock_data(selected_symbols, period_value)
        
        # Gráfico de precios
        st.plotly_chart(
            create_price_chart(chart_data, selected_symbols, "", period_value),
            use_container_width=True
        )
        
        # Tabla de datos detallados
        st.markdown("#### Datos Detallados")
        table_data = []
        for symbol in selected_symbols:
            if stock_data[symbol]:
                d = stock_data[symbol]
                change = calculate_change(d["current_price"], d["prev_close"])
                table_data.append({
                    "Símbolo": symbol,
                    "Precio": f"${d['current_price']:.2f}",
                    "Cambio": change,
                    "Cap. Mercado": format_market_cap(d["market_cap"]),
                    "P/E": f"{d['pe_ratio']:.1f}" if d['pe_ratio'] else "-",
                    "52W Max": f"${d['52w_high']:.2f}",
                    "52W Min": f"${d['52w_low']:.2f}",
                })
        
        if table_data:
            df = pd.DataFrame(table_data)
            
            # Formatear la columna de cambio con colores
            def color_change(val):
                if isinstance(val, (int, float)):
                    color = COLORS["up"] if val >= 0 else COLORS["down"]
                    return f'color: {color}; font-weight: bold'
                return ''
            
            # Mostrar dataframe con estilo
            styled_df = df.style.applymap(color_change, subset=['Cambio'])
            styled_df = styled_df.format({'Cambio': '{:+.2f}%'})
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # TAB 2: Crypto
    if selected_tab == "🪙 Crypto":
        st.markdown("### 🪙 Top 5 Criptomonedas")
        
        crypto_symbols = list(TOP_CRYPTO.keys())
        
        # Obtener datos de criptomonedas
        with st.spinner("📡 Obteniendo datos de criptomonedas..."):
            crypto_data = get_stock_data(crypto_symbols, "1mo")
        
        # Métricas de criptomonedas en una línea
        crypto_items_html = []
        for symbol in crypto_symbols:
            if crypto_data.get(symbol):
                current = crypto_data[symbol]["current_price"]
                prev = crypto_data[symbol]["prev_close"]
                change = calculate_change(current, prev)
                change_color = COLORS["up"] if change >= 0 else COLORS["down"]
                arrow = "▲" if change >= 0 else "▼"
                crypto_info = TOP_CRYPTO[symbol]
                
                # Formatear precio según el valor
                if current >= 1000:
                    price_fmt = f"${current:,.0f}"
                elif current >= 1:
                    price_fmt = f"${current:,.2f}"
                else:
                    price_fmt = f"${current:.4f}"
                
                item = f'''<div style="display:flex;flex-direction:column;align-items:center;background:white;padding:10px 12px;border-radius:12px;border:2px solid {crypto_info['color']}20;box-shadow:0 2px 8px rgba(0,0,0,0.04);min-width:100px;">
                    <span style="font-size:1.2rem;">{crypto_info['emoji']}</span>
                    <span style="font-weight:700;color:#37474F;font-size:0.85rem;">{crypto_info['name']}</span>
                    <span style="font-family:monospace;font-weight:600;color:#37474F;font-size:0.95rem;">{price_fmt}</span>
                    <span style="font-family:monospace;font-weight:600;color:{change_color};font-size:0.85rem;">{arrow}{change:+.2f}%</span>
                </div>'''
                crypto_items_html.append(item)
        
        html_content = '<div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:flex-start;">' + ''.join(crypto_items_html) + '</div>'
        st.markdown(html_content, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Selector de período para gráfico
        crypto_period_options = {
            "1D": "1d", "5D": "5d", "1M": "1mo", "3M": "3mo", 
            "6M": "6mo", "1A": "1y", "2A": "2y"
        }
        
        st.markdown("#### 📈 Evolución de Precios")
        
        st.markdown('<div class="period-selector">', unsafe_allow_html=True)
        crypto_period = st.radio(
            "Período Crypto",
            options=list(crypto_period_options.keys()),
            index=2,  # 1M por defecto
            key="crypto_period",
            horizontal=True,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Obtener datos con el período seleccionado
        crypto_period_value = crypto_period_options[crypto_period]
        with st.spinner(""):
            crypto_chart_data = get_stock_data(crypto_symbols, crypto_period_value)
        
        # Gráfico de precios de criptomonedas
        fig_crypto = go.Figure()
        
        for symbol in crypto_symbols:
            if crypto_chart_data.get(symbol) and len(crypto_chart_data[symbol]["history"]) > 0:
                hist = crypto_chart_data[symbol]["history"]
                first_price = hist['Close'].iloc[0]
                last_price = hist['Close'].iloc[-1]
                change = ((last_price - first_price) / first_price) * 100
                line_color = TOP_CRYPTO[symbol]['color']
                arrow = "▲" if change >= 0 else "▼"
                
                fig_crypto.add_trace(go.Scatter(
                    x=hist.index,
                    y=hist['Close'],
                    mode='lines',
                    name=f"{TOP_CRYPTO[symbol]['name']} {arrow} {change:+.1f}%",
                    line=dict(color=line_color, width=3),
                    hovertemplate=f"<b>{TOP_CRYPTO[symbol]['name']}</b><br>" +
                                 "Fecha: %{x|%d/%m/%Y}<br>" +
                                 "Precio: $%{y:,.2f}<extra></extra>"
                ))
        
        fig_crypto.update_layout(
            template='plotly_white',
            paper_bgcolor='rgba(255,255,255,0)',
            plot_bgcolor='rgba(253,246,240,0.5)',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(color='#37474F', size=9, family='Nunito'),
                itemwidth=30
            ),
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(0,0,0,0.06)',
                tickfont=dict(color='#78909C', family='Nunito', size=10)
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(0,0,0,0.06)',
                tickfont=dict(color='#78909C', family='Nunito', size=10),
                tickprefix="$"
            ),
            margin=dict(l=10, r=10, t=50, b=10),
            autosize=True
        )
        
        st.plotly_chart(fig_crypto, use_container_width=True)
        
        # Gráfico comparativo normalizado
        st.markdown("#### 📊 Comparativa de Rendimiento (%)")
        
        fig_crypto_comp = go.Figure()
        
        for symbol in crypto_symbols:
            if crypto_chart_data.get(symbol) and len(crypto_chart_data[symbol]["history"]) > 0:
                hist = crypto_chart_data[symbol]["history"]
                normalized = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
                final_change = normalized.iloc[-1]
                line_color = TOP_CRYPTO[symbol]['color']
                arrow = "▲" if final_change >= 0 else "▼"
                
                fig_crypto_comp.add_trace(go.Scatter(
                    x=hist.index,
                    y=normalized,
                    mode='lines',
                    name=f"{TOP_CRYPTO[symbol]['name']} {arrow} {final_change:+.1f}%",
                    line=dict(color=line_color, width=3),
                    hovertemplate=f"<b>{TOP_CRYPTO[symbol]['name']}</b><br>" +
                                 "Fecha: %{x|%d/%m/%Y}<br>" +
                                 "Cambio: %{y:.2f}%<extra></extra>"
                ))
        
        fig_crypto_comp.update_layout(
            template='plotly_white',
            paper_bgcolor='rgba(255,255,255,0)',
            plot_bgcolor='rgba(253,246,240,0.5)',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(color='#37474F', size=9, family='Nunito'),
                itemwidth=30
            ),
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(0,0,0,0.06)',
                tickfont=dict(color='#78909C', family='Nunito', size=10)
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(0,0,0,0.06)',
                tickfont=dict(color='#78909C', family='Nunito', size=10),
                ticksuffix="%",
                zeroline=True,
                zerolinecolor='rgba(0,0,0,0.15)',
                zerolinewidth=2
            ),
            margin=dict(l=10, r=10, t=30, b=10),
            autosize=True
        )
        
        st.plotly_chart(fig_crypto_comp, use_container_width=True)
        
        # Tabla de datos
        st.markdown("#### 📋 Datos Detallados")
        crypto_table_data = []
        for symbol in crypto_symbols:
            if crypto_data.get(symbol):
                d = crypto_data[symbol]
                change = calculate_change(d["current_price"], d["prev_close"])
                crypto_table_data.append({
                    "Crypto": TOP_CRYPTO[symbol]["name"],
                    "Precio": d['current_price'],
                    "Cambio %": change,
                    "Cap. Mercado": format_market_cap(d["market_cap"]) if d["market_cap"] else "-",
                    "24h Max": f"${d['52w_high']:,.2f}" if d['52w_high'] else "-",
                    "24h Min": f"${d['52w_low']:,.2f}" if d['52w_low'] else "-",
                })
        
        if crypto_table_data:
            df_crypto = pd.DataFrame(crypto_table_data)
            
            def color_crypto_change(val):
                if isinstance(val, (int, float)):
                    color = COLORS["up"] if val >= 0 else COLORS["down"]
                    return f'color: {color}; font-weight: bold'
                return ''
            
            styled_crypto = df_crypto.style.applymap(color_crypto_change, subset=['Cambio %'])
            styled_crypto = styled_crypto.format({
                'Precio': '${:,.2f}',
                'Cambio %': '{:+.2f}%'
            })
            st.dataframe(styled_crypto, use_container_width=True, hide_index=True)

    # TAB 3: Comparativas (Acciones)
    if selected_tab == "📈 Comparativas":
        # Selector de período para comparativas (usa el mismo período que Dashboard)
        period_options_comp = {
            "1D": "1d", "5D": "5d", "1M": "1mo", "3M": "3mo", 
            "6M": "6mo", "1A": "1y", "2A": "2y", "5A": "5y"
        }
        
        st.markdown("#### 📊 Comparativa de Rendimiento")
        
        # Contenedor con clase para estilos compactos
        st.markdown('<div class="period-selector">', unsafe_allow_html=True)
        period_comp = st.radio(
            "Período",
            options=list(period_options_comp.keys()),
            index=list(period_options_comp.keys()).index(st.session_state.selected_period),
            key="period_comp",
            horizontal=True,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Guardar período seleccionado
        st.session_state.selected_period = period_comp
        
        # Obtener datos con el período seleccionado
        period_comp_value = period_options_comp[period_comp]
        with st.spinner(""):
            comp_data = get_stock_data(selected_symbols, period_comp_value)
        
        # Gráfico de comparativa de rendimiento
        st.plotly_chart(
            create_comparison_chart(comp_data, selected_symbols, period_comp_value),
            use_container_width=True
        )
        
        # Gráfico de capitalización de mercado
        st.plotly_chart(
            create_market_cap_chart(comp_data, selected_symbols),
            use_container_width=True
        )
        
        # Ranking de rendimiento
        st.markdown("### 🏆 Ranking de Rendimiento")
        
        performance_data = []
        for symbol in selected_symbols:
            if comp_data[symbol] and len(comp_data[symbol]["history"]) > 0:
                hist = comp_data[symbol]["history"]
                first_price = hist['Close'].iloc[0]
                last_price = hist['Close'].iloc[-1]
                change = ((last_price - first_price) / first_price) * 100
                performance_data.append({
                    "symbol": symbol,
                    "name": MAGNIFICENT_SEVEN[symbol]['name'],
                    "change": change
                })
        
        performance_data.sort(key=lambda x: x["change"], reverse=True)
        
        for idx, item in enumerate(performance_data):
            medal = ["🥇", "🥈", "🥉"][idx] if idx < 3 else f"#{idx+1}"
            is_positive = item["change"] >= 0
            color = COLORS["up"] if is_positive else COLORS["down"]
            st.markdown(f"""
            <div class="{'alert-up' if is_positive else 'alert-down'}">
                <span style="font-size: 1.3rem; margin-right: 8px;">{medal}</span>
                <strong style="color: #37474F;">{item['symbol']} - {item['name']}</strong>
                <span style="float: right; color: {color}; font-weight: 700; font-family: 'IBM Plex Mono', monospace;">
                    {item['change']:+.2f}%
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    # TAB 4: Alertas
    if selected_tab == "🔔 Alertas":
        st.markdown("### 🔔 Sistema de Alertas")
        st.markdown("Configura alertas de precio para recibir notificaciones cuando se alcancen tus objetivos.")
        
        # Cargar alertas guardadas (persistentes)
        if "alerts" not in st.session_state:
            st.session_state.alerts = load_alerts()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### ➕ Configurar Nueva Alerta")
            
            alert_symbol = st.selectbox(
                "Selecciona la acción",
                options=selected_symbols,
                format_func=lambda x: f"{x} - {MAGNIFICENT_SEVEN[x]['name']}"
            )
            
            current_price = stock_data[alert_symbol]["current_price"] if stock_data[alert_symbol] else 0
            st.info(f"💵 Precio actual: **${current_price:.2f}**")
            
            alert_type = st.radio(
                "Tipo de alerta",
                options=["Precio objetivo (arriba)", "Precio objetivo (abajo)", "Cambio % (arriba)", "Cambio % (abajo)"]
            )
            
            if alert_type == "Precio objetivo (arriba)":
                threshold = st.number_input(
                    "Precio objetivo ($)",
                    min_value=0.0,
                    value=current_price * 1.1,
                    step=1.0
                )
                alert_key = "upper"
            elif alert_type == "Precio objetivo (abajo)":
                threshold = st.number_input(
                    "Precio objetivo ($)",
                    min_value=0.0,
                    value=current_price * 0.9,
                    step=1.0
                )
                alert_key = "lower"
            elif alert_type == "Cambio % (arriba)":
                threshold = st.number_input(
                    "Cambio porcentual (%)",
                    min_value=0.0,
                    value=5.0,
                    step=0.5
                )
                alert_key = "change_up"
            else:  # Cambio % (abajo)
                threshold = st.number_input(
                    "Cambio porcentual (%)",
                    min_value=0.0,
                    value=5.0,
                    step=0.5
                )
                alert_key = "change_down"
            
            if st.button("➕ Añadir Alerta", use_container_width=True):
                if alert_symbol not in st.session_state.alerts:
                    st.session_state.alerts[alert_symbol] = {}
                st.session_state.alerts[alert_symbol][alert_key] = threshold
                save_alerts(st.session_state.alerts)  # Guardar en archivo
                st.success(f"✅ Alerta configurada para {alert_symbol}")
        
        with col2:
            st.markdown("#### 📋 Alertas Activas")
            
            if st.session_state.alerts:
                for symbol, configs in st.session_state.alerts.items():
                    with st.expander(f"{symbol}", expanded=True):
                        for key, value in configs.items():
                            if key == "upper":
                                st.markdown(f"<span style='color: {COLORS['up']}'>▲</span> Precio arriba de: **${value:.2f}**", unsafe_allow_html=True)
                            elif key == "lower":
                                st.markdown(f"<span style='color: {COLORS['down']}'>▼</span> Precio abajo de: **${value:.2f}**", unsafe_allow_html=True)
                            elif key == "change_up":
                                st.markdown(f"<span style='color: {COLORS['up']}'>▲</span> Cambio arriba de: **+{value:.1f}%**", unsafe_allow_html=True)
                            elif key == "change_down":
                                st.markdown(f"<span style='color: {COLORS['down']}'>▼</span> Cambio abajo de: **-{value:.1f}%**", unsafe_allow_html=True)
                            else:
                                st.write(f"Cambio mayor a: **±{value:.1f}%**")
                        
                        if st.button(f"🗑️ Eliminar alertas de {symbol}", key=f"del_{symbol}"):
                            del st.session_state.alerts[symbol]
                            save_alerts(st.session_state.alerts)  # Guardar cambios
                            st.toast(f"Alertas de {symbol} eliminadas")
                
                # Inicializar alertas silenciadas (se borra al cerrar la app)
                if "silenced_alerts" not in st.session_state:
                    st.session_state.silenced_alerts = set()
                
                # Verificar alertas
                all_triggered = check_alerts(stock_data, st.session_state.alerts)
                
                # Filtrar alertas que no estén silenciadas
                triggered = []
                for a in all_triggered:
                    alert_id = f"{a['symbol']}_{a['type']}_{a.get('threshold', '')}"
                    if alert_id not in st.session_state.silenced_alerts:
                        triggered.append(a)
                
                if triggered:
                    st.markdown("---")
                    st.markdown("### ⚠️ Alertas Activadas")
                    
                    # Construir mensaje para la ventana emergente
                    alert_messages = []
                    for a in triggered:
                        if a["type"] == "upper":
                            alert_messages.append(f"▲ {a['symbol']}: Superó ${a['threshold']:.2f} (Actual: ${a['price']:.2f})")
                        elif a["type"] == "lower":
                            alert_messages.append(f"▼ {a['symbol']}: Bajó de ${a['threshold']:.2f} (Actual: ${a['price']:.2f})")
                        elif a["type"] == "change_up":
                            alert_messages.append(f"▲ {a['symbol']}: Subió {a['change']:+.2f}% (Umbral: +{a['threshold']:.1f}%)")
                        elif a["type"] == "change_down":
                            alert_messages.append(f"▼ {a['symbol']}: Bajó {a['change']:+.2f}% (Umbral: -{a['threshold']:.1f}%)")
                        else:
                            alert_messages.append(f"{a['symbol']}: Cambió {a['change']:+.2f}%")
                    
                    # Construir HTML para cada alerta en el modal
                    alerts_html = ""
                    for a in triggered:
                        if a["type"] in ["upper", "change_up"]:
                            color = "#4CAF50"
                            bg = "#E8F5E9"
                            arrow = "▲"
                            if a["type"] == "upper":
                                text = f'{a["symbol"]}: Superó ${a["threshold"]:.2f} (Actual: ${a["price"]:.2f})'
                            else:
                                text = f'{a["symbol"]}: Subió {a["change"]:+.2f}% (Umbral: +{a["threshold"]:.1f}%)'
                        else:
                            color = "#E53935"
                            bg = "#FFEBEE"
                            arrow = "▼"
                            if a["type"] == "lower":
                                text = f'{a["symbol"]}: Bajó de ${a["threshold"]:.2f} (Actual: ${a["price"]:.2f})'
                            else:
                                text = f'{a["symbol"]}: Bajó {a["change"]:+.2f}% (Umbral: -{a["threshold"]:.1f}%)'
                        
                        alerts_html += f'<div style="background:{bg};border-left:4px solid {color};padding:10px 14px;margin:8px 0;border-radius:0 8px 8px 0;"><span style="color:{color};font-weight:bold;">{arrow}</span> {text}</div>'
                    
                    # Verificar si el sonido está habilitado
                    sound_enabled = st.session_state.get("sound_enabled", False)
                    
                    # Reproducir sonido de alarma y mostrar modal en ventana emergente
                    components.html(f"""
                    <script>
                        (function() {{
                            var soundEnabled = {'true' if sound_enabled else 'false'};
                            
                            // Sonido de alarma usando Audio API
                            function playBeep() {{
                                if (!soundEnabled) return;
                                try {{
                                    // Crear contexto de audio
                                    var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                                    
                                    // Función para un beep
                                    function beep(startTime, duration) {{
                                        var oscillator = audioCtx.createOscillator();
                                        var gainNode = audioCtx.createGain();
                                        oscillator.connect(gainNode);
                                        gainNode.connect(audioCtx.destination);
                                        oscillator.frequency.value = 880;
                                        oscillator.type = 'square';
                                        gainNode.gain.value = 0.3;
                                        oscillator.start(audioCtx.currentTime + startTime);
                                        oscillator.stop(audioCtx.currentTime + startTime + duration);
                                    }}
                                    
                                    // 5 beeps más fuertes
                                    beep(0, 0.2);
                                    beep(0.3, 0.2);
                                    beep(0.6, 0.2);
                                    beep(0.9, 0.2);
                                    beep(1.2, 0.2);
                                }} catch(e) {{
                                    console.log('Audio error:', e);
                                }}
                            }}
                            
                            // Ejecutar sonido
                            playBeep();
                            
                            // Crear modal en el documento padre
                            var parentDoc = window.parent.document;
                            
                            // Eliminar modal anterior si existe
                            var oldModal = parentDoc.getElementById('nasdaq-alert-modal');
                            if (oldModal) oldModal.remove();
                            
                            // Crear overlay
                            var overlay = parentDoc.createElement('div');
                            overlay.id = 'nasdaq-alert-modal';
                            overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);display:flex;justify-content:center;align-items:center;z-index:999999;font-family:Nunito,sans-serif;';
                            
                            // Crear contenido del modal
                            overlay.innerHTML = `
                                <div style="background:linear-gradient(135deg,#FDF6F0 0%,#FFFFFF 100%);border-radius:20px;padding:24px;max-width:400px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,0.3);animation:slideIn 0.3s ease;">
                                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;padding-bottom:12px;border-bottom:2px solid #ECEFF1;">
                                        <span style="font-size:1.8rem;">🚨</span>
                                        <span style="font-size:1.2rem;font-weight:700;color:#37474F;">Alertas Activadas</span>
                                    </div>
                                    <div style="max-height:300px;overflow-y:auto;">
                                        {alerts_html}
                                    </div>
                                    <button id="closeAlertBtn" style="width:100%;margin-top:16px;padding:12px;background:linear-gradient(135deg,#B39DDB 0%,#90CAF9 100%);color:white;border:none;border-radius:12px;font-size:1rem;font-weight:600;cursor:pointer;font-family:Nunito,sans-serif;">
                                        Aceptar
                                    </button>
                                </div>
                            `;
                            
                            // Añadir al documento padre
                            parentDoc.body.appendChild(overlay);
                            
                            // Añadir evento para cerrar
                            parentDoc.getElementById('closeAlertBtn').onclick = function() {{
                                overlay.remove();
                            }};
                            
                            // Cerrar al hacer clic fuera
                            overlay.onclick = function(e) {{
                                if (e.target === overlay) overlay.remove();
                            }};
                        }})();
                    </script>
                    """, height=0)
                    
                    for alert in triggered:
                        if alert["type"] == "upper":
                            st.markdown(f"""
                            <div style="background: linear-gradient(90deg, #C8E6C9 0%, #E8F5E9 100%); border-left: 5px solid #4CAF50; padding: 12px 16px; border-radius: 0 12px 12px 0; margin: 8px 0;">
                                <span style="color: #4CAF50; font-size: 1.2rem;">▲</span> <strong>{alert['symbol']}</strong> ha superado ${alert['threshold']:.2f} 
                                (Actual: <span style="color: #4CAF50; font-weight: bold;">${alert['price']:.2f}</span>)
                            </div>
                            """, unsafe_allow_html=True)
                        elif alert["type"] == "lower":
                            st.markdown(f"""
                            <div style="background: linear-gradient(90deg, #FFCDD2 0%, #FFEBEE 100%); border-left: 5px solid #E53935; padding: 12px 16px; border-radius: 0 12px 12px 0; margin: 8px 0;">
                                <span style="color: #E53935; font-size: 1.2rem;">▼</span> <strong>{alert['symbol']}</strong> ha bajado de ${alert['threshold']:.2f} 
                                (Actual: <span style="color: #E53935; font-weight: bold;">${alert['price']:.2f}</span>)
                            </div>
                            """, unsafe_allow_html=True)
                        elif alert["type"] == "change_up":
                            st.markdown(f"""
                            <div style="background: linear-gradient(90deg, #C8E6C9 0%, #E8F5E9 100%); border-left: 5px solid #4CAF50; padding: 12px 16px; border-radius: 0 12px 12px 0; margin: 8px 0;">
                                <span style="color: #4CAF50; font-size: 1.2rem;">▲</span> <strong>{alert['symbol']}</strong> ha subido 
                                <span style="color: #4CAF50; font-weight: bold;">{alert['change']:+.2f}%</span>
                                (Umbral: +{alert['threshold']:.1f}%)
                            </div>
                            """, unsafe_allow_html=True)
                        elif alert["type"] == "change_down":
                            st.markdown(f"""
                            <div style="background: linear-gradient(90deg, #FFCDD2 0%, #FFEBEE 100%); border-left: 5px solid #E53935; padding: 12px 16px; border-radius: 0 12px 12px 0; margin: 8px 0;">
                                <span style="color: #E53935; font-size: 1.2rem;">▼</span> <strong>{alert['symbol']}</strong> ha bajado 
                                <span style="color: #E53935; font-weight: bold;">{alert['change']:+.2f}%</span>
                                (Umbral: -{alert['threshold']:.1f}%)
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            if alert['change'] >= 0:
                                bg_style = "background: linear-gradient(90deg, #C8E6C9 0%, #E8F5E9 100%); border-left: 5px solid #4CAF50;"
                                color = "#4CAF50"
                                arrow = "▲"
                            else:
                                bg_style = "background: linear-gradient(90deg, #FFCDD2 0%, #FFEBEE 100%); border-left: 5px solid #E53935;"
                                color = "#E53935"
                                arrow = "▼"
                            st.markdown(f"""
                            <div style="{bg_style} padding: 12px 16px; border-radius: 0 12px 12px 0; margin: 8px 0;">
                                <span style="color: {color}; font-size: 1.2rem;">{arrow}</span> <strong>{alert['symbol']}</strong> ha cambiado 
                                <span style="color: {color}; font-weight: bold;">{alert['change']:.2f}%</span>
                                (Umbral: ±{alert['threshold']:.1f}%)
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Botón para silenciar alertas activadas
                    if st.button("🗑️ Eliminar alertas activadas", key="silence_alerts", use_container_width=True):
                        for a in triggered:
                            alert_id = f"{a['symbol']}_{a['type']}_{a.get('threshold', '')}"
                            st.session_state.silenced_alerts.add(alert_id)
                        st.toast("Alertas eliminadas. Se reactivarán al recargar la página.")
            else:
                st.info("No hay alertas configuradas. Añade una alerta en el panel izquierdo.")
        
        # Sección de importar/exportar alertas
        st.markdown("---")
        st.markdown("#### 💾 Guardar / Cargar Alertas")
        
        col_exp, col_imp = st.columns(2)
        
        with col_exp:
            if st.session_state.alerts:
                export_data_button(
                    st.session_state.alerts, 
                    "alertas_nasdaq.json", 
                    "⬇️ Exportar Alertas", 
                    "export_alerts"
                )
            else:
                st.button("⬇️ Exportar Alertas", disabled=True, use_container_width=True)
        
        with col_imp:
            uploaded_alerts = st.file_uploader(
                "Importar", 
                type="json", 
                key="import_alerts",
                label_visibility="collapsed"
            )
            if uploaded_alerts is not None:
                try:
                    imported_alerts = json.load(uploaded_alerts)
                    st.session_state.alerts = imported_alerts
                    save_alerts(imported_alerts)
                    st.success("Alertas importadas correctamente")
                except Exception as e:
                    st.error(f"Error al importar: {e}")
    
    # TAB 5: Portfolio
    if selected_tab == "💰 Portfolio":
        st.markdown("### Gestión de Portfolio")
        st.markdown("Registra tus inversiones y haz seguimiento de tu rendimiento.")
        
        # Cargar portfolio
        portfolio = load_portfolio()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Añadir Posición")
            
            # Combinar acciones y criptos
            all_assets = {**MAGNIFICENT_SEVEN, **TOP_CRYPTO}
            
            # Separar por categorías para el selectbox
            stock_options = list(MAGNIFICENT_SEVEN.keys())
            crypto_options = list(TOP_CRYPTO.keys())
            
            asset_type = st.radio(
                "Tipo",
                options=["📈 Acciones", "🪙 Crypto"],
                horizontal=True,
                key="asset_type",
                label_visibility="collapsed"
            )
            
            if asset_type == "📈 Acciones":
                port_symbol = st.selectbox(
                    "Acción",
                    options=stock_options,
                    format_func=lambda x: f"{x} - {MAGNIFICENT_SEVEN[x]['name']}",
                    key="portfolio_symbol_stock"
                )
            else:
                port_symbol = st.selectbox(
                    "Criptomoneda",
                    options=crypto_options,
                    format_func=lambda x: f"{TOP_CRYPTO[x]['emoji']} {TOP_CRYPTO[x]['name']}",
                    key="portfolio_symbol_crypto"
                )
            
            # Etiqueta diferente según tipo de activo
            if asset_type == "📈 Acciones":
                shares = st.number_input("Número de acciones", min_value=0.0, value=1.0, step=0.1)
            else:
                shares = st.number_input("Cantidad", min_value=0.0, value=0.1, step=0.01, format="%.4f")
            
            buy_price = st.number_input("Precio de compra ($)", min_value=0.0, value=100.0, step=1.0)
            buy_date = st.date_input("Fecha de compra", value=datetime.now())
            
            if st.button("Guardar Posición", use_container_width=True):
                if port_symbol not in portfolio:
                    portfolio[port_symbol] = []
                
                portfolio[port_symbol].append({
                    "shares": shares,
                    "buy_price": buy_price,
                    "buy_date": buy_date.strftime("%Y-%m-%d")
                })
                
                save_portfolio(portfolio)
                st.success("Posición guardada correctamente")
        
        with col2:
            st.markdown("#### Resumen del Portfolio")
            
            if portfolio:
                # Obtener datos de criptos si hay alguna en el portfolio
                portfolio_cryptos = [s for s in portfolio.keys() if s in TOP_CRYPTO]
                crypto_data_portfolio = {}
                if portfolio_cryptos:
                    with st.spinner(""):
                        crypto_data_portfolio = get_stock_data(portfolio_cryptos, "1mo")
                
                # Combinar datos de acciones y criptos
                all_portfolio_data = {**stock_data, **crypto_data_portfolio}
                all_assets = {**MAGNIFICENT_SEVEN, **TOP_CRYPTO}
                
                total_invested = 0
                total_current = 0
                total_prev_value = 0  # Valor al cierre anterior
                portfolio_details = []
                
                for symbol, positions in portfolio.items():
                    if symbol in all_assets:
                        asset_info = all_portfolio_data.get(symbol, {})
                        if asset_info and asset_info.get("current_price"):
                            curr_price = asset_info["current_price"]
                            prev_close = asset_info.get("prev_close", curr_price)
                            
                            for pos in positions:
                                invested = pos["shares"] * pos["buy_price"]
                                current = pos["shares"] * curr_price
                                prev_value = pos["shares"] * prev_close
                                gain = current - invested
                                gain_pct = (gain / invested) * 100 if invested > 0 else 0
                                
                                # Ganancia del día
                                daily_gain = current - prev_value
                                daily_gain_pct = ((curr_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0
                                
                                total_invested += invested
                                total_current += current
                                total_prev_value += prev_value
                                
                                portfolio_details.append({
                                    "Símbolo": symbol,
                                    "Cantidad": pos['shares'],
                                    "P. Compra": pos['buy_price'],
                                    "P. Actual": curr_price,
                                    "Invertido": invested,
                                    "Valor": current,
                                    "Ganancia": gain,
                                    "Rend. %": gain_pct,
                                    "Día $": daily_gain,
                                    "Día %": daily_gain_pct
                                })
                
                if portfolio_details:
                    # Métricas generales con colores
                    total_gain = total_current - total_invested
                    total_gain_pct = (total_gain / total_invested) * 100 if total_invested > 0 else 0
                    total_daily_gain = total_current - total_prev_value
                    total_daily_pct = (total_daily_gain / total_prev_value) * 100 if total_prev_value > 0 else 0
                    
                    # Guardar snapshot diario
                    save_daily_snapshot(
                        total_invested, total_current, total_gain, 
                        total_gain_pct, total_daily_gain, total_daily_pct
                    )
                    
                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        st.metric("Invertido", f"${total_invested:,.2f}")
                    with m2:
                        st.metric("Valor Actual", f"${total_current:,.2f}")
                    with m3:
                        st.metric("Ganancia Total", f"${total_gain:+,.2f}", f"{total_gain_pct:+.2f}%")
                    with m4:
                        st.metric("Hoy", f"${total_daily_gain:+,.2f}", f"{total_daily_pct:+.2f}%")
                    
                    st.markdown("---")
                    
                    # Tabla con colores verde/rojo
                    df = pd.DataFrame(portfolio_details)
                    
                    def style_gains(val, col):
                        if col in ['Ganancia', 'Rend. %', 'Día $', 'Día %']:
                            color = COLORS["up"] if val >= 0 else COLORS["down"]
                            return f'color: {color}; font-weight: bold'
                        return ''
                    
                    styled_df = df.style.apply(lambda x: [style_gains(v, c) for c, v in x.items()], axis=1)
                    styled_df = styled_df.format({
                        'Cantidad': '{:.4f}',
                        'P. Compra': '${:.2f}',
                        'P. Actual': '${:.2f}',
                        'Invertido': '${:.2f}',
                        'Valor': '${:.2f}',
                        'Ganancia': '${:+.2f}',
                        'Rend. %': '{:+.2f}%',
                        'Día $': '${:+.2f}',
                        'Día %': '{:+.2f}%'
                    })
                    
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                    
                    # Gráfico de distribución con color único por activo
                    pie_colors = []
                    for d in portfolio_details:
                        symbol = d["Símbolo"]
                        if symbol in MAGNIFICENT_SEVEN:
                            pie_colors.append(MAGNIFICENT_SEVEN[symbol]['color'])
                        elif symbol in TOP_CRYPTO:
                            pie_colors.append(TOP_CRYPTO[symbol]['color'])
                        else:
                            pie_colors.append('#B39DDB')  # Color por defecto
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=[d["Símbolo"] for d in portfolio_details],
                        values=[d["Valor"] for d in portfolio_details],
                        hole=0.45,
                        marker=dict(
                            colors=pie_colors,
                            line=dict(color='white', width=3)
                        ),
                        textfont=dict(color='#37474F', size=12),
                        textinfo='label+percent'
                    )])
                    
                    fig.update_layout(
                        title=dict(text="Distribución del Portfolio", font=dict(color='#37474F', family='Nunito')),
                        template='plotly_white',
                        paper_bgcolor='rgba(255,255,255,0)',
                        plot_bgcolor='rgba(255,255,255,0)',
                        legend=dict(font=dict(color='#37474F', family='Nunito')),
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay posiciones en el portfolio. Añade tu primera inversión.")
            
            if portfolio and st.button("Limpiar Portfolio", type="secondary"):
                save_portfolio({})
                st.toast("Portfolio limpiado")
        
        # Histórico mensual del Portfolio
        st.markdown("---")
        st.markdown("### 📅 Histórico del Portfolio")
        
        portfolio_history = load_portfolio_history()
        
        if portfolio_history:
            # Obtener fechas disponibles
            available_dates = sorted(portfolio_history.keys(), reverse=True)
            available_dates_set = set(available_dates)
            
            # Inicializar mes/año seleccionado
            if "cal_year" not in st.session_state:
                st.session_state.cal_year = datetime.now().year
            if "cal_month" not in st.session_state:
                st.session_state.cal_month = datetime.now().month
            if "selected_history_date" not in st.session_state:
                st.session_state.selected_history_date = available_dates[0] if available_dates else None
            
            # En móvil: calendario arriba, datos abajo
            # En desktop: calendario izquierda, datos derecha
            col_cal1, col_cal2 = st.columns([1, 1.5])
            
            with col_cal1:
                # Contenedor del calendario con estilos
                st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
                
                # Navegación del mes
                st.markdown('<div class="calendar-nav">', unsafe_allow_html=True)
                nav_col1, nav_col2, nav_col3 = st.columns([1, 2.5, 1])
                with nav_col1:
                    if st.button("◀", key="prev_month", use_container_width=True):
                        if st.session_state.cal_month == 1:
                            st.session_state.cal_month = 12
                            st.session_state.cal_year -= 1
                        else:
                            st.session_state.cal_month -= 1
                        st.rerun()
                
                with nav_col2:
                    months_es = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun",
                                 "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                    st.markdown(f"<div style='text-align:center;font-weight:700;color:#37474F;padding:4px;font-size:0.9rem;'>{months_es[st.session_state.cal_month]} {st.session_state.cal_year}</div>", unsafe_allow_html=True)
                
                with nav_col3:
                    if st.button("▶", key="next_month", use_container_width=True):
                        if st.session_state.cal_month == 12:
                            st.session_state.cal_month = 1
                            st.session_state.cal_year += 1
                        else:
                            st.session_state.cal_month += 1
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Crear calendario visual
                cal = calendar.Calendar(firstweekday=0)
                month_days = cal.monthdayscalendar(st.session_state.cal_year, st.session_state.cal_month)
                
                # Cabecera días de la semana
                st.markdown('<div class="calendar-weekdays">' + 
                    ''.join([f"<div>{d}</div>" for d in ["L", "M", "X", "J", "V", "S", "D"]]) + 
                    '</div>', unsafe_allow_html=True)
                
                # Días del mes
                today = datetime.now().date()
                st.markdown('<div class="calendar-days">', unsafe_allow_html=True)
                for week in month_days:
                    cols = st.columns(7, gap="small")
                    for i, day in enumerate(week):
                        with cols[i]:
                            if day == 0:
                                st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)
                            else:
                                date_str = f"{st.session_state.cal_year}-{st.session_state.cal_month:02d}-{day:02d}"
                                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                                has_saved_data = date_str in available_dates_set
                                is_selected = date_str == st.session_state.selected_history_date
                                is_future = date_obj > today
                                
                                if is_future:
                                    st.markdown(f"<div style='text-align:center;color:#E0E0E0;padding:6px 2px;font-size:0.8rem;height:32px;'>{day}</div>", unsafe_allow_html=True)
                                else:
                                    btn_type = "primary" if is_selected else "secondary"
                                    
                                    if st.button(
                                        str(day), 
                                        key=f"day_{date_str}",
                                        type=btn_type,
                                        use_container_width=True
                                    ):
                                        st.session_state.selected_history_date = date_str
                                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Obtener datos de la fecha seleccionada
            selected_date_str = st.session_state.selected_history_date
            
            with col_cal2:
                st.markdown('<div class="history-metrics">', unsafe_allow_html=True)
                if selected_date_str and portfolio:
                    st.markdown(f"<div style='font-weight:700;color:#37474F;font-size:0.9rem;margin-bottom:8px;'>📆 {selected_date_str}</div>", unsafe_allow_html=True)
                    
                    # Obtener precios históricos de Internet (acciones y criptos)
                    all_assets = {**MAGNIFICENT_SEVEN, **TOP_CRYPTO}
                    portfolio_symbols = [s for s in portfolio.keys() if s in all_assets]
                    
                    if portfolio_symbols:
                        with st.spinner("📡"):
                            historical_prices = get_historical_prices(portfolio_symbols, selected_date_str)
                        
                        # Calcular valores del portfolio para esa fecha
                        hist_invested = 0
                        hist_value = 0
                        hist_prev_value = 0
                        actual_date_shown = None
                        valid_data = False
                        
                        for symbol, positions in portfolio.items():
                            if symbol in historical_prices and historical_prices[symbol]:
                                price_data = historical_prices[symbol]
                                actual_date_shown = price_data["actual_date"]
                                valid_data = True
                                
                                for pos in positions:
                                    # Calcular con todas las posiciones del portfolio actual
                                    hist_invested += pos["shares"] * pos["buy_price"]
                                    hist_value += pos["shares"] * price_data["close"]
                                    hist_prev_value += pos["shares"] * price_data["prev_close"]
                        
                        if valid_data and hist_invested > 0:
                            hist_gain = hist_value - hist_invested
                            hist_gain_pct = (hist_gain / hist_invested) * 100
                            hist_daily = hist_value - hist_prev_value
                            hist_daily_pct = (hist_daily / hist_prev_value) * 100 if hist_prev_value > 0 else 0
                            
                            if actual_date_shown and actual_date_shown != selected_date_str:
                                st.caption(f"📍 {actual_date_shown}")
                            
                            hm1, hm2 = st.columns(2, gap="small")
                            with hm1:
                                st.metric("💵 Invertido", f"${hist_invested:,.0f}")
                            with hm2:
                                st.metric("💰 Valor", f"${hist_value:,.0f}")
                            
                            # Cards de ganancia más compactas
                            gain_color = COLORS["up"] if hist_gain >= 0 else COLORS["down"]
                            daily_color = COLORS["up"] if hist_daily >= 0 else COLORS["down"]
                            
                            gc1, gc2 = st.columns(2, gap="small")
                            with gc1:
                                st.markdown(f"""
                                <div class="history-card" style="background:white;padding:8px;border-radius:8px;border:1px solid #ECEFF1;">
                                    <span style="color:#78909C;font-size:0.7rem;">📈 Ganancia</span><br>
                                    <span style="font-family:monospace;font-size:0.9rem;font-weight:600;color:{gain_color};">
                                        ${hist_gain:+,.0f} ({hist_gain_pct:+.1f}%)
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)
                            with gc2:
                                st.markdown(f"""
                                <div class="history-card" style="background:white;padding:8px;border-radius:8px;border:1px solid #ECEFF1;">
                                    <span style="color:#78909C;font-size:0.7rem;">📊 Hoy</span><br>
                                    <span style="font-family:monospace;font-size:0.9rem;font-weight:600;color:{daily_color};">
                                        ${hist_daily:+,.0f} ({hist_daily_pct:+.1f}%)
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Mostrar detalle por acción
                            with st.expander("📋 Detalle por acción", expanded=True):
                                for symbol in portfolio_symbols:
                                    if symbol in historical_prices and historical_prices[symbol]:
                                        price = historical_prices[symbol]["close"]
                                        prev = historical_prices[symbol]["prev_close"]
                                        change = ((price - prev) / prev) * 100 if prev > 0 else 0
                                        change_color = COLORS["up"] if change >= 0 else COLORS["down"]
                                        arrow = "▲" if change >= 0 else "▼"
                                        st.markdown(f"**{symbol}**: ${price:.2f} <span style='color:{change_color};'>{arrow} {change:+.2f}%</span>", unsafe_allow_html=True)
                        else:
                            st.warning("No se pudieron obtener datos de precios para esta fecha.")
                    else:
                        st.info("Añade posiciones al portfolio para ver el histórico.")
                else:
                    st.info("Selecciona un día en el calendario.")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Gráfico de evolución del portfolio
            if len(portfolio_history) > 1:
                st.markdown("#### 📊 Evolución del Valor del Portfolio")
                
                # Preparar datos para el gráfico
                dates = []
                values = []
                gains = []
                
                for date_str in sorted(portfolio_history.keys()):
                    dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
                    values.append(portfolio_history[date_str]["current_value"])
                    gains.append(portfolio_history[date_str]["total_gain"])
                
                fig_history = go.Figure()
                
                # Línea de valor del portfolio
                fig_history.add_trace(go.Scatter(
                    x=dates,
                    y=values,
                    mode='lines+markers',
                    name='Valor Portfolio',
                    line=dict(color='#B39DDB', width=3),
                    marker=dict(size=8, color='#B39DDB'),
                    fill='tozeroy',
                    fillcolor='rgba(179, 157, 219, 0.2)',
                    hovertemplate="Fecha: %{x|%d/%m/%Y}<br>Valor: $%{y:,.2f}<extra></extra>"
                ))
                
                fig_history.update_layout(
                    template='plotly_white',
                    paper_bgcolor='rgba(255,255,255,0)',
                    plot_bgcolor='rgba(253,246,240,0.5)',
                    hovermode='x unified',
                    xaxis=dict(
                        showgrid=True,
                        gridwidth=1,
                        gridcolor='rgba(0,0,0,0.06)',
                        tickfont=dict(color='#78909C', family='Nunito', size=10),
                        tickformat="%d/%m"
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridwidth=1,
                        gridcolor='rgba(0,0,0,0.06)',
                        tickfont=dict(color='#78909C', family='Nunito', size=10),
                        tickprefix="$"
                    ),
                    margin=dict(l=10, r=10, t=30, b=10),
                    height=300
                )
                
                st.plotly_chart(fig_history, use_container_width=True)
        else:
            st.info("📅 El histórico se irá completando automáticamente cada día que consultes el portfolio.")
        
        # Sección de importar/exportar portfolio
        st.markdown("---")
        st.markdown("#### 💾 Guardar / Cargar Portfolio")
        
        col_exp_p, col_imp_p = st.columns(2)
        
        with col_exp_p:
            if portfolio:
                export_data_button(
                    portfolio, 
                    "portfolio_nasdaq.json", 
                    "⬇️ Exportar Portfolio", 
                    "export_portfolio"
                )
            else:
                st.button("⬇️ Exportar Portfolio", disabled=True, use_container_width=True)
        
        with col_imp_p:
            uploaded_portfolio = st.file_uploader(
                "Importar", 
                type="json", 
                key="import_portfolio",
                label_visibility="collapsed"
            )
            if uploaded_portfolio is not None:
                try:
                    imported_portfolio = json.load(uploaded_portfolio)
                    save_portfolio(imported_portfolio)
                    st.success("Portfolio importado correctamente")
                except Exception as e:
                    st.error(f"Error al importar: {e}")


if __name__ == "__main__":
    main()
