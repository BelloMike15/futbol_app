import streamlit as st
import pandas as pd
from features.utils import registrar_entrada
from core.db import get_connection

# 🔍 Filtro por nombre
def filtrar_por_nombre(df, termino):
    return df[df["nombre_equipo"].str.lower().str.contains(termino.lower())]

# 🔄 Paginación
def paginar_dataframe(df, filas_por_pagina=8, nombre="equipos"):
    total_filas = len(df)
    total_paginas = (total_filas - 1) // filas_por_pagina + 1
    pagina = st.number_input("📄 Página", min_value=1, max_value=total_paginas, value=1, key=f"pagina_{nombre}")
    inicio, fin = (pagina - 1) * filas_por_pagina, pagina * filas_por_pagina
    st.dataframe(df.iloc[inicio:fin], use_container_width=True)
    st.caption(f"Mostrando registros {inicio + 1} - {min(fin, total_filas)} de {total_filas}")

# 🌟 Vista principal
def crud_equipos():
    st.title("🏟️ Gestión Profesional de Equipos")
    rol = st.session_state.get("rol")

    try:
        with st.spinner("Cargando equipos..."):
            conn = get_connection()
            cursor = conn.cursor()

            query = "SELECT * FROM equipos ORDER BY id_equipo;"
            df = pd.read_sql(query, conn)

            st.subheader("📋 Equipos registrados")
            filtro = st.text_input("🔍 Buscar por nombre del equipo", placeholder="Ej. Barcelona SC")
            if filtro:
                df = filtrar_por_nombre(df, filtro)

            paginar_dataframe(df, filas_por_pagina=8, nombre="equipos")

        # ➕ Agregar equipo
        if rol in ["admin", "usuario"]:
            with st.expander("➕ Agregar nuevo equipo"):
                with st.form("form_equipo"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nombre = st.text_input("📛 Nombre del equipo")
                        pais = st.text_input("🌍 País")
                    with col2:
                        estadio = st.text_input("🏟️ Estadio")

                    if st.form_submit_button("💾 Guardar"):
                        if not nombre.strip() or not pais.strip() or not estadio.strip():
                            st.warning("⚠️ Todos los campos son obligatorios.")
                        else:
                            cursor.execute(
                                "INSERT INTO equipos (nombre_equipo, pais, estadio) VALUES (%s, %s, %s)",
                                (nombre, pais, estadio)
                            )
                            conn.commit()
                            registrar_entrada("equipos", "INSERT", f"Se agregó equipo: {nombre}")
                            st.success("✅ Equipo agregado correctamente")
                            st.rerun()

        # ✏️ Editar / eliminar equipo
        if rol == "admin" and not df.empty:
            st.subheader("✏️ Editar o eliminar equipo")
            id_sel = st.selectbox("🎯 Selecciona un equipo por ID", df["id_equipo"].tolist())
            equipo = df[df["id_equipo"] == id_sel].iloc[0]

            with st.form("form_editar_equipo"):
                col1, col2 = st.columns(2)
                with col1:
                    nuevo_nombre = st.text_input("📛 Nombre del equipo", equipo["nombre_equipo"])
                    nuevo_pais = st.text_input("🌍 País", equipo["pais"])
                with col2:
                    nuevo_estadio = st.text_input("🏟️ Estadio", equipo["estadio"])

                col_guardar, col_eliminar = st.columns(2)
                with col_guardar:
                    if st.form_submit_button("💾 Guardar cambios"):
                        if not nuevo_nombre.strip() or not nuevo_pais.strip() or not nuevo_estadio.strip():
                            st.warning("⚠️ Todos los campos deben estar completos.")
                        else:
                            cursor.execute(
                                "UPDATE equipos SET nombre_equipo=%s, pais=%s, estadio=%s WHERE id_equipo=%s",
                                (nuevo_nombre, nuevo_pais, nuevo_estadio, id_sel)
                            )
                            conn.commit()
                            registrar_entrada("equipos", "UPDATE", f"Actualizado equipo ID {id_sel}: {nuevo_nombre}")
                            st.success("✅ Equipo actualizado correctamente")
                            st.rerun()

                with col_eliminar:
                    if st.form_submit_button("🗑️ Eliminar equipo"):
                        cursor.execute("DELETE FROM equipos WHERE id_equipo = %s", (id_sel,))
                        conn.commit()
                        registrar_entrada("equipos", "DELETE", f"Eliminado equipo ID {id_sel}")
                        st.warning("⚠️ Equipo eliminado")
                        st.rerun()

    except Exception as e:
        st.error(f"❌ Error al conectar con la base de datos: {e}")
    finally:
        conn.close()
