import streamlit as st
import requests
import os
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CONSTANTES
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def get_auth_header() -> Dict[str, str]:
    """Obtiene el header de autorización con el token actual."""
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def api_request(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    files: Optional[Dict] = None,
    require_auth: bool = True
) -> Tuple[bool, Any]:
    """
    Realiza una petición a la API manejando errores y autenticación.
    """
    url = f"{API_URL}{endpoint}"
    headers = {}
    
    if require_auth:
        headers.update(get_auth_header())
        
    try:
        logger.info(f"API Request: {method} {endpoint}")
        response = requests.request(
            method,
            url,
            json=data,
            files=files,
            headers=headers,
            timeout=30
        )
        
        # Intentar parsear JSON
        try:
            response_data = response.json()
        except ValueError:
            response_data = response.text

        if response.status_code in (200, 201, 204):
            return True, response_data
        else:
            error_msg = response_data.get("detail", "Error desconocido") if isinstance(response_data, dict) else str(response_data)
            logger.error(f"API Error {response.status_code}: {error_msg}")
            return False, error_msg

    except requests.exceptions.Timeout:
        logger.error("API Timeout connection")
        return False, "Error de conexión: El servidor tardó demasiado en responder."
    except requests.exceptions.ConnectionError:
        logger.error("API Connection Error")
        return False, "Error de conexión: No se pudo conectar con el servidor."
    except Exception as e:
        logger.error(f"Unexpected API Error: {str(e)}")
        return False, f"Error inesperado: {str(e)}"

def login(username: str, password: str) -> Tuple[bool, str]:
    """Autentica al usuario y guarda la sesión."""
    success, data = api_request(
        "POST", 
        "/auth/login", 
        data={"username": username, "password": password},
        require_auth=False
    )
    
    if success:
        st.session_state["token"] = data["access_token"]
        st.session_state["user"] = data["user"]
        return True, "Login exitoso"
    else:
        return False, data

def logout():
    """Cierra la sesión actual limpiando el estado."""
    if "token" in st.session_state:
        del st.session_state["token"]
    if "user" in st.session_state:
        del st.session_state["user"]
    
    # Limpiar estado adicional si existe
    keys_to_clear = ["messages", "current_conversation_id", "page"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
            
    st.rerun()

def is_authenticated() -> bool:
    """Verifica si el usuario está autenticado."""
    # TODO: Podríamos añadir validación de expiración aquí decoding el JWT
    return "token" in st.session_state and st.session_state["token"] is not None

def is_admin() -> bool:
    """Verifica si el usuario actual es administrador."""
    if not is_authenticated():
        return False
    user = st.session_state.get("user", {})
    return user.get("role") == "admin"

def format_cost(cost_usd: float) -> str:
    """Formatea costo en USD (ej. '$0.0027')."""
    if cost_usd is None: return "$0.0000"
    return f"${cost_usd:.4f}"

def format_tokens(tokens: int) -> str:
    """Formatea cantidad de tokens de forma legible (ej. '1.2K')."""
    if tokens is None: return "0"
    if tokens >= 1000000:
        return f"{tokens/1000000:.1f}M"
    elif tokens >= 1000:
        return f"{tokens/1000:.1f}K"
    return str(tokens)

def format_datetime(dt: datetime) -> str:
    """Formatea fecha/hora de forma amigable (ej. 'Hace 2 horas')."""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return dt
            
    now = datetime.now()
    diff = now - dt # Asumiendo dt es local o naive compatible
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Hace unos segundos"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"Hace {minutes} minuto{'s' if minutes != 1 else ''}"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"Hace {hours} hora{'s' if hours != 1 else ''}"
    elif seconds < 172800:
        return "Ayer"
    else:
        return dt.strftime("%d/%m/%Y %H:%M")

def show_error(message: str):
    """Muestra mensaje de error estilizado."""
    st.error(f"❌ {message}")

def show_success(message: str):
    """Muestra mensaje de éxito estilizado."""
    st.success(f"✅ {message}")

def show_info(message: str):
    """Muestra mensaje de información estilizado."""
    st.info(f"ℹ️ {message}")
