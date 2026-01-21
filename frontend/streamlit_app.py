import streamlit as st
from frontend.utils import is_authenticated, is_admin
from frontend.pages import login, chat, admin_dashboard, admin_users, admin_documents # Added admin_documents
from frontend.components.sidebar import render_sidebar

# Configuración de la página
st.set_page_config(
    page_title="Commercial RAG System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    /* Estilos globales */
    .main {
        padding: 2rem;
    }
    
    /* Estilo para métricas */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    
    /* Botones */
    .stButton button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Verificar autenticación
    if not is_authenticated():
        # Using show_login_page() instead of login.show_login_page() because login module was imported
        login.show_login_page()
        return
    
    # Renderizar sidebar y obtener página seleccionada
    selected_page = render_sidebar()
    
    # Enrutamiento de páginas
    if "Chat" in selected_page or "💬" in selected_page:
        # Using chat_page() as defined in chat.py
        chat.chat_page()
    
    elif "Dashboard" in selected_page or "📊" in selected_page:
        if is_admin():
            admin_dashboard.show_admin_dashboard()
        else:
            st.error("Acceso no autorizado")
    
    elif "Usuarios" in selected_page or "👥" in selected_page:
        if is_admin():
            admin_users.show_admin_users()
        else:
            st.error("Acceso no autorizado")
    
    elif "Documentos" in selected_page or "📁" in selected_page:
        if is_admin():
            # Integrated admin_documents page
            admin_documents.show_admin_documents()
        else:
            st.error("Acceso no autorizado")
    
    elif "Estadísticas" in selected_page or "📈" in selected_page:
        if is_admin():
            # TODO: Implementar página de estadísticas detalladas
            st.info("Página de estadísticas - Próximamente")
        else:
            st.error("Acceso no autorizado")
    
    elif "Conversaciones" in selected_page or "📋" in selected_page:
        # TODO: Página de historial de conversaciones
        st.info("Página de conversaciones - Próximamente")
    
    elif "Configuración" in selected_page or "⚙️" in selected_page:
        # TODO: Página de configuración de usuario
        st.info("Página de configuración - Próximamente")

if __name__ == "__main__":
    main()
