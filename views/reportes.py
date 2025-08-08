import streamlit as st
import pandas as pd
import io
import requests
import matplotlib.pyplot as plt
from core.db import get_connection
from streamlit_lottie import st_lottie

# 🌀 Lottie
def cargar_lottie(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

# 📜 Reportes
def reportes():
    st.set_page_config(page_title="Reportes", page_icon="📊", layout="wide")

    st.markdown("""
        <style>
        .titulo {
            font-size: 2.3rem;
            font-weight: bold;
            color: #003366;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="titulo">📊 Reportes del Sistema de Gestión Futbolística</h1>', unsafe_allow_html=True)

    animacion = cargar_lottie("https://lottie.host/8f1c5566-e4b9-4d08-8ad0-9b7348441bfb/yvOKmBGz1L.json")
    if animacion:
        st_lottie(animacion, height=180)

    try:
        conn = get_connection()
        tab1, tab2 = st.tabs(["🏃 Rendimiento de Jugadores", "📅 Historial de Partidos"])

        # 🎯 TAB 1 - Rendimiento
        with tab1:
            st.subheader("🧑‍💼 Rendimiento por partido")

            query1 = """
                SELECT
                    j.nombre AS jugador,
                    e.nombre_equipo AS equipo,
                    p.fecha AS fecha_partido,
                    est.goles,
                    est.asistencias,
                    est.minutos_jugados
                FROM estadisticas est
                JOIN jugadores j ON est.id_jugador = j.id_jugador
                LEFT JOIN equipos e ON j.id_equipo = e.id_equipo
                JOIN partidos p ON est.id_partido = p.id_partido
                ORDER BY p.fecha DESC;
            """
            df1 = pd.read_sql(query1, conn)

            if not df1.empty:
                # Filtros
                jugador_sel = st.selectbox("🔎 Filtrar por jugador", ["Todos"] + sorted(df1["jugador"].unique().tolist()))
                equipo_sel = st.selectbox("🏳️ Filtrar por equipo", ["Todos"] + sorted(df1["equipo"].dropna().unique().tolist()))

                if jugador_sel != "Todos":
                    df1 = df1[df1["jugador"] == jugador_sel]
                if equipo_sel != "Todos":
                    df1 = df1[df1["equipo"] == equipo_sel]

                # Paginación
                filas_pagina = 10
                pagina = st.number_input("📄 Página", min_value=1, max_value=(len(df1) // filas_pagina + 1), step=1)
                inicio = (pagina - 1) * filas_pagina
                fin = inicio + filas_pagina

                st.dataframe(df1.iloc[inicio:fin], use_container_width=True)

                # Descarga
                excel_buffer = io.BytesIO()
                df1.to_excel(excel_buffer, index=False, engine='openpyxl')
                st.download_button("📥 Descargar rendimiento", data=excel_buffer.getvalue(), file_name="reporte_rendimiento.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

                # 📊 Gráfico
                st.subheader("📊 Goles por jugador")
                top_goleadores = df1.groupby("jugador")["goles"].sum().sort_values(ascending=False).head(10)
                st.bar_chart(top_goleadores)

        # 🎯 TAB 2 - Partidos
        with tab2:
            st.subheader("🏟️ Historial completo de partidos")

            query2 = """
                SELECT
                    p.fecha,
                    el.nombre_equipo AS equipo_local,
                    ev.nombre_equipo AS equipo_visitante,
                    p.marcador_local,
                    p.marcador_visitante
                FROM partidos p
                JOIN equipos el ON p.equipo_local = el.id_equipo
                JOIN equipos ev ON p.equipo_visitante = ev.id_equipo
                ORDER BY p.fecha DESC;
            """
            df2 = pd.read_sql(query2, conn)

            if not df2.empty:
                # Filtro por equipo
                equipos = sorted(set(df2["equipo_local"]).union(df2["equipo_visitante"]))
                filtro_equipo = st.selectbox("🏁 Filtrar por equipo", ["Todos"] + equipos)
                if filtro_equipo != "Todos":
                    df2 = df2[(df2["equipo_local"] == filtro_equipo) | (df2["equipo_visitante"] == filtro_equipo)]

                # Paginación
                filas_pagina = 10
                pagina = st.number_input("📄 Página de partidos", min_value=1, max_value=(len(df2) // filas_pagina + 1), step=1, key="partidos_pagina")
                inicio = (pagina - 1) * filas_pagina
                fin = inicio + filas_pagina

                st.dataframe(df2.iloc[inicio:fin], use_container_width=True)

                # Descarga
                excel_buffer = io.BytesIO()
                df2.to_excel(excel_buffer, index=False, engine='openpyxl')
                st.download_button("📥 Descargar historial", data=excel_buffer.getvalue(), file_name="reporte_historial.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

                # 📊 Gráfico
                st.subheader("📈 Promedio de goles por partido")
                df2["total_goles"] = df2["marcador_local"] + df2["marcador_visitante"]
                fig, ax = plt.subplots()
                df2.groupby("fecha")["total_goles"].mean().plot(ax=ax)
                ax.set_title("Promedio de goles por fecha")
                ax.set_ylabel("Goles")
                st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Error al generar los reportes: {e}")
    finally:
        conn.close()
