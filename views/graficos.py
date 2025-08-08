import streamlit as st
import pandas as pd
import plotly.express as px
from core.db import get_connection
from streamlit_lottie import st_lottie
import requests

# 🔄 Cargar animación Lottie desde URL
def cargar_animacion(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

def graficos():
    st.set_page_config(page_title="Gráficos", page_icon="📊", layout="wide")
    st.title("📊 Visualización de Rendimiento del Torneo")

    # 🌟 Mostrar animación decorativa
    animacion = cargar_animacion("https://lottie.host/f6339a7d-3e55-4fd0-80db-1b5012fc0f44/vq13lQ86V5.json")
    if animacion:
        st_lottie(animacion, height=200, key="grafico_animado")

    st.markdown("---")

    try:
        conn = get_connection()

        # 🥇 Top 5 goleadores
        st.subheader("🥇 Top 5 Goleadores del Torneo")
        query1 = """
            SELECT j.nombre AS jugador, SUM(e.goles) AS total_goles
            FROM estadisticas e
            JOIN jugadores j ON e.id_jugador = j.id_jugador
            GROUP BY j.nombre
            ORDER BY total_goles DESC
            LIMIT 5;
        """
        df1 = pd.read_sql(query1, conn)

        if not df1.empty:
            fig1 = px.bar(
                df1,
                x="jugador",
                y="total_goles",
                color="jugador",
                text_auto=True,
                labels={"jugador": "Jugador", "total_goles": "Goles"},
            )
            fig1.update_layout(
                plot_bgcolor='white',
                margin=dict(l=20, r=20, t=30, b=20),
                showlegend=False
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("⚠️ No hay datos de goles registrados.")

        st.markdown("---")

        # ⚽ Goles por equipo
        st.subheader("⚽ Distribución de Goles por Equipo")
        query2 = """
            SELECT eq.nombre_equipo, SUM(e.goles) AS goles_equipo
            FROM estadisticas e
            JOIN jugadores j ON e.id_jugador = j.id_jugador
            JOIN equipos eq ON j.id_equipo = eq.id_equipo
            GROUP BY eq.nombre_equipo
            ORDER BY goles_equipo DESC;
        """
        df2 = pd.read_sql(query2, conn)

        if not df2.empty:
            fig2 = px.pie(
                df2,
                names="nombre_equipo",
                values="goles_equipo",
                hole=0.4,
            )
            fig2.update_traces(textinfo='label+percent')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("⚠️ No hay datos suficientes para mostrar goles por equipo.")

    except Exception as e:
        st.error(f"❌ Error al generar gráficos: {e}")
    finally:
        conn.close()
