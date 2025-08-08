import streamlit as st
import pandas as pd
from features.utils import registrar_entrada
from core.db import get_connection

# 🔍 Filtrado por búsqueda
def filtrar_por_nombre(df, termino):
    return df[df["nombre"].str.lower().str.contains(termino.lower())]

# 🔄 Paginación
def paginar_dataframe(df, filas_por_pagina=10, nombre="tabla"):
    total_filas = len(df)
    total_paginas = (total_filas - 1) // filas_por_pagina + 1
    pagina = st.number_input("📄 Página", min_value=1, max_value=total_paginas, value=1, key=f"pagina_{nombre}")
    inicio, fin = (pagina - 1) * filas_por_pagina, (pagina) * filas_por_pagina
    st.dataframe(df.iloc[inicio:fin], use_container_width=True)
    st.caption(f"Mostrando registros {inicio + 1} - {min(fin, total_filas)} de {total_filas}")

# 🌟 Vista principal
def crud_jugadores():
    st.title("⚽ Gestión Profesional de Jugadores")
    rol = st.session_state.get("rol")

    try:
        with st.spinner("Cargando jugadores..."):
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT j.id_jugador, j.nombre, j.edad, j.nacionalidad, j.posicion, j.id_equipo, e.nombre_equipo
                FROM jugadores j
                LEFT JOIN equipos e ON j.id_equipo = e.id_equipo
                ORDER BY j.id_jugador;
            """
            df = pd.read_sql(query, conn)

            st.subheader("📋 Jugadores registrados")
            filtro = st.text_input("🔍 Buscar por nombre", placeholder="Ej. Messi")
            if filtro:
                df = filtrar_por_nombre(df, filtro)

            paginar_dataframe(df, filas_por_pagina=8, nombre="jugadores")

        if rol in ["admin", "usuario"]:
            with st.expander("➕ Agregar nuevo jugador"):
                with st.form("form_nuevo_jugador"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nombre = st.text_input("🧾 Nombre completo")
                        edad = st.number_input("🎂 Edad", min_value=15, max_value=50)
                        nacionalidad = st.text_input("🌍 Nacionalidad")
                    with col2:
                        posicion = st.selectbox("📌 Posición", ["Delantero", "Mediocampista", "Defensa", "Portero"])
                        id_equipo = st.number_input("🏟️ ID del equipo", min_value=1)

                    if st.form_submit_button("💾 Guardar"):
                        if not nombre.strip() or not nacionalidad.strip():
                            st.warning("⚠️ Todos los campos deben estar completos.")
                        else:
                            cursor.execute("""
                                INSERT INTO jugadores (nombre, edad, nacionalidad, posicion, id_equipo)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (nombre, edad, nacionalidad, posicion, id_equipo))
                            conn.commit()
                            registrar_entrada("jugadores", "INSERT", f"Se agregó jugador: {nombre}")
                            st.success("✅ Jugador agregado correctamente")
                            st.rerun()

        if rol == "admin" and not df.empty:
            st.subheader("✏️ Editar o eliminar jugador existente")
            id_sel = st.selectbox("🎯 Selecciona un jugador por ID", df["id_jugador"].tolist())
            jugador = df[df["id_jugador"] == id_sel].iloc[0]

            with st.form("form_editar_jugador"):
                col1, col2 = st.columns(2)
                with col1:
                    nuevo_nombre = st.text_input("🧾 Nombre", jugador["nombre"])
                    nueva_edad = st.number_input("🎂 Edad", 15, 50, jugador["edad"])
                    nueva_nacionalidad = st.text_input("🌍 Nacionalidad", jugador["nacionalidad"])
                with col2:
                    nueva_posicion = st.selectbox(
                        "📌 Posición", ["Delantero", "Mediocampista", "Defensa", "Portero"],
                        index=["Delantero", "Mediocampista", "Defensa", "Portero"].index(jugador["posicion"])
                    )
                    nuevo_id_equipo = st.number_input("🏟️ ID del equipo", min_value=1, value=jugador["id_equipo"])

                col1_btn, col2_btn = st.columns(2)
                with col1_btn:
                    if st.form_submit_button("💾 Guardar cambios"):
                        cursor.execute("""
                            UPDATE jugadores
                            SET nombre=%s, edad=%s, nacionalidad=%s, posicion=%s, id_equipo=%s
                            WHERE id_jugador=%s
                        """, (nuevo_nombre, nueva_edad, nueva_nacionalidad, nueva_posicion, nuevo_id_equipo, id_sel))
                        conn.commit()
                        registrar_entrada("jugadores", "UPDATE", f"Actualizado jugador ID {id_sel}: {nuevo_nombre}")
                        st.success("✅ Jugador actualizado correctamente")
                        st.rerun()

                with col2_btn:
                    if st.form_submit_button("🗑️ Eliminar jugador"):
                        cursor.execute("DELETE FROM jugadores WHERE id_jugador = %s", (id_sel,))
                        conn.commit()
                        registrar_entrada("jugadores", "DELETE", f"Eliminado jugador ID {id_sel}")
                        st.warning("⚠️ Jugador eliminado")
                        st.rerun()

    except Exception as e:
        st.error(f"❌ Error: {e}")
    finally:
        conn.close()
