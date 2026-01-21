from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import logging
import sys
import os

# Add parent directory to path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_db, init_db, User
from backend.auth import (
    authenticate_user, 
    create_access_token, 
    get_current_user, 
    create_initial_admin, 
    get_password_hash
)
from backend.schemas import (
    UserRegister, 
    UserLogin, 
    Token, 
    UserResponse,
    ConversationCreate,
    ConversationResponse,
    QueryRequest,
    QueryResponse,
    DocumentInfo,
    DocumentUploadResponse,
    ReindexResponse,
    RealtimeUsageResponse,
    ConversationTitleUpdate,
    PasswordUpdate
)
from backend.config import settings

# RAG & Services
from backend.rag_engine import ClaudeRAG
from backend.conversation_service import (
    create_conversation,
    get_user_conversations,
    get_conversation,
    add_message,
    delete_conversation,
    get_conversation_history,
    update_conversation_title
)
from backend.usage_tracker import track_query

# Inicializar RAG engine
# Nota: Esto se ejecuta al importar el módulo. Para evitar IO blocker en startup, 
# ClaudeRAG inicializa cliente ligero. La carga pesada (Chroma) es lazy o rápida.
rag_engine = ClaudeRAG()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Commercial RAG System API",
    description="API for RAG-based commercial queries with user management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Inicializar BD
    logger.info("Initializing database...")
    init_db()
    # Crear admin inicial si no existe
    logger.info("Checking initial admin user...")
    db = next(get_db())
    try:
        create_initial_admin(db)
    finally:
        db.close()

# ==========================================
# RAG QUERY ENDPOINTS
# ==========================================

