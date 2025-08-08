import streamlit as st
import pandas as pd
from core.db import get_connection
from features.utils import registrar_entrada

# 🔄 Paginador elegante
def paginar_dataframe(df, filas_por_pagina=8, nombre="estadisticas"):
    total_filas = len(df)
    total_paginas = (total_filas - 1) // filas_por_pagina + 1
    pagina = st.number_input("📄 Página", min_value=1, max_value=total_paginas, value=1, key=f"pagina_{nombre}")
    inicio = (pagina - 1) * filas_por_pagina
    fin = inicio + filas_por_pagina
    st.dataframe(df.iloc[inicio:fin], use_container_width=True)
    st.caption(f"Mostrando registros {inicio + 1} - {min(fin, total_filas)} de {total_filas}")

# 🔍 Filtro por jugador o fecha
def filtrar_estadisticas(df, texto):
    return df[df["jugador"].str.lower().str.contains(texto.lower()) |
              df["fecha"].astype(str).str.contains(texto)]

def crud_estadisticas():
    st.title("📊 Gestión Profesional de Estadísticas de Jugadores")
    rol = st.session_state.get("rol")

    try:
        with st.spinner("Cargando estadísticas..."):
            conn = get_connection()
            cursor = conn.cursor()

            query = """
            SELECT est.id_estadistica, j.nombre AS jugador, p.fecha, 
                   est.goles, est.asistencias, est.minutos_jugados
            FROM estadisticas est
            JOIN jugadores j ON est.id_jugador = j.id_jugador
            JOIN partidos p ON est.id_partido = p.id_partido
            ORDER BY p.fecha DESC;
            """
            df = pd.read_sql(query, conn)

        st.subheader("📋 Estadísticas registradas")
        if df.empty:
            st.info("ℹ️ No hay estadísticas registradas.")
        else:
            filtro = st.text_input("🔎 Filtrar por jugador o fecha", placeholder="Ej. Messi, 2025-08-01")
            if filtro:
                df = filtrar_estadisticas(df, filtro)
            paginar_dataframe(df, nombre="estadisticas")

        # Obtener datos para formularios
        jugadores = pd.read_sql("SELECT id_jugador, nombre FROM jugadores ORDER BY nombre", conn)
        partidos = pd.read_sql("SELECT id_partido, fecha FROM partidos ORDER BY fecha DESC", conn)

        # ➕ Agregar nueva estadística
        if rol in ["admin", "usuario"] and not jugadores.empty and not partidos.empty:
            with st.expander("➕ Agregar nueva estadística"):
                with st.form("form_estadistica"):
                    col1, col2 = st.columns(2)
                    with col1:
                        jugador_sel = st.selectbox("👤 Jugador", jugadores["nombre"].tolist())
                        id_jugador = jugadores[jugadores["nombre"] == jugador_sel]["id_jugador"].values[0]
                        goles = st.number_input("⚽ Goles", min_value=0)
                        asistencias = st.number_input("🎯 Asistencias", min_value=0)
                    with col2:
                        partido_sel = st.selectbox("📅 Partido (fecha)", partidos["fecha"].astype(str).tolist())
                        id_partido = partidos[partidos["fecha"].astype(str) == partido_sel]["id_partido"].values[0]
                        minutos = st.number_input("⏱️ Minutos jugados", min_value=0, max_value=150)

                    if st.form_submit_button("💾 Guardar"):
                        if minutos <= 0:
                            st.warning("⚠️ Los minutos jugados deben ser mayores a 0.")
                        else:
                            cursor.execute("""
                                INSERT INTO estadisticas (id_jugador, id_partido, goles, asistencias, minutos_jugados)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (id_jugador, id_partido, goles, asistencias, minutos))
                            conn.commit()
                            registrar_entrada("estadisticas", "INSERT", f"{jugador_sel} - Goles: {goles}, Asistencias: {asistencias}")
                            st.success("✅ Estadística agregada correctamente")
                            st.rerun()

        # ✏️ Editar o eliminar estadísticas
        if rol == "admin" and not df.empty:
            st.subheader("✏️ Editar o eliminar estadísticas")
            id_sel = st.selectbox("🎯 Selecciona una estadística por ID", df["id_estadistica"].tolist())
            fila = df[df["id_estadistica"] == id_sel].iloc[0]

            with st.form("form_edit_est"):
                col1, col2 = st.columns(2)
                with col1:
                    nuevos_goles = st.number_input("⚽ Goles", min_value=0, value=fila["goles"])
                    nuevas_asistencias = st.number_input("🎯 Asistencias", min_value=0, value=fila["asistencias"])
                with col2:
                    nuevos_minutos = st.number_input("⏱️ Minutos jugados", min_value=0, value=fila["minutos_jugados"])

                col_guardar, col_eliminar = st.columns(2)
                with col_guardar:
                    if st.form_submit_button("💾 Guardar cambios"):
                        cursor.execute("""
                            UPDATE estadisticas
                            SET goles=%s, asistencias=%s, minutos_jugados=%s
                            WHERE id_estadistica=%s
                        """, (nuevos_goles, nuevas_asistencias, nuevos_minutos, id_sel))
                        conn.commit()
                        registrar_entrada("estadisticas", "UPDATE", f"Actualizada estadística ID {id_sel}")
                        st.success("✅ Estadística actualizada correctamente")
                        st.rerun()

                with col_eliminar:
                    if st.form_submit_button("🗑️ Eliminar"):
                        cursor.execute("DELETE FROM estadisticas WHERE id_estadistica=%s", (id_sel,))
                        conn.commit()
                        registrar_entrada("estadisticas", "DELETE", f"Eliminada estadística ID {id_sel}")
                        st.warning("⚠️ Estadística eliminada")
                        st.rerun()

    except Exception as e:
        st.error(f"❌ Error en la base de datos: {e}")
    finally:
        conn.close()
