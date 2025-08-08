# vistas_globales.py

import streamlit as st
import pandas as pd
import psycopg2
import io
from streamlit_lottie import st_lottie
import json
import matplotlib.pyplot as plt

# 🎨 Animación
def cargar_animacion(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"No se pudo cargar la animación: {e}")
        return None

# ⚙️ Conexión
def conectar_bd():
    return psycopg2.connect(
        host="localhost",
        database="futbol_gestion",
        user="postgres",
        password="12345"
    )

# 🧾 Cargar vista
def cargar_vista(nombre_vista):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {nombre_vista}")
    columnas = [desc[0] for desc in cursor.description]
    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(datos, columns=columnas)

# 📤 Exportar Excel
def descargar_excel(df, nombre_archivo):
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    st.download_button(
        label="📥 Descargar Excel",
        data=buffer.getvalue(),
        file_name=nombre_archivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# 📊 Gráfico básico por columna
def mostrar_graficos(df):
    st.markdown("### 📈 Gráficos")
    if 'jugador' in df.columns and 'goles' in df.columns:
        goles = df.groupby('jugador')['goles'].sum().sort_values()
        st.bar_chart(goles)
    if 'equipo' in df.columns:
        equipo_counts = df['equipo'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(equipo_counts, labels=equipo_counts.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

# 🖥️ Interfaz principal
def mostrar_vistas():
    st.set_page_config(page_title="Vistas Globales", layout="wide")

    animacion = cargar_animacion("animaciones/futbol.json")
    if animacion:
        st_lottie(animacion, height=180, speed=1, key="animacion_futbol")

    st.title("📊 Reportes Globales del Sistema Futbolístico")
    st.markdown("Consulta las vistas avanzadas del sistema de forma elegante y profesional.")

    opcion = st.selectbox("🔎 Selecciona una vista para mostrar:", (
        "📈 Estadísticas de jugadores",
        "⚽ Partidos completos",
        "🟥 Sanciones por jugador"
    ))

    vista_dict = {
        "📈 Estadísticas de jugadores": ("vista_estadisticas_jugadores", "estadisticas_jugadores.xlsx"),
        "⚽ Partidos completos": ("vista_partidos_completos", "partidos_completos.xlsx"),
        "🟥 Sanciones por jugador": ("vista_sanciones_jugadores", "sanciones_por_jugador.xlsx")
    }

    nombre_vista, archivo_excel = vista_dict[opcion]
    df = cargar_vista(nombre_vista)

    with st.expander("📋 Vista completa con filtros, paginación y exportación"):
        if df.empty:
            st.warning("⚠️ No hay datos disponibles.")
        else:
            # 🔍 Filtro por columnas
            columnas_filtrables = st.multiselect("🔎 Filtrar por columnas:", df.columns.tolist())
            for col in columnas_filtrables:
                valores = df[col].unique()
                seleccionados = st.multiselect(f"Filtrar {col}:", valores)
                if seleccionados:
                    df = df[df[col].isin(seleccionados)]

            # 📄 Paginación
            filas_por_pagina = st.selectbox("📄 Filas por página:", [5, 10, 20, 50], index=1)
            total_filas = len(df)
            total_paginas = (total_filas - 1) // filas_por_pagina + 1
            pagina_actual = st.number_input("📍 Página:", min_value=1, max_value=total_paginas, step=1)

            inicio = (pagina_actual - 1) * filas_por_pagina
            fin = inicio + filas_por_pagina
            st.dataframe(df.iloc[inicio:fin], use_container_width=True)

            descargar_excel(df, archivo_excel)

            # 📊 Mostrar gráficos decorativos
            mostrar_graficos(df)

# Ejecutar directamente
if __name__ == "__main__":
    mostrar_vistas()
