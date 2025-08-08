import os
import streamlit as st
from streamlit_lottie import st_lottie
import requests
import psycopg2
from core.db import get_connection
from features.utils import registrar_entrada  # ✅ Bitácora

# 📌 Ruta del logo usando la ubicación real
LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "img", "uleam_logo.png")

# Cargar animación Lottie desde URL
def cargar_animacion(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

def login():
    st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

    # 🎨 Fondo y estilo personalizado
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #080101;
        }
        .titulo {
            font-size: 2rem;
            font-weight: bold;
            color: #003366;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 🖼 Logo ULEAM (ruta segura)
    st.image(LOGO_PATH, width=120)

    # 📝 Título
    st.markdown('<h1 class="titulo">🔐 Iniciar Sesión</h1>', unsafe_allow_html=True)
    st.markdown("Bienvenido al sistema de gestión futbolística. Por favor, inicia sesión para continuar.")

    # 🎬 Animación decorativa
    animacion = cargar_animacion("https://lottie.host/f1dcbfd0-b816-4a86-8a64-3eeae51a03cc/XBOkU82A4J.json")
    if animacion:
        st_lottie(animacion, height=180, key="login")

    # 📋 Formulario de login
    with st.form("login_form"):
        col1, col2 = st.columns(2)
        with col1:
            usuario = st.text_input("👤 Usuario", placeholder="Nombre de usuario")
        with col2:
            contrasena = st.text_input("🔒 Contraseña", type="password", placeholder="Tu contraseña")

        iniciar = st.form_submit_button("🔓 Iniciar Sesión")

        if iniciar:
            if not usuario.strip() or not contrasena.strip():
                st.warning("⚠️ Por favor, completa todos los campos.")
            else:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT rol FROM usuarios WHERE nombre_usuario = %s AND contrasena = %s",
                        (usuario, contrasena)
                    )
                    resultado = cursor.fetchone()
                    conn.close()

                    if resultado:
                        st.success(f"✅ Bienvenido, {usuario}")
                        st.session_state["logueado"] = True
                        st.session_state["usuario"] = usuario
                        st.session_state["rol"] = resultado[0]

                        registrar_entrada("usuarios", "LOGIN", f"Usuario {usuario} inició sesión")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
                except Exception as e:
                    st.error(f"❌ Error de conexión: {e}")

    # 🔗 Opción para ir a registro
    st.markdown("---")
    st.markdown("¿No tienes cuenta aún?")
    if st.button("📝 Registrarse ahora"):
        st.session_state["ir_a_registro"] = True
        st.rerun()
