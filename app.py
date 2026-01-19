"""
NASDAQ Magnificent Seven Tracker
Aplicación para monitorear las 7 grandes tecnológicas del NASDAQ
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import os

# Configuración de la página
st.set_page_config(
    page_title="NASDAQ Magnificent 7 Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Colores para incrementos y decrementos
COLORS = {
    "up": "#4CAF50",        # Verde para incrementos
    "down": "#E53935",      # Rojo para decrementos
    "up_light": "#C8E6C9",  # Verde claro
    "down_light": "#FFCDD2" # Rojo claro
}

# CSS personalizado para un diseño moderno con colores pastel
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
    }
    
    /* Sidebar - SIEMPRE visible */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #FDF6F0 100%) !important;
        border-right: 1px solid #ECEFF1;
        min-width: 300px !important;
        width: 300px !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        transform: translateX(0) !important;
        left: 0 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-secondary);
    }
    
    /* Forzar sidebar expandido */
    [data-testid="stSidebar"] > div {
        display: block !important;
        visibility: visible !important;
    }
    
    /* Botón de colapsar sidebar - oculto para evitar que lo cierren */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* Contenido principal con margen para el sidebar */
    .main .block-container {
        margin-left: 0 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 14px;
        border: 2px solid #ECEFF1;
        color: var(--text-secondary);
        padding: 12px 28px;
        font-weight: 600;
        transition: all 0.3s ease;
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
        border-radius: 14px;
        font-family: 'Nunito', sans-serif;
        font-weight: 700;
        padding: 0.7rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(179, 157, 219, 0.35);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(179, 157, 219, 0.5);
    }
    
    /* Inputs */
    .stNumberInput input, .stTextInput input, .stSelectbox > div > div {
        background: white !important;
        border: 2px solid #ECEFF1 !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    .stNumberInput input:focus, .stTextInput input:focus {
        border-color: #B39DDB !important;
        box-shadow: 0 0 0 3px rgba(179, 157, 219, 0.2) !important;
    }
    
    /* DataFrames */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: var(--shadow);
        border: 1px solid #ECEFF1;
    }
    
    /* Alertas personalizadas - Verde para subidas */
    .alert-up {
        background: linear-gradient(90deg, #E8F5E9 0%, rgba(232, 245, 233, 0.4) 100%);
        border-left: 5px solid #4CAF50;
        padding: 1rem 1.5rem;
        border-radius: 0 14px 14px 0;
        margin: 0.6rem 0;
        color: var(--text-primary);
    }
    
    /* Alertas personalizadas - Rojo para bajadas */
    .alert-down {
        background: linear-gradient(90deg, #FFEBEE 0%, rgba(255, 235, 238, 0.4) 100%);
        border-left: 5px solid #E53935;
        padding: 1rem 1.5rem;
        border-radius: 0 14px 14px 0;
        margin: 0.6rem 0;
        color: var(--text-primary);
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
        border-radius: 20px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
    }
    
    .stock-card:hover {
        border-color: #B39DDB;
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(179, 157, 219, 0.2);
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
        border-radius: 14px;
        border: 2px solid #ECEFF1;
        font-weight: 600;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 14px;
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

PORTFOLIO_FILE = "portfolio.json"
ALERTS_FILE = "alerts.json"


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


@st.cache_data(ttl=300)  # Cache de 5 minutos
def get_stock_data(symbols, period="1mo"):
    """Obtener datos de acciones"""
    data = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
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


def create_price_chart(data, symbols, title="Evolución de Precios"):
    """Crear gráfico de evolución de precios - Color único por acción"""
    fig = go.Figure()
    
    for symbol in symbols:
        if data[symbol] and len(data[symbol]["history"]) > 0:
            hist = data[symbol]["history"]
            first_price = hist['Close'].iloc[0]
            last_price = hist['Close'].iloc[-1]
            change = ((last_price - first_price) / first_price) * 100
            # Usar el color único de cada acción
            line_color = MAGNIFICENT_SEVEN[symbol]['color']
            # Indicador de subida/bajada en el nombre
            arrow = "▲" if change >= 0 else "▼"
            
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['Close'],
                mode='lines',
                name=f"{MAGNIFICENT_SEVEN[symbol]['emoji']} {symbol} {arrow} {change:+.1f}%",
                line=dict(color=line_color, width=3),
                hovertemplate=f"<b>{symbol}</b><br>" +
                             "Fecha: %{x}<br>" +
                             "Precio: $%{y:.2f}<extra></extra>"
            ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=20, color='#37474F', family='Nunito')),
        template='plotly_white',
        paper_bgcolor='rgba(255,255,255,0)',
        plot_bgcolor='rgba(253,246,240,0.5)',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='#37474F', size=11, family='Nunito')
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.06)',
            tickfont=dict(color='#78909C', family='Nunito')
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.06)',
            tickfont=dict(color='#78909C', family='Nunito'),
            tickprefix="$"
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


def create_comparison_chart(data, symbols):
    """Crear gráfico de comparación normalizado - Color único por acción"""
    fig = go.Figure()
    
    for symbol in symbols:
        if data[symbol] and len(data[symbol]["history"]) > 0:
            hist = data[symbol]["history"]
            # Normalizar a porcentaje desde el inicio
            normalized = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
            final_change = normalized.iloc[-1]
            
            # Usar el color único de cada acción
            line_color = MAGNIFICENT_SEVEN[symbol]['color']
            # Crear color de relleno con transparencia
            hex_color = line_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            fill_color = f"rgba({r}, {g}, {b}, 0.15)"
            
            arrow = "▲" if final_change >= 0 else "▼"
            
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=normalized,
                mode='lines',
                name=f"{MAGNIFICENT_SEVEN[symbol]['emoji']} {symbol} {arrow} {final_change:+.1f}%",
                line=dict(color=line_color, width=3),
                fill='tozeroy',
                fillcolor=fill_color,
                hovertemplate=f"<b>{symbol}</b><br>" +
                             "Fecha: %{x}<br>" +
                             "Cambio: %{y:.2f}%<extra></extra>"
            ))
    
    fig.update_layout(
        title=dict(text="📊 Comparativa de Rendimiento (%)", font=dict(size=20, color='#37474F', family='Nunito')),
        template='plotly_white',
        paper_bgcolor='rgba(255,255,255,0)',
        plot_bgcolor='rgba(253,246,240,0.5)',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='#37474F', size=10, family='Nunito')
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.06)',
            tickfont=dict(color='#78909C', family='Nunito')
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.06)',
            tickfont=dict(color='#78909C', family='Nunito'),
            ticksuffix="%",
            zeroline=True,
            zerolinecolor='rgba(0,0,0,0.15)',
            zerolinewidth=2
        ),
        margin=dict(l=20, r=20, t=60, b=20)
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
            names.append(f"{MAGNIFICENT_SEVEN[symbol]['emoji']} {symbol}")
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
        title=dict(text="💰 Capitalización de Mercado (Trillones USD)", font=dict(size=20, color='#37474F', family='Nunito')),
        template='plotly_white',
        paper_bgcolor='rgba(255,255,255,0)',
        plot_bgcolor='rgba(253,246,240,0.5)',
        xaxis=dict(
            tickfont=dict(color='#78909C', family='Nunito'),
            showgrid=False
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.06)',
            tickfont=dict(color='#78909C', family='Nunito'),
            tickprefix="$",
            ticksuffix="T"
        ),
        margin=dict(l=20, r=20, t=60, b=20)
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
    
    return triggered_alerts


def main():
    # Header principal compacto
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0; margin-bottom: 0.5rem;">
        <h1 style="font-size: 1.6rem !important; margin: 0 !important;">📈 NASDAQ Magnificent Seven</h1>
        <p style="color: #78909C; font-size: 0.9rem; margin: 0.2rem 0 0 0;">
            Monitoreo en tiempo real
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuración")
        
        # Selector de período
        period = st.selectbox(
            "📅 Período de datos",
            options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=2,
            help="Selecciona el período de tiempo para los gráficos"
        )
        
        # Selector de acciones
        st.markdown("### 📊 Acciones a mostrar")
        selected_symbols = st.multiselect(
            "Selecciona las acciones",
            options=list(MAGNIFICENT_SEVEN.keys()),
            default=list(MAGNIFICENT_SEVEN.keys()),
            format_func=lambda x: f"{MAGNIFICENT_SEVEN[x]['emoji']} {MAGNIFICENT_SEVEN[x]['name']}"
        )
        
        # Auto-refresh
        st.markdown("### 🔄 Actualización")
        auto_refresh = st.checkbox("Auto-actualizar (5 min)", value=False)
        
        if st.button("🔄 Actualizar ahora", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        
        # Leyenda de colores por acción
        st.markdown("### 🎨 Colores")
        legend_html = '<div style="padding: 0.8rem; background: white; border-radius: 12px; border: 1px solid #ECEFF1;">'
        for symbol, info in MAGNIFICENT_SEVEN.items():
            legend_html += f'''
            <div style="display: flex; align-items: center; margin-bottom: 0.4rem;">
                <div style="width: 14px; height: 14px; background: {info['color']}; border-radius: 4px; margin-right: 8px;"></div>
                <span style="color: #37474F; font-size: 0.85rem;">{info['emoji']} {symbol}</span>
            </div>'''
        legend_html += f'''
        <div style="margin-top: 0.6rem; padding-top: 0.6rem; border-top: 1px solid #ECEFF1;">
            <div style="display: flex; align-items: center; margin-bottom: 0.3rem;">
                <span style="color: {COLORS['up']}; font-size: 0.85rem; font-weight: 600;">▲ Subida</span>
            </div>
            <div style="display: flex; align-items: center;">
                <span style="color: {COLORS['down']}; font-size: 0.85rem; font-weight: 600;">▼ Bajada</span>
            </div>
        </div>
        </div>'''
        st.markdown(legend_html, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #78909C; font-size: 0.8rem;">
            <p>Datos de Yahoo Finance</p>
            <p>Actualizado: {}</p>
        </div>
        """.format(datetime.now().strftime("%H:%M:%S")), unsafe_allow_html=True)
    
    if not selected_symbols:
        st.warning("⚠️ Por favor, selecciona al menos una acción en el panel lateral.")
        return
    
    # Obtener datos
    with st.spinner("📡 Obteniendo datos del mercado..."):
        stock_data = get_stock_data(selected_symbols, period)
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard",
        "📈 Comparativas", 
        "🔔 Alertas",
        "💼 Portfolio"
    ])
    
    # TAB 1: Dashboard
    with tab1:
        st.markdown("### 💹 Resumen del Mercado")
        
        # Métricas principales en cards
        cols = st.columns(len(selected_symbols))
        
        for idx, symbol in enumerate(selected_symbols):
            with cols[idx]:
                if stock_data[symbol]:
                    current = stock_data[symbol]["current_price"]
                    prev = stock_data[symbol]["prev_close"]
                    change = calculate_change(current, prev)
                    
                    st.metric(
                        label=f"{MAGNIFICENT_SEVEN[symbol]['emoji']} {symbol}",
                        value=f"${current:.2f}",
                        delta=f"{change:.2f}%"
                    )
                else:
                    st.metric(label=f"{MAGNIFICENT_SEVEN[symbol]['emoji']} {symbol}", value="Error")
        
        st.markdown("---")
        
        # Gráfico de precios
        st.plotly_chart(
            create_price_chart(stock_data, selected_symbols, "📈 Evolución de Precios"),
            use_container_width=True
        )
        
        # Tabla de datos detallados con colores
        st.markdown("### 📋 Datos Detallados")
        
        table_data = []
        for symbol in selected_symbols:
            if stock_data[symbol]:
                d = stock_data[symbol]
                change = calculate_change(d["current_price"], d["prev_close"])
                table_data.append({
                    "Acción": f"{MAGNIFICENT_SEVEN[symbol]['emoji']} {MAGNIFICENT_SEVEN[symbol]['name']}",
                    "Símbolo": symbol,
                    "Precio Actual": f"${d['current_price']:.2f}",
                    "Cambio %": change,
                    "Cap. Mercado": format_market_cap(d["market_cap"]),
                    "P/E Ratio": f"{d['pe_ratio']:.2f}" if d['pe_ratio'] else "N/A",
                    "52W Alto": f"${d['52w_high']:.2f}",
                    "52W Bajo": f"${d['52w_low']:.2f}"
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
            styled_df = df.style.applymap(color_change, subset=['Cambio %'])
            styled_df = styled_df.format({'Cambio %': '{:+.2f}%'})
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # TAB 2: Comparativas
    with tab2:
        # Gráfico de comparativa de rendimiento
        st.plotly_chart(
            create_comparison_chart(stock_data, selected_symbols),
            use_container_width=True
        )
        
        # Gráfico de capitalización de mercado
        st.plotly_chart(
            create_market_cap_chart(stock_data, selected_symbols),
            use_container_width=True
        )
        
        # Ranking de rendimiento
        st.markdown("### 🏆 Ranking de Rendimiento")
        
        performance_data = []
        for symbol in selected_symbols:
            if stock_data[symbol] and len(stock_data[symbol]["history"]) > 0:
                hist = stock_data[symbol]["history"]
                first_price = hist['Close'].iloc[0]
                last_price = hist['Close'].iloc[-1]
                change = ((last_price - first_price) / first_price) * 100
                performance_data.append({
                    "symbol": symbol,
                    "name": MAGNIFICENT_SEVEN[symbol]['name'],
                    "emoji": MAGNIFICENT_SEVEN[symbol]['emoji'],
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
                <strong style="color: #37474F;">{item['emoji']} {item['name']}</strong>
                <span style="float: right; color: {color}; font-weight: 700; font-family: 'IBM Plex Mono', monospace;">
                    {item['change']:+.2f}%
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    # TAB 3: Alertas
    with tab3:
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
                format_func=lambda x: f"{MAGNIFICENT_SEVEN[x]['emoji']} {MAGNIFICENT_SEVEN[x]['name']}"
            )
            
            current_price = stock_data[alert_symbol]["current_price"] if stock_data[alert_symbol] else 0
            st.info(f"💵 Precio actual: **${current_price:.2f}**")
            
            alert_type = st.radio(
                "Tipo de alerta",
                options=["Precio objetivo (arriba)", "Precio objetivo (abajo)", "Cambio porcentual"]
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
            else:
                threshold = st.number_input(
                    "Cambio porcentual (%)",
                    min_value=0.0,
                    value=5.0,
                    step=0.5
                )
                alert_key = "change_percent"
            
            if st.button("➕ Añadir Alerta", use_container_width=True):
                if alert_symbol not in st.session_state.alerts:
                    st.session_state.alerts[alert_symbol] = {}
                st.session_state.alerts[alert_symbol][alert_key] = threshold
                save_alerts(st.session_state.alerts)  # Guardar en archivo
                st.success(f"✅ Alerta configurada para {alert_symbol}")
                st.rerun()
        
        with col2:
            st.markdown("#### 📋 Alertas Activas")
            
            if st.session_state.alerts:
                for symbol, configs in st.session_state.alerts.items():
                    with st.expander(f"{MAGNIFICENT_SEVEN[symbol]['emoji']} {symbol}", expanded=True):
                        for key, value in configs.items():
                            if key == "upper":
                                st.markdown(f"<span style='color: {COLORS['up']}'>📈</span> Precio arriba de: **${value:.2f}**", unsafe_allow_html=True)
                            elif key == "lower":
                                st.markdown(f"<span style='color: {COLORS['down']}'>📉</span> Precio abajo de: **${value:.2f}**", unsafe_allow_html=True)
                            else:
                                st.write(f"📊 Cambio mayor a: **{value:.1f}%**")
                        
                        if st.button(f"🗑️ Eliminar alertas de {symbol}", key=f"del_{symbol}"):
                            del st.session_state.alerts[symbol]
                            save_alerts(st.session_state.alerts)  # Guardar cambios
                            st.rerun()
                
                # Verificar alertas
                triggered = check_alerts(stock_data, st.session_state.alerts)
                
                if triggered:
                    st.markdown("---")
                    st.markdown("### ⚠️ Alertas Activadas")
                    for alert in triggered:
                        if alert["type"] == "upper":
                            st.markdown(f"""
                            <div class="alert-up">
                                📈 <strong>{alert['symbol']}</strong> ha superado ${alert['threshold']:.2f} 
                                (Actual: <span style="color: {COLORS['up']}; font-weight: bold;">${alert['price']:.2f}</span>)
                            </div>
                            """, unsafe_allow_html=True)
                        elif alert["type"] == "lower":
                            st.markdown(f"""
                            <div class="alert-down">
                                📉 <strong>{alert['symbol']}</strong> ha bajado de ${alert['threshold']:.2f} 
                                (Actual: <span style="color: {COLORS['down']}; font-weight: bold;">${alert['price']:.2f}</span>)
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            change_color = COLORS['up'] if alert['change'] >= 0 else COLORS['down']
                            st.markdown(f"""
                            <div class="{'alert-up' if alert['change'] >= 0 else 'alert-down'}">
                                📊 <strong>{alert['symbol']}</strong> ha cambiado 
                                <span style="color: {change_color}; font-weight: bold;">{alert['change']:.2f}%</span>
                                (Umbral: ±{alert['threshold']:.1f}%)
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("No hay alertas configuradas. Añade una alerta en el panel izquierdo.")
    
    # TAB 4: Portfolio
    with tab4:
        st.markdown("### 💼 Gestión de Portfolio")
        st.markdown("Registra tus inversiones y haz seguimiento de tu rendimiento.")
        
        # Cargar portfolio
        portfolio = load_portfolio()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### ➕ Añadir Posición")
            
            port_symbol = st.selectbox(
                "Acción",
                options=list(MAGNIFICENT_SEVEN.keys()),
                format_func=lambda x: f"{MAGNIFICENT_SEVEN[x]['emoji']} {MAGNIFICENT_SEVEN[x]['name']}",
                key="portfolio_symbol"
            )
            
            shares = st.number_input("Número de acciones", min_value=0.0, value=1.0, step=0.1)
            buy_price = st.number_input("Precio de compra ($)", min_value=0.0, value=100.0, step=1.0)
            buy_date = st.date_input("Fecha de compra", value=datetime.now())
            
            if st.button("💾 Guardar Posición", use_container_width=True):
                if port_symbol not in portfolio:
                    portfolio[port_symbol] = []
                
                portfolio[port_symbol].append({
                    "shares": shares,
                    "buy_price": buy_price,
                    "buy_date": buy_date.strftime("%Y-%m-%d")
                })
                
                save_portfolio(portfolio)
                st.success("✅ Posición guardada correctamente")
                st.rerun()
        
        with col2:
            st.markdown("#### 📊 Resumen del Portfolio")
            
            if portfolio:
                total_invested = 0
                total_current = 0
                portfolio_details = []
                
                for symbol, positions in portfolio.items():
                    if symbol in MAGNIFICENT_SEVEN:
                        current_price = stock_data.get(symbol, {})
                        if current_price and current_price.get("current_price"):
                            curr_price = current_price["current_price"]
                            
                            for pos in positions:
                                invested = pos["shares"] * pos["buy_price"]
                                current = pos["shares"] * curr_price
                                gain = current - invested
                                gain_pct = (gain / invested) * 100 if invested > 0 else 0
                                
                                total_invested += invested
                                total_current += current
                                
                                portfolio_details.append({
                                    "Acción": f"{MAGNIFICENT_SEVEN[symbol]['emoji']} {symbol}",
                                    "Acciones": pos['shares'],
                                    "P. Compra": pos['buy_price'],
                                    "P. Actual": curr_price,
                                    "Invertido": invested,
                                    "Valor": current,
                                    "Ganancia": gain,
                                    "Rend. %": gain_pct
                                })
                
                if portfolio_details:
                    # Métricas generales con colores
                    total_gain = total_current - total_invested
                    total_gain_pct = (total_gain / total_invested) * 100 if total_invested > 0 else 0
                    
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("💰 Invertido", f"${total_invested:,.2f}")
                    with m2:
                        st.metric("📈 Valor Actual", f"${total_current:,.2f}")
                    with m3:
                        st.metric("💵 Ganancia", f"${total_gain:+,.2f}", f"{total_gain_pct:+.2f}%")
                    
                    st.markdown("---")
                    
                    # Tabla con colores verde/rojo
                    df = pd.DataFrame(portfolio_details)
                    
                    def style_gains(val, col):
                        if col in ['Ganancia', 'Rend. %']:
                            color = COLORS["up"] if val >= 0 else COLORS["down"]
                            return f'color: {color}; font-weight: bold'
                        return ''
                    
                    styled_df = df.style.apply(lambda x: [style_gains(v, c) for c, v in x.items()], axis=1)
                    styled_df = styled_df.format({
                        'Acciones': '{:.2f}',
                        'P. Compra': '${:.2f}',
                        'P. Actual': '${:.2f}',
                        'Invertido': '${:.2f}',
                        'Valor': '${:.2f}',
                        'Ganancia': '${:+.2f}',
                        'Rend. %': '{:+.2f}%'
                    })
                    
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                    
                    # Gráfico de distribución con color único por acción
                    # Extraer símbolos de los detalles del portfolio
                    pie_colors = []
                    for d in portfolio_details:
                        symbol = d["Acción"].split()[-1]  # Obtener el símbolo (última palabra)
                        if symbol in MAGNIFICENT_SEVEN:
                            pie_colors.append(MAGNIFICENT_SEVEN[symbol]['color'])
                        else:
                            pie_colors.append('#B39DDB')  # Color por defecto
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=[d["Acción"] for d in portfolio_details],
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
                        title=dict(text="📊 Distribución del Portfolio", font=dict(color='#37474F', family='Nunito')),
                        template='plotly_white',
                        paper_bgcolor='rgba(255,255,255,0)',
                        plot_bgcolor='rgba(255,255,255,0)',
                        legend=dict(font=dict(color='#37474F', family='Nunito')),
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay posiciones en el portfolio. Añade tu primera inversión.")
            
            if portfolio and st.button("🗑️ Limpiar Portfolio", type="secondary"):
                save_portfolio({})
                st.rerun()


if __name__ == "__main__":
    main()
