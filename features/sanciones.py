import streamlit as st
import pandas as pd
import psycopg2
import requests
from streamlit_lottie import st_lottie

# 🔌 Conexión
def conectar_bd():
    return psycopg2.connect(
        host="localhost",
        database="futbol_gestion",
        user="postgres",
        password="12345"
    )

# Jugadores
def obtener_jugadores():
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("SELECT id_jugador, nombre FROM jugadores ORDER BY nombre")
    datos = cur.fetchall()
    conn.close()
    return datos

# Partidos
def obtener_partidos():
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("""
        SELECT id_partido, 
            (SELECT nombre_equipo FROM equipos WHERE id_equipo = equipo_local) || ' vs ' ||
            (SELECT nombre_equipo FROM equipos WHERE id_equipo = equipo_visitante) || ' - ' || fecha
        FROM partidos ORDER BY fecha DESC
    """)
    datos = cur.fetchall()
    conn.close()
    return datos

# Registrar sanción
def registrar_sancion(jugador_id, partido_id, tipo, minuto, observacion, usuario):
    try:
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute("""
            CALL registrar_sancion(%s, %s, %s, %s, %s, %s)
        """, (jugador_id, partido_id, tipo, minuto, observacion, usuario))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Error al registrar sanción: {e}")
        return False


# Mostrar sanciones
def mostrar_sanciones():
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            s.id_sancion,
            j.nombre AS jugador,
            eq.nombre_equipo AS equipo,
            p.fecha,
            s.tipo,
            s.minuto,
            s.observacion
        FROM sanciones s
        JOIN jugadores j ON s.id_jugador = j.id_jugador
        LEFT JOIN equipos eq ON j.id_equipo = eq.id_equipo
        JOIN partidos p ON s.id_partido = p.id_partido
        ORDER BY p.fecha DESC, s.tipo;
    """)
    columnas = [desc[0] for desc in cur.description]
    datos = cur.fetchall()
    conn.close()
    return pd.DataFrame(datos, columns=columnas)

# Cargar animación
def cargar_lottie(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

# Interfaz mejorada con paginación y filtros
def mostrar_pantalla_sanciones():
    st.set_page_config(page_title="Sanciones", page_icon="🟥", layout="centered")

    st.markdown("""
        <style>
        .stApp { background-color: #0b0c0f; }
        .titulo { font-size: 2.2rem; font-weight: 700; color: #ff4444; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="titulo">🟥 Registro de Sanciones</h1>', unsafe_allow_html=True)

    animacion = cargar_lottie("https://lottie.host/5aa309cf-d46f-4aa4-a548-6a49ac8bba9e/yFM4lqBCxg.json")
    if animacion:
        st_lottie(animacion, height=180)

    with st.expander("➕ Registrar nueva sanción"):
        jugadores = obtener_jugadores()
        partidos = obtener_partidos()

        jugador_sel = st.selectbox("👤 Jugador sancionado", [j[1] for j in jugadores])
        partido_sel = st.selectbox("🗓️ Partido", [p[1] for p in partidos])

        jugador_id = [j[0] for j in jugadores if j[1] == jugador_sel][0]
        partido_id = [p[0] for p in partidos if p[1] == partido_sel][0]

        tipo = st.selectbox("🚩 Tipo de sanción", ["Amarilla", "Roja", "Suspensión"])
        minuto = st.number_input("⏱️ Minuto", min_value=0, max_value=120, step=1)
        observacion = st.text_area("📝 Observación", max_chars=200)

        usuario_actual = st.text_input("👤 Usuario responsable", value="admin")

        if st.button("✅ Registrar sanción"):
            if tipo and jugador_id and partido_id:
                exito = registrar_sancion(jugador_id, partido_id, tipo, minuto, observacion, usuario_actual)
                if exito:
                    st.success("✅ Sanción registrada correctamente.")
                    st.rerun()
            else:
                st.warning("⚠️ Por favor, completa todos los campos obligatorios.")

    st.markdown("---")
    st.subheader("📋 Lista de sanciones registradas")

    df = mostrar_sanciones()

    if df.empty:
        st.info("ℹ️ No hay sanciones registradas.")
        return

    # Filtros
    col1, col2 = st.columns(2)
    jugadores = df["jugador"].unique()
    tipos = df["tipo"].unique()

    jugador_filtro = col1.selectbox("🔍 Filtrar por jugador", ["Todos"] + sorted(jugadores.tolist()))
    tipo_filtro = col2.selectbox("🚩 Filtrar por tipo", ["Todos"] + sorted(tipos.tolist()))

    if jugador_filtro != "Todos":
        df = df[df["jugador"] == jugador_filtro]

    if tipo_filtro != "Todos":
        df = df[df["tipo"] == tipo_filtro]

    # Paginación
    registros_por_pagina = 10
    total_paginas = (len(df) - 1) // registros_por_pagina + 1
    pagina_actual = st.number_input("📄 Página", min_value=1, max_value=total_paginas, step=1)

    inicio = (pagina_actual - 1) * registros_por_pagina
    fin = inicio + registros_por_pagina
    st.dataframe(df.iloc[inicio:fin], use_container_width=True)

# ▶️ Ejecutar
if __name__ == "__main__":
    mostrar_pantalla_sanciones()