@app.post(
    "/query",
    response_model=QueryResponse,
    tags=["RAG"],
    summary="Consultar RAG",
    description="Endpoint principal. Procesa la pregunta, recupera contexto, y genera respuesta con Claude."
)
async def query_rag(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Procesar consulta RAG."""
    # 1. Gestionar Conversación
    if request.conversation_id:
        conversation = get_conversation(db, request.conversation_id, current_user.id)
        conv_id = request.conversation_id
    else:
        # Crear nueva si no existe
        title = request.question[:30] + "..."
        conversation = create_conversation(db, current_user.id, title)
        conv_id = conversation.id
        
    # 2. Guardar mensaje del usuario
    user_msg = add_message(
        db, 
        conv_id, 
        "user", 
        request.question
    )
    
    # 3. Obtener historial (incluyendo el mensaje nuevo)
    # Nota: rag_engine.ask maneja el historial si se le pasa, 
    # pero aquí podemos obtenerlo limpio desde DB
    history = get_conversation_history(db, conv_id)
    # Excluimos el último mensaje para no duplicarlo si ask() lo añade al prompt
    # o simplemente pasamos el historial previo
    chat_history = history[:-1] if history else []
    
    # 4. Llamar a Claude RAG
    try:
        # ask() espera query y historial de chat
        # Modificamos ask() para aceptar chat_history list[dict]
        result = rag_engine.ask(request.question, conversation_history=chat_history)
        
        answer = result.get("answer", "No answer generated.")
        sources = result.get("sources", [])
        tokens_in = result.get("tokens_input", 0)
        tokens_out = result.get("tokens_output", 0)
        cost = result.get("cost_usd", 0.0)
        
    except Exception as e:
        logger.error(f"RAG Engine Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
        
    # 5. Guardar respuesta assistant
    assist_msg = add_message(
        db,
        conv_id,
        "assistant",
        answer,
        tokens_input=tokens_in,
        tokens_output=tokens_out,
        cost_usd=cost
    )
    
    # 6. Track Usage
    track_query(db, current_user.id, tokens_in, tokens_out)
    
    # 7. Retornar respuesta
    return {
        "answer": answer,
        "sources": sources,
        "tokens_input": tokens_in,
        "tokens_output": tokens_out,
        "cost_usd": cost,
        "conversation_id": conv_id,
        "message_id": assist_msg.id
    }

# ==========================================
# ADMIN ENDPOINTS
# ==========================================

from backend.admin_service import (
    get_all_users,
    get_user_by_id,
    create_user_admin,
    update_user_password,
    toggle_user_active,
    delete_user,
    list_documents,
    upload_documents,
    delete_document
)
from backend.auth import require_admin
from backend.usage_tracker import get_user_usage, get_all_users_usage, get_realtime_usage
from backend.schemas import UserUsageResponse, UsageStatsResponse
from fastapi import UploadFile, File
from typing import List
from datetime import date

# --- USER MANAGEMENT ---

@app.post(
    "/admin/users/create",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
    summary="Crear Usuario (Admin)",
    description="Crea un usuario permitiendo rol admin."
)
async def admin_create_user(
    user: UserRegister,
    db: Session = Depends(get_db)
):
    return create_user_admin(db, user)

@app.get(
    "/admin/users",
    response_model=List[UserResponse],
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
    summary="Listar Usuarios"
)
async def admin_list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_all_users(db, skip, limit)

@app.get(
    "/admin/users/{user_id}",
    response_model=UserResponse,
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
    summary="Detalle Usuario"
)
async def admin_get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    return get_user_by_id(db, user_id)

@app.put(
    "/admin/users/{user_id}/password",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
    summary="Cambiar Password"
)
async def admin_update_password(
    user_id: str,
    password_data: PasswordUpdate,
    db: Session = Depends(get_db)
):
    """Body: {"new_password": "..."}"""
    update_user_password(db, user_id, password_data.new_password)
    return {"message": "Password updated successfully"}

@app.put(
    "/admin/users/{user_id}/toggle-active",
    response_model=UserResponse,
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
    summary="Activar/Desactivar"
)
async def admin_toggle_active(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return toggle_user_active(db, user_id, str(current_user.id))

@app.delete(
    "/admin/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
    summary="Eliminar Usuario"
)
async def admin_delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    delete_user(db, user_id, str(current_user.id))
    return None

# --- DOCUMENT MANAGEMENT ---

@app.post(
    "/admin/documents/upload",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
    summary="Subir Documentos",
    status_code=status.HTTP_201_CREATED,
    response_model=DocumentUploadResponse
)
async def admin_upload_docs(
    files: List[UploadFile] = File(...)
):
    saved = upload_documents(files)
    return {"uploaded": len(saved), "files": saved}

@app.post(
    "/admin/documents/reindex",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
    summary="Reindexar Todo",
    response_model=ReindexResponse
)
async def admin_reindex():
    """Ejecuta reindexado completo de ChromaDB."""
    stats = rag_engine.reindex_all()
    # Map keys to Schema
    return {
        "status": stats.get("status"),
        "chunks_indexed": stats.get("chunks_indexed", 0),
        "time_seconds": stats.get("elapsed_time_seconds", 0.0),
        "documents_processed": stats.get("documents_found", 0)
    }

@app.get(
    "/admin/documents",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
    summary="Listar Documentos",
    response_model=List[DocumentInfo]
)
async def admin_list_docs():
    return list_documents()

@app.delete(
    "/admin/documents/{filename}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
    summary="Eliminar Documento"
)
async def admin_delete_doc(filename: str):
    delete_document(filename)
    return None

# --- STATS ---

@app.get(
    "/admin/usage/user/{user_id}",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
    summary="Estadísticas de Usuario",
    response_model=UserUsageResponse 
)
async def admin_user_stats(
    user_id: str,
    date_from: date = None, 
    date_to: date = None,
    db: Session = Depends(get_db)
):
    # Nota: UserUsageResponse espera 'daily_stats', el tracker lo devuelve
    return get_user_usage(db, user_id, date_from, date_to)

@app.get(
    "/admin/usage/global",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
    summary="Estadísticas Globales",
    response_model=List[UserUsageResponse] 
)
async def admin_global_stats(
    date_from: date = None, 
    date_to: date = None,
    db: Session = Depends(get_db)
):
    # retorna lista de usuarios con totales
    # El response model debe coincidir con la estructura devuelta por get_all_users_usage
    # Estructura tracker: [{user: User, total_cost_usd: float...}]
    # Estructura Schema: UserUsageResponse (tiene user_id, totals, daily_stats...)
    # Ajuste: get_all_users_usage devuelve una lista custom, necesitamos otro schema o adaptar
    return get_all_users_usage(db, date_from, date_to)

@app.get(
    "/admin/usage/realtime",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
    summary="Estadísticas Tiempo Real",
    response_model=RealtimeUsageResponse
)
async def admin_realtime_stats(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    return get_realtime_usage(db, hours)

# ==========================================
# SYSTEM ENDPOINTS
# ==========================================

@app.post(
    "/auth/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario con rol 'user'. El username y email deben ser únicos.",
    responses={
        201: {"description": "Usuario creado exitosamente"},
        400: {"description": "Username o email ya existen"},
    }
)
async def register(user: UserRegister, db: Session = Depends(get_db)):
    """Registrar un nuevo usuario."""
    # Verificar username
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )
    # Verificar email
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Crear usuario
    hashed_pass = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pass,
        role=user.role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post(
    "/auth/login", 
    response_model=Token,
    tags=["Authentication"],
    summary="Iniciar sesión",
    description="Autentica un usuario y devuelve un JWT Access Token + datos del perfil.",
    responses={
        200: {"description": "Login exitoso"},
        401: {"description": "Credenciales inválidas"},
    }
)
async def login(form_data: UserLogin, db: Session = Depends(get_db)):
    """Iniciar sesión y obtener token JWT."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas (usuario o contraseña)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token acces con datos extra
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
    }
    access_token = create_access_token(data=token_data)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
        }
    }

