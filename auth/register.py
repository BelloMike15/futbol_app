import streamlit as st
from streamlit_lottie import st_lottie
import requests
import psycopg2
from psycopg2 import errors
from core.db import get_connection

# Función para cargar animaciones desde URL
def cargar_animacion(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

def register():
    st.set_page_config(page_title="Registro", page_icon="📝", layout="centered")

    # Fondo sutil con color
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #080101;
        }
        .title {
            font-size: 2rem;
            font-weight: bold;
            color: #003366;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Logo de la ULEAM
    st.image("uleam_logo.png", width=120)

    # Título estilizado
    st.markdown('<h1 class="title">📝 Registro de nuevo usuario</h1>', unsafe_allow_html=True)
    st.markdown("Por favor, completa los campos para crear una cuenta nueva.")

    # Animación decorativa
    animacion = cargar_animacion("https://lottie.host/2d0b3d94-7d14-4f8b-bf07-0a82cc8029d2/VnOeKzMTyM.json")
    if animacion:
        st_lottie(animacion, height=180, key="registro")

    # Formulario de registro
    with st.form("registro_usuario"):
        col1, col2 = st.columns(2)
        with col1:
            nombre_usuario = st.text_input("👤 Nombre de usuario")
        with col2:
            contrasena = st.text_input("🔒 Contraseña", type="password")

        confirmar = st.text_input("🔁 Confirmar contraseña", type="password")
        enviar = st.form_submit_button("📨 Registrarse")

        if enviar:
            # Validaciones
            if not nombre_usuario.strip() or not contrasena.strip() or not confirmar.strip():
                st.warning("⚠️ Todos los campos son obligatorios.")
            elif contrasena != confirmar:
                st.warning("⚠️ Las contraseñas no coinciden.")
            else:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO usuarios (nombre_usuario, contrasena, rol)
                        VALUES (%s, %s, %s)
                    """, (nombre_usuario.strip(), contrasena.strip(), "invitado"))
                    conn.commit()
                    conn.close()

                    st.success("✅ Registro exitoso. Redirigiendo al inicio de sesión...")
                    st.session_state["registro_ok"] = True
                    st.session_state["ir_a_registro"] = False
                    st.rerun()

                except errors.UniqueViolation:
                    st.error("❌ El nombre de usuario ya está registrado. Intente con otro.")
                except Exception as e:
                    st.error(f"❌ Error inesperado: {e}")
