# futbol_app/main.py
import os
import json
import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie

# 📌 RUTA RAÍZ DEL PROYECTO
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
env_file = ".env" if os.getenv("ENV", "local") == "local" else ".env.prod"
load_dotenv(os.path.join(ROOT, env_file))

# 📌 IMPORTS SEGÚN TU NUEVA ESTRUCTURA
from views.crud_jugadores import crud_jugadores
from views.crud_equipos import crud_equipos
from views.crud_partidos import crud_partidos
from views.crud_estadisticas import crud_estadisticas
from views.reportes import reportes
from views.graficos import graficos
from views.vistas import mostrar_vistas

from auth.auth import login
from auth.register import register
from auth.usuarios_admin import gestion_usuarios

from features.entrenadores import mostrar_pantalla_entrenadores
from features.sanciones import mostrar_pantalla_sanciones
from features.asistencias import mostrar_pantalla_asistencias
from features.bitacora import mostrar_bitacora

from core.paths import css_path, anim_path
from features.utils import registrar_salida  # 📌 Ahora en features/utils.py

# 📌 CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Sistema de Gestión Futbolística", layout="wide", page_icon="⚽")

# 📌 CARGA CSS
css_file = css_path("styles.css")
if css_file.exists():
    st.markdown(f"<style>{css_file.read_text(encoding='utf-8', errors='ignore')}</style>", unsafe_allow_html=True)
else:
    st.warning("No se encontró assets/css/styles.css")

# 📌 FUNCIÓN PARA CARGAR LOTTIE
def load_lottiefile(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

LOTTIE_BIENVENIDA = load_lottiefile(anim_path("lottie_futbol.json"))

# 📌 FUNCIÓN PRINCIPAL
def main():
    # Estado inicial de sesión
    for key in ["logueado", "usuario", "rol", "ir_a_registro", "registro_ok"]:
        st.session_state.setdefault(key, False if key not in ["usuario", "rol"] else "")

    # Si no está logueado
    if not st.session_state["logueado"]:
        if st.session_state["registro_ok"]:
            st.session_state["registro_ok"] = False
            login()
        elif st.session_state["ir_a_registro"]:
            register()
        else:
            login()
        return

    # Bienvenida
    col1, col2 = st.columns([1, 3])
    with col1:
        if LOTTIE_BIENVENIDA:
            st_lottie(LOTTIE_BIENVENIDA, height=180, key="bienvenida")
        else:
            st.info("🟢 Bienvenido/a")

    with col2:
        st.markdown(f"""
        <div style="background-color: #001f3f; padding: 1.2rem; border-radius: 10px; color: white; margin-bottom: 1rem;">
            <h2 style="margin:0;">Bienvenido/a <span style="color: #2ECC40;">{st.session_state["usuario"]}</span></h2>
            <p style="margin:0;">Rol actual: <strong>{st.session_state["rol"].capitalize()}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    # Menú lateral
    with st.sidebar:
        menu = option_menu(
            "Menú principal",
            ["Inicio", "Jugadores", "Equipos", "Partidos", "Estadísticas",
             "Entrenadores", "Sanciones", "Asistencias", "Reportes", "Vistas",
             "Gráficos", "Usuarios", "Bitácora", "Cerrar sesión"],
            icons=["house", "person-lines-fill", "building", "calendar2-event", "bar-chart-line",
                   "person-video2", "exclamation-circle", "ticket-perforated", "clipboard-data", "eye",
                   "graph-up", "people", "journal-text", "box-arrow-right"],
            default_index=0
        )

    # Lógica de navegación
    if menu == "Inicio":
        st.success("Selecciona una opción en el menú lateral para comenzar.")
    elif menu == "Jugadores": crud_jugadores()
    elif menu == "Equipos": crud_equipos()
    elif menu == "Partidos": crud_partidos()
    elif menu == "Estadísticas": crud_estadisticas()
    elif menu == "Entrenadores": mostrar_pantalla_entrenadores()
    elif menu == "Sanciones": mostrar_pantalla_sanciones()
    elif menu == "Asistencias": mostrar_pantalla_asistencias()
    elif menu == "Reportes": reportes()
    elif menu == "Vistas": mostrar_vistas()
    elif menu == "Gráficos": graficos()
    elif menu == "Usuarios":
        if st.session_state["rol"] == "admin":
            gestion_usuarios()
        else:
            st.warning("⚠️ Solo los administradores pueden ver esta sección.")
    elif menu == "Bitácora":
        if st.session_state["rol"] == "admin":
            mostrar_bitacora()
        else:
            st.warning("⚠️ Acceso restringido a administradores.")
    elif menu == "Cerrar sesión":
        usuario = st.session_state.get("usuario", "desconocido")
        registrar_salida(usuario)
        st.session_state.clear()
        st.rerun()

# 📌 EJECUCIÓN
if __name__ == "__main__":
    main()
