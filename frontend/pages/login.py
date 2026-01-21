import streamlit as st
import time
from frontend.utils import login, show_error, show_success

def show_login_page():
    # Estilos custom para el login
    st.markdown("""
        <style>
        .login-container {
            padding: 2rem;
            border-radius: 10px;
            background-color: #ffffff;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        div[data-testid="stForm"] {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .stButton>button {
            background-color: #0d6efd;
            color: white;
            border-radius: 5px;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #0b5ed7;
            border-color: #0a58ca;
        }
        </style>
    """, unsafe_allow_html=True)

    # Centrar contenido con columnas
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo/Título
        st.markdown("<h1 style='text-align: center;'>🏢 Commercial RAG</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #6c757d;'>Sistema de Consultas Empresarial</h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Formulario de login
        with st.form("login_form"):
            st.write("#### 👤 Iniciar Sesión")
            username = st.text_input("Usuario", placeholder="Ingrese su usuario")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingrese su contraseña")
            
            st.write("") # Spacer
            submit = st.form_submit_button("🔐 Iniciar Sesión", use_container_width=True)
            
            if submit:
                if not username or not password:
                    show_error("Por favor complete todos los campos")
                else:
                    with st.spinner("Autenticando..."):
                        # Simular pequeño delay para UX
                        time.sleep(0.5) 
                        success, message = login(username, password)
                        
                        if success:
                            show_success("¡Login exitoso!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            show_error(f"Error: {message}")
        
        # Información adicional
        st.markdown("---")
        st.caption("💡 Contacte al administrador si olvidó su contraseña")
