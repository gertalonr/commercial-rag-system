import streamlit as st
import time
from frontend.utils import (
    api_request, 
    format_cost, 
    format_tokens, 
    format_datetime, 
    show_error
)

def chat_page():
    st.title("💬 Chat - Consultas Empresariales")
    
    # Inicializar estado si no existe
    if "current_conversation_id" not in st.session_state:
        st.session_state["current_conversation_id"] = None
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    
    # Header con selector de conversación
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Obtener conversaciones del usuario
        success, conversations = api_request("GET", "/conversations")
        
        if success and isinstance(conversations, list):
            # Dropdown de conversaciones
            conv_options = {
                conv["id"]: f"{conv['title']}"  # Simplificado para evitar errores si backend no manda created_at compatible
                for conv in conversations
            }
            # Add formatted date if available
            for conv in conversations:
                if "created_at" in conv:
                     conv_options[conv["id"]] = f"{conv['title']} - {format_datetime(conv['created_at'])}"

            # Opción para nueva
            options_ids = ["new"] + list(conv_options.keys())
            
            # Determinar índice seleccionado actual
            idx = 0
            if st.session_state["current_conversation_id"] in conv_options:
                idx = options_ids.index(st.session_state["current_conversation_id"])
            
            selected = st.selectbox(
                "Seleccione conversación",
                options=options_ids,
                format_func=lambda x: "➕ Nueva Conversación" if x == "new" else conv_options.get(x, "Desconocida"),
                key="conversation_selector",
                index=idx
            )
            
            # Lógica de cambio de selección
            if selected != "new":
                if selected != st.session_state["current_conversation_id"]:
                     load_conversation(selected)
            elif st.session_state["current_conversation_id"] is not None:
                # Si se seleccionó "new" y teníamos una cargada, resetear
                create_new_conversation()
                
        else:
            st.info("No tienes conversaciones. ¡Haz tu primera pregunta!")
    
    with col2:
        st.write("") # Spacer
        st.write("") 
        if st.button("➕ Nueva", use_container_width=True):
            create_new_conversation()
    
    st.markdown("---")
    
    # Área de mensajes (chat history)
    # Usamos st.container para agrupar, aunque st.chat_message ya renderiza en flujo
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state["messages"] and not st.session_state["current_conversation_id"]:
             st.markdown("""
             ### 👋 ¡Bienvenido!
             Estoy listo para responder tus consultas sobre la documentación de la empresa.
             """)

        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
                # Mostrar metadata si es mensaje de assistant
                if msg["role"] == "assistant" and "metadata" in msg:
                    meta = msg["metadata"]
                    
                    # Fuentes
                    if meta.get("sources"):
                        with st.expander("📚 Fuentes utilizadas"):
                             for s in meta["sources"]:
                                 st.markdown(f"- {s}")
                    
                    # Estadísticas
                    cost = format_cost(meta.get("cost_usd", 0))
                    tokens_in = format_tokens(meta.get("tokens_input", 0))
                    tokens_out = format_tokens(meta.get("tokens_output", 0))
                    st.caption(f"💰 {cost} | 📊 {tokens_in} in / {tokens_out} out")
    
    # Input de nueva pregunta
    user_input = st.chat_input("Escribe tu pregunta aquí...")
    
    if user_input:
        # 1. Añadir mensaje del usuario al chat localmente
        st.session_state["messages"].append({
            "role": "user",
            "content": user_input
        })
        
        # Mostrar mensaje del usuario inmediatamente (para feedback instantáneo)
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # 2. Llamar a la API
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                payload = {"question": user_input}
                if st.session_state["current_conversation_id"]:
                    payload["conversation_id"] = st.session_state["current_conversation_id"]
                
                success, response = api_request("POST", "/query", data=payload)
                
                if success:
                    # Actualizar conversation_id si era nueva
                    if not st.session_state["current_conversation_id"]:
                        st.session_state["current_conversation_id"] = response["conversation_id"]
                        # Hack para refrescar el selectbox en el próximo rerun sin perder foco si es posible (Streamlit limita esto)
                    
                    # Mostrar respuesta
                    st.markdown(response["answer"])
                    
                    # Mostrar metadata
                    sources = response.get("sources", [])
                    if sources:
                        with st.expander("📚 Fuentes utilizadas"):
                             for s in sources:
                                 st.markdown(f"- {s}")
                    
                    cost = format_cost(response.get("cost_usd", 0))
                    tokens_in = format_tokens(response.get("tokens_input", 0))
                    tokens_out = format_tokens(response.get("tokens_output", 0))
                    st.caption(f"💰 {cost} | 📊 {tokens_in} in / {tokens_out} out")
                    
                    # Añadir respuesta al historial state
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": response["answer"],
                        "metadata": {
                            "sources": sources,
                            "cost_usd": response.get("cost_usd", 0),
                            "tokens_input": response.get("tokens_input", 0),
                            "tokens_output": response.get("tokens_output", 0)
                        }
                    })
                else:
                    st.error(f"Error al procesar consulta: {response}")

def load_conversation(conversation_id: str):
    """Cargar mensajes de una conversación existente"""
    success, conv = api_request("GET", f"/conversations/{conversation_id}")
    
    if success:
        st.session_state["current_conversation_id"] = conversation_id
        st.session_state["messages"] = [
            {
                "role": msg["role"],
                "content": msg["content"],
                "metadata": {
                    "sources": [], # El endpoint de detalle de conv no siempre devuelve sources por mensaje, depende del backend. Asumimos vacío o update backend.
                    "cost_usd": msg.get("cost_usd", 0),
                    "tokens_input": msg.get("tokens_input", 0),
                    "tokens_output": msg.get("tokens_output", 0)
                }
            }
            for msg in conv.get("messages", [])
        ]
        st.rerun()

def create_new_conversation():
    """Crear nueva conversación"""
    st.session_state["current_conversation_id"] = None
    st.session_state["messages"] = []
    st.rerun()