@app.get(
    "/auth/me", 
    response_model=UserResponse,
    tags=["Authentication"],
    summary="Perfil de usuario",
    description="Obtiene los datos del usuario autenticado actual.",
    responses={
        200: {"description": "Perfil recuperado"},
        401: {"description": "No autenticado o token inválido"},
    }
)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Obtener perfil del usuario actual."""
    return current_user

@app.post(
    "/auth/refresh", 
    response_model=Token,
    tags=["Authentication"],
    summary="Refrescar token",
    description="Genera un nuevo token de acceso para mantener la sesión activa.",
    responses={
        200: {"description": "Token renovado"},
        401: {"description": "Token actual inválido o expirado"},
    }
)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refrescar token JWT (obtiene uno nuevo)."""
    token_data = {
        "sub": str(current_user.id),
        "username": current_user.username,
        "role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    }
    access_token = create_access_token(data=token_data)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        }
    }

# ==========================================
# CONVERSATION ENDPOINTS
# ==========================================

@app.post(
    "/conversations/create",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Conversations"],
    summary="Crear conversación",
    description="Inicializa una nueva sesión de chat vacía para el usuario."
)
async def create_new_conversation(
    conv: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear una nueva conversación."""
    return create_conversation(db, current_user.id, conv.title)

@app.get(
    "/conversations",
    response_model=list[ConversationResponse],
    tags=["Conversations"],
    summary="Listar conversaciones",
    description="Obtiene el historial de conversaciones del usuario, ordenadas por fecha reciente."
)
async def list_conversations(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar conversaciones del usuario."""
    return get_user_conversations(db, current_user.id, skip, limit)

@app.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
    tags=["Conversations"],
    summary="Obtener conversación",
    description="Recupera una conversación específica con todos sus mensajes."
)
async def read_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener detalle de conversación."""
    return get_conversation(db, conversation_id, current_user.id)

@app.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Conversations"],
    summary="Eliminar conversación",
    description="Borra permanentemente una conversación y sus mensajes."
)
async def remove_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar conversación."""
    delete_conversation(db, conversation_id, current_user.id)
    return None

@app.put(
    "/conversations/{conversation_id}/title",
    response_model=ConversationResponse,
    tags=["Conversations"],
    summary="Actualizar título",
    description="Modifica el título de una conversación existente."
)
async def update_title(
    conversation_id: str,
    title_data: ConversationTitleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar título."""
    return update_conversation_title(db, conversation_id, title_data.title, current_user.id)

@app.get(
    "/health",
    tags=["System"],
    summary="Health Check",
    description="Verifica que la API esté operativa.",
    status_code=status.HTTP_200_OK
)
async def health_check():
    """Verificar estado de la API."""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
