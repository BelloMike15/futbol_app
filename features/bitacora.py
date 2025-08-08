import streamlit as st
import pandas as pd
from core.db import get_connection

def mostrar_bitacora():
    st.title("📜 Registro de Bitácora del Sistema")
    st.markdown("Visualiza todas las acciones realizadas en el sistema, con filtros detallados.")

    try:
        conn = get_connection()
        query = "SELECT * FROM bitacora ORDER BY hora_ingreso DESC"
        df = pd.read_sql(query, conn)

        if df.empty:
            st.info("ℹ️ No hay registros en la bitácora.")
            return

        # 🧪 Filtros personalizados
        with st.expander("🔎 Filtrar registros"):
            col1, col2, col3 = st.columns(3)

            usuarios = df["usuario"].dropna().unique().tolist()
            tablas = df["tabla_afectada"].dropna().unique().tolist()
            acciones = df["tipo_accion"].dropna().unique().tolist()

            with col1:
                usuario_sel = st.selectbox("👤 Usuario", ["Todos"] + usuarios)

            with col2:
                tabla_sel = st.selectbox("📂 Tabla afectada", ["Todas"] + tablas)

            with col3:
                accion_sel = st.selectbox("⚙️ Tipo de acción", ["Todas"] + acciones)

            col4, col5 = st.columns(2)
            with col4:
                fecha_ini = st.date_input("📅 Desde", value=df["hora_ingreso"].min().date())
            with col5:
                fecha_fin = st.date_input("📅 Hasta", value=df["hora_ingreso"].max().date())

        # 🔁 Aplicar filtros
        df_filtrado = df.copy()

        if usuario_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["usuario"] == usuario_sel]
        if tabla_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado["tabla_afectada"] == tabla_sel]
        if accion_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado["tipo_accion"] == accion_sel]

        df_filtrado["fecha"] = pd.to_datetime(df_filtrado["hora_ingreso"]).dt.date
        df_filtrado = df_filtrado[(df_filtrado["fecha"] >= fecha_ini) & (df_filtrado["fecha"] <= fecha_fin)]

        # 📥 Botón de exportar
        col_export, _ = st.columns(2)
        with col_export:
            st.download_button(
                label="⬇️ Exportar a CSV",
                data=df_filtrado.to_csv(index=False).encode('utf-8'),
                file_name='bitacora_filtrada.csv',
                mime='text/csv'
            )

        # 🧾 Mostrar bitácora filtrada
        st.markdown(f"### 📋 Resultados encontrados: {len(df_filtrado)} registros")
        st.dataframe(df_filtrado.drop(columns=["fecha"]), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al cargar la bitácora: {e}")
    finally:
        conn.close()
