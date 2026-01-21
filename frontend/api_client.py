import requests
import streamlit as st
from typing import Optional, Dict, Any, List
from frontend.config import API_URL

class APIClient:
    """Clase para manejar las peticiones a la API."""
    
    def __init__(self):
        self.base_url = API_URL
        
    def _get_headers(self) -> Dict[str, str]:
        """Obtiene headers con token si existe en session state."""
        headers = {}
        if "token" in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state['token']}"
        return headers

    def login(self, username, password) -> bool:
        """Realiza login y guarda token en session state."""
        try:
            res = requests.post(f"{self.base_url}/auth/login", json={
                "username": username,
                "password": password
            })
            if res.status_code == 200:
                data = res.json()
                st.session_state["token"] = data["access_token"]
                st.session_state["user"] = data["user"]
                return True
            return False
        except Exception as e:
            st.error(f"Error de conexión: {e}")
            return False

    def get_conversations(self) -> List[Dict]:
        """Obtiene lista de conversaciones."""
        res = requests.get(f"{self.base_url}/conversations", headers=self._get_headers())
        if res.status_code == 200:
            return res.json()
        return []

    def create_conversation(self, title: str) -> Optional[Dict]:
        """Crea nueva conversación."""
        res = requests.post(
            f"{self.base_url}/conversations/create",
            json={"title": title},
            headers=self._get_headers()
        )
        if res.status_code == 201:
            return res.json()
        return None

    def get_conversation(self, conv_id: str) -> Optional[Dict]:
        """Obtiene detalle de conversación."""
        res = requests.get(
            f"{self.base_url}/conversations/{conv_id}", 
            headers=self._get_headers()
        )
        if res.status_code == 200:
            return res.json()
        return None

    def send_query(self, question: str, conversation_id: Optional[str] = None) -> Optional[Dict]:
        """Envía pregunta al RAG."""
        payload = {"question": question}
        if conversation_id:
            payload["conversation_id"] = conversation_id
            
        try:
            res = requests.post(
                f"{self.base_url}/query",
                json=payload,
                headers=self._get_headers()
            )
            if res.status_code == 200:
                return res.json()
            else:
                st.error(f"Error del servidor: {res.text}")
                return None
        except Exception as e:
            st.error(f"Error de conexión: {e}")
            return None

    # --- ADMIN METHODS ---
    
    def admin_get_users(self):
        res = requests.get(f"{self.base_url}/admin/users", headers=self._get_headers())
        return res.json() if res.status_code == 200 else []

    def admin_get_global_stats(self):
        res = requests.get(f"{self.base_url}/admin/usage/global", headers=self._get_headers())
        return res.json() if res.status_code == 200 else []

    def admin_upload_files(self, files):
        # files is a list of UploadedFile from streamlit
        files_payload = [
            ("files", (f.name, f.getvalue(), f.type)) for f in files
        ]
        res = requests.post(f"{self.base_url}/admin/documents/upload", files=files_payload, headers=self._get_headers())
        return res.json() if res.status_code == 201 else None

    def admin_reindex(self):
        res = requests.post(f"{self.base_url}/admin/documents/reindex", headers=self._get_headers())
        return res.json() if res.status_code == 200 else None

    def admin_update_user_password(self, user_id: str, new_password: str) -> bool:
        res = requests.put(
            f"{self.base_url}/admin/users/{user_id}/password",
            json={"new_password": new_password},
            headers=self._get_headers()
        )
        return res.status_code == 200

    def admin_toggle_user_active(self, user_id: str) -> bool:
        res = requests.put(
            f"{self.base_url}/admin/users/{user_id}/toggle-active",
            headers=self._get_headers()
        )
        return res.status_code == 200
