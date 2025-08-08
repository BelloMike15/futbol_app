# 📦 utils.py
# Funciones auxiliares para bitácora, conexión y datos del sistema

import psycopg2
import socket
import streamlit as st
from core.db import get_connection

# 🖥️ Obtener IP y nombre de la máquina local
def obtener_datos_equipo():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        nombre = socket.gethostname()
    except:
        ip = "127.0.0.1"
        nombre = "localhost"
    return ip, nombre

# 📝 Registrar acción en la bitácora
def registrar_entrada(tabla, accion, descripcion, navegador="streamlit"):
    """
    Registra una nueva entrada en la tabla bitácora con la hora actual.
    
    Parámetros:
        tabla (str): Nombre de la tabla afectada.
        accion (str): Tipo de acción realizada (INSERT, UPDATE, DELETE, LOGIN, etc).
        descripcion (str): Descripción de lo ocurrido.
        navegador (str): Origen del acceso. Por defecto es "streamlit".
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        usuario = st.session_state.get("usuario", "desconocido")
        ip, nombre_maquina = obtener_datos_equipo()

        cursor.execute("""
            INSERT INTO bitacora (
                usuario, hora_ingreso, navegador, ip, nombre_maquina,
                tabla_afectada, tipo_accion, descripcion
            ) VALUES (%s, current_timestamp, %s, %s, %s, %s, %s, %s)
        """, (
            usuario, navegador, ip, nombre_maquina, tabla, accion, descripcion
        ))

        conn.commit()
        conn.close()
        print(f"🟢 Entrada registrada en bitácora: {usuario} - {accion} en {tabla}")
    except Exception as e:
        print(f"❌ Error al registrar entrada: {e}")

# 🚪 Registrar salida de sesión en la bitácora
def registrar_salida(usuario):
    """
    Actualiza la hora de salida de la última sesión activa del usuario.
    
    Parámetros:
        usuario (str): Nombre del usuario que cierra sesión.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Buscar la última entrada sin hora_salida
        cursor.execute("""
            SELECT id_bitacora FROM bitacora
            WHERE usuario = %s AND hora_salida IS NULL
            ORDER BY hora_ingreso DESC
            LIMIT 1
        """, (usuario,))
        resultado = cursor.fetchone()

        if resultado:
            id_bitacora = resultado[0]
            cursor.execute("""
                UPDATE bitacora
                SET hora_salida = current_timestamp
                WHERE id_bitacora = %s
            """, (id_bitacora,))
            conn.commit()
            print(f"✅ Hora de salida registrada para {usuario}")
        else:
            print("⚠️ No se encontró sesión activa para cerrar.")
    except Exception as e:
        print(f"❌ Error al registrar hora de salida: {e}")
    finally:
        conn.close()
