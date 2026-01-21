import streamlit as st
from frontend.utils import logout, is_admin

def render_sidebar() -> str:
    """
    Renderiza el sidebar y retorna la página seleccionada.
    """
    with st.sidebar:
        # Header con info de usuario
        user = st.session_state.get("user", {})
        username = user.get("username", "Usuario")
        email = user.get("email", "")
        
        st.markdown(f"### 👤 {username}")
        if email:
            st.caption(email)
        st.markdown("---")
        
        # Navegación según rol
        if is_admin():
            # Menú admin
            page = st.radio(
                "Navegación",
                [
                    "💬 Chat",
                    "📊 Dashboard",
                    "👥 Usuarios",
                    "📁 Documentos",
                    "📈 Estadísticas",
                    "⚙️ Configuración"  # Placeholder
                ],
                label_visibility="collapsed"
            )
        else:
            # Menú usuario normal
            page = st.radio(
                "Navegación",
                [
                    "💬 Chat",
                    "📋 Mis Conversaciones", # Placeholder
                    "⚙️ Configuración"      # Placeholder
                ],
                label_visibility="collapsed"
            )
        
        st.markdown("---")
        
        # Botón de cerrar sesión
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
        
        # Footer con info
        st.markdown("---")
        st.caption("v1.0.0 | Commercial RAG")
        
        return page
