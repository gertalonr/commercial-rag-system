import streamlit as st
import time
from frontend.utils import api_request, show_error, show_success

def show_admin_users():
    st.title("👥 Gestión de Usuarios")
    
    # Botón crear nuevo usuario
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("➕ Nuevo Usuario", use_container_width=True):
            show_create_user_dialog()
    
    st.markdown("---")
    
    # Obtener lista de usuarios
    success, users = api_request("GET", "/admin/users")
    
    if success and users:
        # Header Tabla
        h1, h2, h3, h4, h5 = st.columns([2, 3, 1, 1, 2])
        h1.markdown("**Usuario**")
        h2.markdown("**Email**")
        h3.markdown("**Rol**")
        h4.markdown("**Activo**")
        h5.markdown("**Acciones**")
        st.divider()

        # Rows
        for user in users:
            col1, col2, col3, col4, col5 = st.columns([2, 3, 1, 1, 2])
            
            with col1:
                st.text(user["username"])
            
            with col2:
                st.text(user["email"])
            
            with col3:
                badge_color = "🔴" if user["role"] == "admin" else "🟢"
                st.markdown(f"{badge_color} `{user['role']}`")
            
            with col4:
                status = "✅" if user["is_active"] else "❌"
                st.text(status)
            
            with col5:
                # Botones de acción
                # Importante: usar keys únicas
                c_edit, c_del = st.columns(2)
                with c_edit:
                    if st.button("⚙️", key=f"edit_{user['id']}", help="Editar Usuario"):
                        show_edit_user_dialog(user)
                
                with c_del:
                    # No permitir eliminar al propio admin
                    current_user = st.session_state.get("user", {})
                    if str(user["id"]) != str(current_user.get("id")):
                        if st.button("🗑️", key=f"delete_{user['id']}", help="Eliminar Usuario"):
                             show_delete_confirmation_dialog(user)
                    else:
                        st.write("Current")
            
            st.markdown("---")
    else:
        st.info("No se pudieron cargar los usuarios o no existen.")

@st.dialog("Crear Nuevo Usuario")
def show_create_user_dialog():
    with st.form("create_user_form"):
        username = st.text_input("Usuario")
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")
        role = st.selectbox("Rol", ["user", "admin"])
        
        submit = st.form_submit_button("Crear Usuario")
        
        if submit:
            if not username or not email or not password:
                st.error("Todos los campos son obligatorios")
            else:
                success, response = api_request(
                    "POST",
                    "/admin/users/create",
                    data={
                        "username": username,
                        "email": email,
                        "password": password,
                        "role": role
                    }
                )
                
                if success:
                    st.success(f"Usuario {username} creado exitosamente")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Error: {response}")

@st.dialog("Editar Usuario")
def show_edit_user_dialog(user: dict):
    st.subheader(f"Editando: {user['username']}")
    
    # Cambiar contraseña
    with st.form("change_password_form"):
        st.markdown("#### Cambiar Contraseña")
        new_password = st.text_input("Nueva Contraseña", type="password")
        submit_pwd = st.form_submit_button("Actualizar Contraseña")
        
        if submit_pwd:
             if new_password and len(new_password) >= 8:
                success, response = api_request(
                    "PUT",
                    f"/admin/users/{user['id']}/password",
                    data={"new_password": new_password}
                )
                
                if success:
                    st.success("Contraseña actualizada")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Error: {response}")
             else:
                 st.error("La contraseña debe tener mín. 8 caracteres")
    
    st.divider()
    
    # Toggle activo/inactivo
    status_text = "Activo" if user["is_active"] else "Inactivo"
    action_text = "Desactivar" if user["is_active"] else "Activar"
    btn_type = "primary" if not user["is_active"] else "secondary"
    
    st.markdown(f"**Estado actual:** {status_text}")
    
    if st.button(f"{action_text} Usuario", type=btn_type, use_container_width=True):
        success, response = api_request(
            "PUT",
            f"/admin/users/{user['id']}/toggle-active"
        )
        
        if success:
            st.success(f"Usuario {action_text.lower()}do")
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"Error: {response}")

@st.dialog("Confirmar Eliminación")
def show_delete_confirmation_dialog(user: dict):
    st.warning(f"¿Estás seguro que deseas eliminar permanentemente a **{user['username']}**?")
    st.caption("Esta acción eliminará también sus estadísticas y logs.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
            
    with col2:
        if st.button("Sí, Eliminar", type="primary", use_container_width=True):
            success, response = api_request(
                "DELETE",
                f"/admin/users/{user['id']}"
            )
            
            if success:
                st.success("Usuario eliminado")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"Error: {response}")

# Alias
admin_users_page = show_admin_users
