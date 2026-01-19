# 📈 NASDAQ Magnificent Seven Tracker

Aplicación web para monitorear en tiempo real las 7 grandes tecnológicas del NASDAQ:

- 🔍 **Alphabet (Google)** - GOOGL
- 📦 **Amazon** - AMZN
- 🍎 **Apple** - AAPL
- 👤 **Meta (Facebook)** - META
- 🪟 **Microsoft** - MSFT
- 🎮 **NVIDIA** - NVDA
- 🚗 **Tesla** - TSLA

## ✨ Características

### 📊 Dashboard
- Precios en tiempo real
- Gráficos interactivos de evolución
- Métricas detalladas (P/E, Market Cap, 52W High/Low)

### 📈 Comparativas
- Rendimiento normalizado entre acciones
- Ranking de performance
- Gráficos de capitalización de mercado

### 🔔 Alertas
- Configura alertas de precio objetivo
- Alertas por cambio porcentual
- Notificaciones en tiempo real

### 💼 Portfolio
- Registra tus inversiones
- Seguimiento de ganancias/pérdidas
- Distribución visual del portfolio

## 🚀 Instalación

### Requisitos
- Python 3.8 o superior

### Pasos

1. **Clonar o descargar el proyecto**

2. **Crear entorno virtual (recomendado)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**
```bash
streamlit run app.py
```

5. **Abrir en el navegador**
   - La aplicación se abrirá automáticamente en `http://localhost:8501`

## 📦 Dependencias

- **Streamlit**: Framework para la interfaz web
- **yfinance**: Obtención de datos del mercado (Yahoo Finance)
- **Pandas**: Manipulación de datos
- **Plotly**: Gráficos interactivos
- **NumPy**: Cálculos numéricos

## 🎨 Interfaz

La aplicación cuenta con un diseño moderno y oscuro, optimizado para visualización de datos financieros:

- Tema oscuro tecnológico
- Gráficos interactivos con Plotly
- Diseño responsive
- Actualizaciones automáticas opcionales

## ☁️ Despliegue en Streamlit Cloud

### Pasos para desplegar

1. **Sube el proyecto a GitHub**
   - Crea un repositorio en [github.com](https://github.com)
   - Sube todos los archivos del proyecto

2. **Accede a Streamlit Cloud**
   - Ve a [share.streamlit.io](https://share.streamlit.io)
   - Inicia sesión con tu cuenta de GitHub

3. **Despliega la app**
   - Haz clic en "New app"
   - Selecciona tu repositorio
   - Branch: `main`
   - Main file: `app.py`
   - Haz clic en "Deploy"

4. **Accede desde tu smartphone**
   - La app estará disponible en: `https://tu-usuario-nasdaq-web.streamlit.app`
   - Añade a la pantalla de inicio de tu móvil para acceso rápido

### ⚠️ Nota importante sobre datos
En Streamlit Cloud, los archivos `portfolio.json` y `alerts.json` **se reinician** cada vez que la app se reinicia. Para persistencia permanente, considera usar una base de datos externa (Firebase, Supabase, etc.).

---

## 📝 Notas

- Los datos son proporcionados por Yahoo Finance
- La información tiene un retraso de ~15 minutos (datos gratuitos)
- El portfolio se guarda localmente en `portfolio.json` (en modo local)
- En Streamlit Cloud, los datos del portfolio no persisten entre reinicios

## 🛠️ Personalización

Puedes modificar las acciones a seguir editando el diccionario `MAGNIFICENT_SEVEN` en `app.py`:

```python
MAGNIFICENT_SEVEN = {
    "GOOGL": {"name": "Alphabet (Google)", "emoji": "🔍", "color": "#4285F4"},
    # Añade más acciones aquí...
}
```

---

**Desarrollado con ❤️ usando Python y Streamlit**
