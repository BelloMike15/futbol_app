import streamlit as st
import pandas as pd
from core.db import get_connection
from psycopg2 import errors

def gestion_usuarios():
    st.title("👥 Gestión de Usuarios del Sistema")

    if st.session_state.get("rol") != "admin":
        st.error("🚫 Acceso restringido: solo disponible para administradores.")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()

        df = pd.read_sql("SELECT id_usuario, nombre_usuario, rol FROM usuarios ORDER BY rol", conn)

        # Filtro de roles
        st.markdown("### 📋 Lista de usuarios registrados")
        filtro = st.selectbox("Filtrar por rol", ["Todos", "admin", "usuario", "invitado"])
        if filtro != "Todos":
            df = df[df["rol"] == filtro]

        st.dataframe(df, use_container_width=True)

        st.markdown("---")

        # Crear usuario
        with st.expander("➕ Crear nuevo usuario"):
            with st.form("crear_usuario"):
                col1, col2 = st.columns(2)
                with col1:
                    nombre = st.text_input("👤 Nombre de usuario")
                with col2:
                    contrasena = st.text_input("🔒 Contraseña", type="password")
                rol = st.selectbox("🎖️ Rol asignado", ["admin", "usuario", "invitado"])

                if st.form_submit_button("📨 Crear usuario"):
                    if not nombre.strip() or not contrasena.strip():
                        st.warning("⚠️ Todos los campos son obligatorios.")
                    else:
                        try:
                            cursor.execute(
                                "INSERT INTO usuarios (nombre_usuario, contrasena, rol) VALUES (%s, %s, %s)",
                                (nombre.strip(), contrasena.strip(), rol)
                            )
                            conn.commit()
                            st.success("✅ Usuario creado correctamente.")
                            st.rerun()
                        except errors.UniqueViolation:
                            st.error("❌ El usuario ya existe.")
                        except Exception as e:
                            st.error(f"❌ Error al crear usuario: {e}")

        # Editar o eliminar usuario existente
        if not df.empty:
            st.markdown("### ✏️ Editar o eliminar usuario existente")
            id_sel = st.selectbox("Selecciona un usuario por ID", df["id_usuario"].tolist())
            usuario = df[df["id_usuario"] == id_sel].iloc[0]

            with st.form("editar_usuario"):
                col1, col2 = st.columns(2)
                with col1:
                    nuevo_rol = st.selectbox("🛡️ Nuevo rol", ["admin", "usuario", "invitado"], index=["admin", "usuario", "invitado"].index(usuario["rol"]))
                with col2:
                    nueva_contra = st.text_input("🔄 Nueva contraseña (opcional)", type="password")

                col_guardar, col_borrar = st.columns(2)
                with col_guardar:
                    if st.form_submit_button("💾 Guardar cambios"):
                        try:
                            if nueva_contra.strip():
                                cursor.execute(
                                    "UPDATE usuarios SET rol=%s, contrasena=%s WHERE id_usuario=%s",
                                    (nuevo_rol, nueva_contra.strip(), id_sel)
                                )
                            else:
                                cursor.execute(
                                    "UPDATE usuarios SET rol=%s WHERE id_usuario=%s",
                                    (nuevo_rol, id_sel)
                                )
                            conn.commit()
                            st.success("✅ Cambios guardados correctamente.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error al actualizar: {e}")
                with col_borrar:
                    if st.form_submit_button("🗑️ Eliminar usuario"):
                        if st.session_state["usuario"] == usuario["nombre_usuario"]:
                            st.warning("⚠️ No puedes eliminar tu propia cuenta.")
                        else:
                            cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_sel,))
                            conn.commit()
                            st.warning(f"🗑️ Usuario '{usuario['nombre_usuario']}' eliminado.")
                            st.rerun()

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos: {e}")
    finally:
        conn.close()
