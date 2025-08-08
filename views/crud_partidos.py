import streamlit as st
import pandas as pd
from core.db import get_connection
from features.utils import registrar_entrada

# 🔄 Paginador elegante
def paginar_dataframe(df, filas_por_pagina=8, nombre="partidos"):
    total_filas = len(df)
    total_paginas = (total_filas - 1) // filas_por_pagina + 1
    pagina = st.number_input("📄 Página", min_value=1, max_value=total_paginas, value=1, key=f"pagina_{nombre}")
    inicio = (pagina - 1) * filas_por_pagina
    fin = inicio + filas_por_pagina
    st.dataframe(df.iloc[inicio:fin], use_container_width=True)
    st.caption(f"Mostrando registros {inicio + 1} - {min(fin, total_filas)} de {total_filas}")

# 🔍 Filtro por nombre
def filtrar_por_equipo(df, texto):
    return df[df["equipo_local"].str.lower().str.contains(texto.lower()) |
              df["equipo_visitante"].str.lower().str.contains(texto.lower())]

def crud_partidos():
    st.title("📅 Gestión Profesional de Partidos")
    rol = st.session_state.get("rol")

    try:
        with st.spinner("Cargando datos de partidos..."):
            conn = get_connection()
            cursor = conn.cursor()

            query = """
            SELECT p.id_partido, p.fecha, el.nombre_equipo AS equipo_local, ev.nombre_equipo AS equipo_visitante,
                   p.marcador_local, p.marcador_visitante,
                   p.equipo_local AS id_local, p.equipo_visitante AS id_visitante
            FROM partidos p
            JOIN equipos el ON p.equipo_local = el.id_equipo
            JOIN equipos ev ON p.equipo_visitante = ev.id_equipo
            ORDER BY p.fecha DESC;
            """
            df = pd.read_sql(query, conn)

        st.subheader("📋 Partidos registrados")
        if df.empty:
            st.info("ℹ️ No hay partidos registrados aún.")
        else:
            filtro = st.text_input("🔎 Filtrar por nombre de equipo", placeholder="Ej. Barcelona, Emelec")
            if filtro:
                df = filtrar_por_equipo(df, filtro)
            paginar_dataframe(df.drop(columns=["id_local", "id_visitante"]), nombre="partidos")

        # ➕ Agregar partido
        if rol in ["admin", "usuario"]:
            with st.expander("➕ Agregar nuevo partido"):
                with st.form("form_partido"):
                    col1, col2 = st.columns(2)
                    with col1:
                        fecha = st.date_input("📅 Fecha del partido")
                        marcador_local = st.number_input("⚽ Goles equipo local", min_value=0)
                        marcador_visitante = st.number_input("⚽ Goles equipo visitante", min_value=0)
                    with col2:
                        equipo_local = st.number_input("🏠 ID equipo local", min_value=1)
                        equipo_visitante = st.number_input("🛫 ID equipo visitante", min_value=1)

                    if st.form_submit_button("💾 Guardar"):
                        if equipo_local == equipo_visitante:
                            st.warning("⚠️ Los equipos no pueden ser iguales.")
                        else:
                            cursor.execute("""
                                INSERT INTO partidos (fecha, equipo_local, equipo_visitante, marcador_local, marcador_visitante)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (fecha, equipo_local, equipo_visitante, marcador_local, marcador_visitante))
                            conn.commit()
                            registrar_entrada("partidos", "INSERT", f"Se agregó partido el {fecha}")
                            st.success("✅ Partido agregado correctamente")
                            st.rerun()

        # ✏️ Editar / eliminar
        if rol == "admin" and not df.empty:
            st.subheader("✏️ Editar o eliminar partido")
            id_sel = st.selectbox("🎯 Selecciona un partido por ID", df["id_partido"].tolist())
            partido = df[df["id_partido"] == id_sel].iloc[0]

            with st.form("form_editar_partido"):
                col1, col2 = st.columns(2)
                with col1:
                    nueva_fecha = st.date_input("📅 Fecha", partido["fecha"])
                    nuevo_marcador_local = st.number_input("⚽ Goles local", value=partido["marcador_local"], min_value=0)
                    nuevo_marcador_visitante = st.number_input("⚽ Goles visitante", value=partido["marcador_visitante"], min_value=0)
                with col2:
                    nuevo_local = st.number_input("🏠 ID equipo local", value=int(partido["id_local"]), min_value=1)
                    nuevo_visitante = st.number_input("🛫 ID equipo visitante", value=int(partido["id_visitante"]), min_value=1)

                col_guardar, col_eliminar = st.columns(2)
                with col_guardar:
                    if st.form_submit_button("💾 Guardar cambios"):
                        if nuevo_local == nuevo_visitante:
                            st.warning("⚠️ Los equipos no pueden ser iguales.")
                        else:
                            cursor.execute("""
                                UPDATE partidos SET fecha=%s, equipo_local=%s, equipo_visitante=%s,
                                                    marcador_local=%s, marcador_visitante=%s
                                WHERE id_partido=%s
                            """, (nueva_fecha, nuevo_local, nuevo_visitante,
                                  nuevo_marcador_local, nuevo_marcador_visitante, id_sel))
                            conn.commit()
                            registrar_entrada("partidos", "UPDATE", f"Actualizado partido ID {id_sel}")
                            st.success("✅ Partido actualizado correctamente")
                            st.rerun()

                with col_eliminar:
                    if st.form_submit_button("🗑️ Eliminar partido"):
                        cursor.execute("DELETE FROM partidos WHERE id_partido = %s", (id_sel,))
                        conn.commit()
                        registrar_entrada("partidos", "DELETE", f"Eliminado partido ID {id_sel}")
                        st.warning("⚠️ Partido eliminado")
                        st.rerun()

    except Exception as e:
        st.error(f"❌ Error en la base de datos: {e}")
    finally:
        conn.close()
