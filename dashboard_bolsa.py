import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Configurar la página de Streamlit para que use un layout amplio
st.set_page_config(
    page_title="Dashboard IBEX 35",
    page_icon="📈",
    layout="wide"
)

# Título de la aplicación
st.title("📈 Análisis Histórico de Acciones del IBEX 35")
st.markdown("---")  # Línea separadora

# Cargar los datos desde el CSV
@st.cache_data  # Esta decoración evita que se recarguen los datos cada vez que interactúas con la página (mejora el rendimiento)
def load_data():
    # Leer el archivo CSV
    df = pd.read_csv('precios_cierre_bolsa.csv')
    # Asegurarse de que la columna 'Fecha' es de tipo datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    return df

df = load_data()

# --- Sidebar (Panel de control lateral) ---
st.sidebar.header("Filtros")

# 1. Selector de Ticker (Acción)
tickers_unicos = df['Ticker'].unique()
ticker_seleccionado = st.sidebar.selectbox(
    'Selecciona una Acción:',
    options=tickers_unicos
)

# 2. Selector de Rango de Fechas
fecha_min = df['Fecha'].min()
fecha_max = df['Fecha'].max()
rango_fechas = st.sidebar.date_input(
    "Selecciona un Rango de Fechas:",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

# --- Aplicar Filtros al DataFrame ---
# A veces el widget de fecha devuelve 1 o 2 valores, esto lo maneja.
if len(rango_fechas) == 2:
    fecha_inicio, fecha_fin = rango_fechas
    df_filtrado = df[(df['Ticker'] == ticker_seleccionado) & 
                     (df['Fecha'] >= pd.to_datetime(fecha_inicio)) & 
                     (df['Fecha'] <= pd.to_datetime(fecha_fin))]
else:
    df_filtrado = df[df['Ticker'] == ticker_seleccionado]

# --- Cálculo de la Variación Porcentual del Día ---
# Ordenar por fecha para asegurar el cálculo correcto
df_ordenado = df_filtrado.sort_values('Fecha')
if len(df_ordenado) > 1:
    precio_actual = df_ordenado['Precio_Cierre'].iloc[-1]
    precio_anterior = df_ordenado['Precio_Cierre'].iloc[-2]
    variacion_porcentual = ((precio_actual - precio_anterior) / precio_anterior) * 100
else:
    variacion_porcentual = 0.0

# Mostrar la variación en un cuadro llamativo
color_variacion = "red" if variacion_porcentual < 0 else "green"
st.metric(
    label=f"Precio de {ticker_seleccionado}",
    value=f"{precio_actual:.2f} €",
    delta=f"{variacion_porcentual:.2f} %",
    delta_color="normal"  # Streamlit usa rojo/verde automáticamente
)

# --- Gráfico Principal: Evolución del Precio ---
st.header("Evolución del Precio de Cierre")
fig = px.line(
    df_filtrado,
    x='Fecha',
    y='Precio_Cierre',
    title=f'Evolución de {ticker_seleccionado}',
    labels={'Precio_Cierre': 'Precio (€)', 'Fecha': 'Fecha'}
)
# Personalizar el gráfico
fig.update_layout(
    xaxis=dict(showgrid=True),
    yaxis=dict(showgrid=True),
    hovermode='x unified'
)
# Mostrar el gráfico en la app
st.plotly_chart(fig, use_container_width=True)

# --- Tabla de Datos Históricos ---
st.header("Datos Históricos")
# Formatear la fecha para mostrarla mejor y redondear el precio
df_mostrar = df_filtrado.copy()
df_mostrar['Fecha'] = df_mostrar['Fecha'].dt.strftime('%d-%m-%Y')
df_mostrar['Precio_Cierre'] = df_mostrar['Precio_Cierre'].round(2)
st.dataframe(df_mostrar, hide_index=True, use_container_width=True)

# --- Información Adicional en el Sidebar ---
st.sidebar.markdown("---")
st.sidebar.info("""
**💡 Información:**
- Los datos se recogen automáticamente al cierre de mercado.
- La variación porcentual se calcula respecto al día anterior.
- Utiliza los filtros para personalizar la vista.
""")