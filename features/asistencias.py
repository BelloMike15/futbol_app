import streamlit as st
import psycopg2
import pandas as pd

# 🎯 Conexión
def conectar_bd():
    return psycopg2.connect(
        host="localhost",
        database="futbol_gestion",
        user="postgres",
        password="12345"
    )

# 🔄 Partidos
def obtener_partidos():
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("""
        SELECT id_partido, 
               (SELECT nombre_equipo FROM equipos WHERE id_equipo = equipo_local) || ' vs ' ||
               (SELECT nombre_equipo FROM equipos WHERE id_equipo = equipo_visitante) || ' - ' || fecha
        FROM partidos
        ORDER BY fecha DESC;
    """)
    partidos = cur.fetchall()
    conn.close()
    return partidos

# 💾 Registro
def registrar_asistencia(id_partido, espectadores, capacidad):
    try:
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO asistencias_partido (id_partido, espectadores, capacidad_estadio)
            VALUES (%s, %s, %s)
        """, (id_partido, espectadores, capacidad))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Error al registrar asistencia: {e}")
        return False

# 📋 Mostrar asistencias
def mostrar_asistencias():
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("""
        SELECT ap.id_asistencia,
               p.fecha,
               el.nombre_equipo AS equipo_local,
               ev.nombre_equipo AS equipo_visitante,
               ap.espectadores,
               ap.capacidad_estadio,
               ROUND(ap.porcentaje_ocupacion, 2) AS ocupacion
        FROM asistencias_partido ap
        JOIN partidos p ON ap.id_partido = p.id_partido
        JOIN equipos el ON p.equipo_local = el.id_equipo
        JOIN equipos ev ON p.equipo_visitante = ev.id_equipo
        ORDER BY p.fecha DESC;
    """)
    columnas = [desc[0] for desc in cur.description]
    datos = cur.fetchall()
    conn.close()
    return pd.DataFrame(datos, columns=columnas)

# 🎨 Interfaz elegante con filtros y paginación
def mostrar_pantalla_asistencias():
    st.title("🎟️ Registro y Análisis de Asistencias")

    with st.expander("➕ Registrar nueva asistencia"):
        partidos = obtener_partidos()
        if not partidos:
            st.warning("⚠️ No hay partidos registrados aún.")
        else:
            partidos_desc = [p[1] for p in partidos]
            partido_sel = st.selectbox("📅 Selecciona un partido", partidos_desc)
            id_partido = [p[0] for p in partidos if p[1] == partido_sel][0]

            espectadores = st.number_input("👥 Número de espectadores", min_value=0, step=10)
            capacidad = st.number_input("🏟️ Capacidad del estadio", min_value=1000, step=100)

            if st.button("💾 Registrar asistencia"):
                if espectadores <= capacidad and capacidad > 0:
                    exito = registrar_asistencia(id_partido, espectadores, capacidad)
                    if exito:
                        st.success("✅ Asistencia registrada correctamente.")
                        st.rerun()
                else:
                    st.warning("⚠️ Los espectadores no pueden superar la capacidad del estadio.")

    st.subheader("📊 Asistencias registradas")
    df = mostrar_asistencias()

    if df.empty:
        st.info("ℹ️ No hay asistencias registradas aún.")
        return

    # 🎯 Filtros
    equipos_locales = df["equipo_local"].unique()
    equipo_filtrado = st.selectbox("🔍 Filtrar por equipo local", ["Todos"] + list(equipos_locales))
    if equipo_filtrado != "Todos":
        df = df[df["equipo_local"] == equipo_filtrado]

    # 🔢 Paginación
    filas_por_pagina = 5
    total_paginas = (len(df) - 1) // filas_por_pagina + 1
    pagina = st.number_input("📄 Página", min_value=1, max_value=total_paginas, step=1)

    inicio = (pagina - 1) * filas_por_pagina
    fin = inicio + filas_por_pagina

    # 🔵 Etiqueta visual
    def color_ocupacion(valor):
        if valor >= 90:
            return "✅ Alta"
        elif valor >= 70:
            return "🟡 Media"
        else:
            return "🔴 Baja"

    df["Nivel de Ocupación"] = df["ocupacion"].apply(color_ocupacion)
    df = df.rename(columns={"ocupacion": "Porcentaje de Ocupación (%)"})

    # 📋 Tabla paginada
    st.dataframe(df.iloc[inicio:fin].style.format({
        "Porcentaje de Ocupación (%)": "{:.2f}"
    }), use_container_width=True)

# 🚀 Ejecutar
if __name__ == "__main__":
    mostrar_pantalla_asistencias()
