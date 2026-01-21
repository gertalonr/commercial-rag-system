"""
Test Suite Completo para Commercial RAG System
Ejecutar con: pytest tests/test_complete_system.py -v
"""

import pytest
import requests
import time
from typing import Dict, Any
import os

# Configuración
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")

# Credenciales de prueba
ADMIN_CREDS = {
    "username": "admin",
    "password": os.getenv("ADMIN_PASSWORD", "changeme")
}

TEST_USER_CREDS = {
    "username": "test_user_automated",
    "email": "test@automated.com",
    "password": "TestPassword123!"
}

class TestSystemHealth:
    """Tests de verificación de servicios"""
    
    def test_backend_health(self):
        """Verificar que backend responde"""
        response = requests.get(f"{API_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_frontend_accessible(self):
        """Verificar que frontend es accesible"""
        response = requests.get(FRONTEND_URL)
        assert response.status_code == 200
    
    def test_api_docs_accessible(self):
        """Verificar que documentación API está disponible"""
        response = requests.get(f"{API_URL}/docs")
        assert response.status_code == 200


class TestAuthentication:
    """Tests de autenticación"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada test"""
        self.admin_token = None
        self.user_token = None
    
    def test_admin_login(self):
        """Test login de admin"""
        response = requests.post(
            f"{API_URL}/auth/login",
            json=ADMIN_CREDS
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "admin"
        self.admin_token = data["access_token"]
    
    def test_login_invalid_credentials(self):
        """Test login con credenciales inválidas"""
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": "invalid", "password": "wrong"}
        )
        assert response.status_code == 401
    
    def test_register_new_user(self):
        """Test registro de nuevo usuario"""
        response = requests.post(
            f"{API_URL}/auth/register",
            json=TEST_USER_CREDS
        )
        # Puede ser 201 si es nuevo, o 400 si ya existe (de runs previos)
        assert response.status_code in [201, 400]
    
    def test_get_current_user(self):
        """Test obtener usuario actual con token"""
        # Login primero
        login_response = requests.post(
            f"{API_URL}/auth/login",
            json=ADMIN_CREDS
        )
        token = login_response.json()["access_token"]
        
        # Obtener usuario actual
        response = requests.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == ADMIN_CREDS["username"]
    
    def test_unauthorized_access(self):
        """Test acceso sin token"""
        response = requests.get(f"{API_URL}/auth/me")
        assert response.status_code == 401


class TestRAGSystem:
    """Tests del sistema RAG"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Obtener token para tests"""
        login_response = requests.post(
            f"{API_URL}/auth/login",
            json=ADMIN_CREDS
        )
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_create_conversation(self):
        """Test crear nueva conversación"""
        response = requests.post(
            f"{API_URL}/conversations/create",
            json={"title": "Test Conversation Automated"},
            headers=self.headers
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Conversation Automated"
    
    def test_list_conversations(self):
        """Test listar conversaciones"""
        response = requests.get(
            f"{API_URL}/conversations",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_rag_query(self):
        """Test hacer query al RAG"""
        response = requests.post(
            f"{API_URL}/query",
            json={
                "question": "¿Cuál es el precio del producto A?",
                "conversation_id": None
            },
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "tokens_input" in data
        assert "tokens_output" in data
        assert "cost_usd" in data
        assert data["tokens_input"] > 0
        assert data["tokens_output"] > 0
        assert data["cost_usd"] > 0
    
    def test_rag_query_with_conversation(self):
        """Test query con conversación existente"""
        # Crear conversación
        conv_response = requests.post(
            f"{API_URL}/conversations/create",
            json={"title": "Test RAG Query"},
            headers=self.headers
        )
        conv_id = conv_response.json()["id"]
        
        # Primera query
        response1 = requests.post(
            f"{API_URL}/query",
            json={
                "question": "¿Qué productos tienes?",
                "conversation_id": conv_id
            },
            headers=self.headers
        )
        assert response1.status_code == 200
        
        # Segunda query en misma conversación
        response2 = requests.post(
            f"{API_URL}/query",
            json={
                "question": "¿Cuál es el más caro?",
                "conversation_id": conv_id
            },
            headers=self.headers
        )
        assert response2.status_code == 200
        
        # Verificar que se guardaron los mensajes
        conv_response = requests.get(
            f"{API_URL}/conversations/{conv_id}",
            headers=self.headers
        )
        assert conv_response.status_code == 200
        messages = conv_response.json()["messages"]
        assert len(messages) >= 4  # 2 user + 2 assistant


class TestAdminFunctions:
    """Tests de funciones de administrador"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Obtener token admin"""
        login_response = requests.post(
            f"{API_URL}/auth/login",
            json=ADMIN_CREDS
        )
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_list_all_users(self):
        """Test listar todos los usuarios (admin)"""
        response = requests.get(
            f"{API_URL}/admin/users",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Al menos admin debe existir
    
    def test_create_user_as_admin(self):
        """Test crear usuario como admin"""
        response = requests.post(
            f"{API_URL}/admin/users/create",
            json={
                "username": f"test_user_{int(time.time())}",
                "email": f"test_{int(time.time())}@test.com",
                "password": "TestPass123!",
                "role": "user"
            },
            headers=self.headers
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
    
    def test_get_user_usage_stats(self):
        """Test obtener estadísticas de usuario"""
        # Obtener primer usuario
        users_response = requests.get(
            f"{API_URL}/admin/users",
            headers=self.headers
        )
        user_id = users_response.json()[0]["id"]
        
        response = requests.get(
            f"{API_URL}/admin/usage/user/{user_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
    
    def test_get_global_usage_stats(self):
        """Test estadísticas globales"""
        response = requests.get(
            f"{API_URL}/admin/usage/global",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_realtime_usage(self):
        """Test estadísticas en tiempo real"""
        response = requests.get(
            f"{API_URL}/admin/usage/realtime?hours=24",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_queries" in data
        assert "total_cost_usd" in data
        assert "active_users" in data
    
    def test_list_documents(self):
        """Test listar documentos"""
        response = requests.get(
            f"{API_URL}/admin/documents",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_non_admin_cannot_access_admin_endpoints(self):
        """Test que usuario normal no puede acceder a endpoints admin"""
        # Login como usuario normal
        user_login = requests.post(
            f"{API_URL}/auth/login",
            json=TEST_USER_CREDS
        )
        
        if user_login.status_code == 200:
            user_token = user_login.json()["access_token"]
            user_headers = {"Authorization": f"Bearer {user_token}"}
            
            # Intentar acceder a endpoint admin
            response = requests.get(
                f"{API_URL}/admin/users",
                headers=user_headers
            )
            assert response.status_code == 403  # Forbidden


class TestUsageTracking:
    """Tests de tracking de uso"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Obtener token"""
        login_response = requests.post(
            f"{API_URL}/auth/login",
            json=ADMIN_CREDS
        )
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_query_tracks_tokens_and_cost(self):
        """Test que las queries registran tokens y coste"""
        response = requests.post(
            f"{API_URL}/query",
            json={
                "question": "Test query para verificar tracking",
                "conversation_id": None
            },
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que se registraron tokens
        assert data["tokens_input"] > 0
        assert data["tokens_output"] > 0
        
        # Verificar que se calculó el coste
        assert data["cost_usd"] > 0
        
        # Verificar que el coste es razonable (no negativo, no excesivo)
        assert 0 < data["cost_usd"] < 1.0  # Debería ser centavos


class TestErrorHandling:
    """Tests de manejo de errores"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Obtener token"""
        login_response = requests.post(
            f"{API_URL}/auth/login",
            json=ADMIN_CREDS
        )
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_invalid_conversation_id(self):
        """Test con ID de conversación inválido"""
        response = requests.get(
            f"{API_URL}/conversations/00000000-0000-0000-0000-000000000000",
            headers=self.headers
        )
        assert response.status_code == 404
    
    def test_empty_query(self):
        """Test query vacía"""
        response = requests.post(
            f"{API_URL}/query",
            json={
                "question": "",
                "conversation_id": None
            },
            headers=self.headers
        )
        # Debería rechazar queries vacías
        assert response.status_code in [400, 422]
    
    def test_malformed_request(self):
        """Test request mal formado"""
        response = requests.post(
            f"{API_URL}/query",
            json={"invalid": "data"},
            headers=self.headers
        )
        assert response.status_code == 422  # Validation error


def run_all_tests():
    """Ejecutar todos los tests y generar reporte"""
    print("🧪 Ejecutando suite completa de tests...")
    print("=" * 60)
    
    # Ejecutar pytest con opciones
    exit_code = pytest.main([
        __file__,
        "-v",  # Verbose
        "--tb=short",  # Traceback corto
        "--color=yes",  # Colores
        "-W", "ignore::DeprecationWarning",  # Ignorar warnings
        "--html=tests/report.html",  # Generar reporte HTML
        "--self-contained-html"  # HTML auto-contenido
    ])
    
    if exit_code == 0:
        print("\n✅ Todos los tests pasaron exitosamente")
    else:
        print(f"\n❌ Algunos tests fallaron (código: {exit_code})")
    
    return exit_code


if __name__ == "__main__":
    run_all_tests()
