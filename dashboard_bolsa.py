import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# ==============================
# 1. Cargar y preparar datos
# ==============================
file_path = "precios_cierre_bolsa.csv"
df = pd.read_csv(file_path, parse_dates=["Fecha"])

# Última cotización del día por Ticker
df = df.sort_values(["Ticker", "Fecha", "Hora"]).drop_duplicates(
    subset=["Fecha", "Ticker"], keep="last"
)

# Pivotar: columnas = fechas, valores = precios
precios = df.pivot(index="Ticker", columns="Fecha", values="Precio_Cierre")

# Variación %
variacion = precios.pct_change(axis=1) * 100

# Crear tabla final intercalando Precio / %
tabla_final = pd.DataFrame(index=precios.index)

for fecha in precios.columns:
    #fecha_str = fecha.date().strftime("%Y-%m-%d")
    fecha_str = fecha.date().strftime("%d-%m-%y")
    tabla_final[f"{fecha_str} €"] = precios[fecha].round(2)
    tabla_final[f"{fecha_str} %"] = variacion[fecha].round(2)

tabla_final = tabla_final.reset_index()

# ==============================
# 2. Streamlit App
# ==============================
st.set_page_config(page_title="Dashboard IBEX35", layout="wide")
st.title("Dashboard IBEX35 Profesional - AgGrid")

# ==============================
# 3. Configuración de AgGrid
# ==============================
gb = GridOptionsBuilder.from_dataframe(tabla_final)

# Congelar primera columna
gb.configure_column("Ticker", pinned="left", width=100)

# Configuración general
gb.configure_default_column(
    editable=False,
    filter=True,
    sortable=True,
    resizable=True,
    minWidth=80
)

# Formato condicional %
cellsytle_jscode = JsCode("""
function(params) {
    if (params.value == null) {return {}}
    if (params.value > 0) {return {'color': 'green', 'font-weight': 'bold'};}
    else if (params.value < 0) {return {'color': 'red', 'font-weight': 'bold'};}
    else {return {};}
};
""")

for col in tabla_final.columns:
    if "%" in col:
        gb.configure_column(col, cellStyle=cellsytle_jscode, type=["numericColumn","numberColumnFilter","customNumericFormat"], precision=2)

grid_options = gb.build()

AgGrid(
    tabla_final,
    gridOptions=grid_options,
    enable_enterprise_modules=False,
    theme="alpine",
    height=600,
    width='100%',
    fit_columns_on_grid_load=False,  # <--- desactivado
    allow_unsafe_jscode=True
)