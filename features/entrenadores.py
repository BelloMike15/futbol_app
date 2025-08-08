import streamlit as st
import psycopg2
import pandas as pd
import math
import os
from dotenv import load_dotenv






ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
env_file = ".env" if os.getenv("ENV", "local") == "local" else ".env.prod"
load_dotenv(os.path.join(ROOT, env_file))

# Función para conectar con la base de datos
def conectar_bd():
    return psycopg2.connect(
        host="localhost",
        database="futbol_gestion",
        user="postgres",
        password="12345"
    )

# Obtener lista de equipos
def obtener_equipos():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id_equipo, nombre_equipo FROM equipos ORDER BY nombre_equipo")
    equipos = cursor.fetchall()
    conn.close()
    return equipos

# Mostrar entrenadores existentes
def mostrar_entrenadores():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT en.id_entrenador, en.nombre, en.nacionalidad, en.edad, eq.nombre_equipo AS equipo
        FROM entrenadores en
        LEFT JOIN equipos eq ON en.id_equipo = eq.id_equipo
        ORDER BY en.nombre;
    """)
    columnas = [desc[0] for desc in cursor.description]
    datos = cursor.fetchall()
    conn.close()
    return pd.DataFrame(datos, columns=columnas)

# Registrar nuevo entrenador
def registrar_entrenador(nombre, nacionalidad, edad, id_equipo):
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO entrenadores (nombre, nacionalidad, edad, id_equipo)
            VALUES (%s, %s, %s, %s)
        """, (nombre, nacionalidad, edad, id_equipo))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Error al registrar: {e}")
        return False

# Función para paginar un DataFrame
def paginar_dataframe(df, pagina, filas_por_pagina):
    total_filas = len(df)
    total_paginas = math.ceil(total_filas / filas_por_pagina)
    inicio = pagina * filas_por_pagina
    fin = inicio + filas_por_pagina
    return df.iloc[inicio:fin], total_paginas

# Interfaz principal
def mostrar_pantalla_entrenadores():
    st.title("🧠 Gestión de Entrenadores")
    st.caption("Registra y visualiza los entrenadores de los equipos disponibles.")

    # ➕ Formulario
    with st.expander("➕ Registrar nuevo entrenador"):
        st.markdown("### 📌 Formulario de registro")
        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input("🧑 Nombre completo")
            nacionalidad = st.text_input("🌎 Nacionalidad")

        with col2:
            edad = st.number_input("🎂 Edad", min_value=30, max_value=70, step=1)

            equipos = obtener_equipos()
            nombres_equipos = [e[1] for e in equipos]
            seleccionado = st.selectbox("🏟️ Equipo asignado", nombres_equipos)
            id_equipo = [e[0] for e in equipos if e[1] == seleccionado][0]

        col_reg, _ = st.columns(2)
        with col_reg:
            if st.button("💾 Registrar entrenador"):
                if nombre.strip() and nacionalidad.strip():
                    exito = registrar_entrenador(nombre, nacionalidad, edad, id_equipo)
                    if exito:
                        st.success("✅ Entrenador registrado correctamente.")
                        st.rerun()
                else:
                    st.warning("⚠️ Todos los campos deben estar completos.")

    # 📋 Tabla de entrenadores con paginación
    st.markdown("### 📋 Lista de entrenadores registrados")

    df = mostrar_entrenadores()
    if df.empty:
        st.info("ℹ️ No hay entrenadores registrados aún.")
    else:
        filas_por_pagina = 10
        total_paginas = math.ceil(len(df) / filas_por_pagina)

        if "pagina_entrenador" not in st.session_state:
            st.session_state.pagina_entrenador = 0

        col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
        with col_pag1:
            if st.button("⬅️ Anterior", disabled=st.session_state.pagina_entrenador == 0):
                st.session_state.pagina_entrenador -= 1

        with col_pag2:
            st.markdown(f"<center><b>Página {st.session_state.pagina_entrenador + 1} de {total_paginas}</b></center>", unsafe_allow_html=True)

        with col_pag3:
            if st.button("➡️ Siguiente", disabled=st.session_state.pagina_entrenador + 1 >= total_paginas):
                st.session_state.pagina_entrenador += 1

        df_pagina, _ = paginar_dataframe(df, st.session_state.pagina_entrenador, filas_por_pagina)
        st.dataframe(df_pagina, use_container_width=True)

# Ejecutar directamente si se llama el script
if __name__ == "__main__":
    mostrar_pantalla_entrenadores()
