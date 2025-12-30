import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# 1. Configuración de la app
# -----------------------------
st.set_page_config(
    page_title="Emergencias Chile - Datos Abiertos",
    layout="wide",
    page_icon="🚨"
)
st.title("🚨 Emergencias y Datos Públicos en Chile")
st.markdown(
    "Proyecto Final - Solemne II  \n"
    "Análisis interactivo de un dataset público desde API REST de datos.gob.cl"
)

# -----------------------------
# 2. Función para cargar datos desde API REST
# -----------------------------
@st.cache_data
def cargar_datos():
    resource_id = "caeb64a6-7a5c-4ed5-8dfa-2b41502b7d95"  # Dataset válido
    url = f"https://datos.gob.cl/api/3/action/datastore_search?resource_id={resource_id}&limit=500"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if "result" in data and "records" in data["result"]:
            df = pd.DataFrame(data["result"]["records"])
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con la API: {e}")
        return pd.DataFrame()

# -----------------------------
# 3. Cargar y verificar datos
# -----------------------------
with st.spinner("Cargando datos desde la API..."):
    df = cargar_datos()

if df.empty:
    st.error("No se pudieron cargar datos desde la API REST. Verifica tu conexión o el dataset.")
    st.stop()

st.success("✅ Datos cargados correctamente desde la API REST")

# Normalizar nombres de columnas
df.columns = df.columns.str.lower()

# -----------------------------
# 4. Filtros interactivos en sidebar
# -----------------------------
st.sidebar.header("Filtros de datos")

# Filtrar por región si existe la columna
if "region" in df.columns:
    regiones = sorted(df["region"].dropna().unique())
    region_sel = st.sidebar.selectbox("Seleccione una región", regiones)
    df_filtrado = df[df["region"] == region_sel]
else:
    df_filtrado = df

# Filtrar por otra columna si quieres (opcional)
# e.g., comuna
if "comuna" in df_filtrado.columns:
    comunas = sorted(df_filtrado["comuna"].dropna().unique())
    comuna_sel = st.sidebar.multiselect("Filtrar por comuna", comunas)
    if comuna_sel:
        df_filtrado = df_filtrado[df_filtrado["comuna"].isin(comuna_sel)]

# -----------------------------
# 5. Mostrar datos
# -----------------------------
st.subheader("📋 Tabla de datos filtrada")
st.write(f"Mostrando **{len(df_filtrado)} registros** para la selección actual")
st.dataframe(df_filtrado, use_container_width=True)

# -----------------------------
# 6. Gráficos interactivos
# -----------------------------
st.subheader("📊 Visualización de frecuencia")

# Selección de columna para gráfico
columna_grafico = st.selectbox(
    "Seleccione la columna para visualizar frecuencia",
    df_filtrado.columns.tolist(),
    index=df_filtrado.columns.get_loc("comuna") if "comuna" in df_filtrado.columns else 0
)

conteo = df_filtrado[columna_grafico].value_counts()

fig, ax = plt.subplots(figsize=(12, 5))
conteo.plot(kind="bar", color="#FF5733", edgecolor="black", ax=ax)
plt.xticks(rotation=45, ha="right")
plt.xlabel(columna_grafico.capitalize())
plt.ylabel("Cantidad de registros")
plt.title(f"Frecuencia de {columna_grafico.capitalize()}", fontsize=14)
plt.tight_layout()
st.pyplot(fig)

# -----------------------------
# 7. Mensaje final
# -----------------------------
st.markdown(
    "📌 **Nota:** Esta aplicación utiliza datos abiertos de Chile a través de una API REST pública "
    "y permite explorar los registros de forma interactiva."
)
