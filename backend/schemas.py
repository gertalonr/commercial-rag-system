from datetime import datetime, date
from typing import List, Optional, Literal, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator

# ==========================================
# AUTH SCHEMAS
# ==========================================

class UserLogin(BaseModel):
    """Schema para login de usuario."""
    username: str
    password: str

class UserRegister(BaseModel):
    """Schema para registro de nuevos usuarios."""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario único")
    email: EmailStr = Field(..., description="Email válido")
    password: str = Field(..., min_length=8, description="Contraseña segura (min 8 caracteres)")
    role: Literal['admin', 'user'] = 'user'

class Token(BaseModel):
    """Schema para respuesta de token JWT."""
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]  # id, username, email, role

class UserResponse(BaseModel):
    """Schema para retornar datos de usuario (sin password)."""
    id: UUID
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
   
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# CONVERSATION SCHEMAS
# ==========================================

class MessageCreate(BaseModel):
    """Schema para crear un mensaje (usuario)."""
    content: str
    role: Literal['user', 'assistant']

class MessageResponse(BaseModel):
    """Schema para respuesta de mensaje."""
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    timestamp: datetime
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    cost_usd: Optional[float] = None
   
    model_config = ConfigDict(from_attributes=True)

class ConversationCreate(BaseModel):
    """Schema para crear una nueva conversación."""
    title: str = Field(..., description="Título de la conversación")

class ConversationResponse(BaseModel):
    """Schema para respuesta de conversación con sus mensajes."""
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    messages: List[MessageResponse] = []
   
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# RAG QUERY SCHEMAS
# ==========================================

class QueryRequest(BaseModel):
    """Schema para realizar una consulta RAG."""
    question: str = Field(..., min_length=1, description="La pregunta del usuario")
    conversation_id: Optional[UUID] = Field(None, description="ID de conversación existente (opcional)")

class QueryResponse(BaseModel):
    """Schema para la respuesta del motor RAG."""
    answer: str
    sources: List[str]
    tokens_input: int
    tokens_output: int
    cost_usd: float
    conversation_id: UUID
    message_id: UUID

# ==========================================
# ADMIN SCHEMAS
# ==========================================

class UserUpdate(BaseModel):
    """Schema para actualizar usuario (Admin)."""
    is_active: Optional[bool] = None
    role: Optional[str] = None

class PasswordUpdate(BaseModel):
    new_password: str = Field(..., min_length=8)

class UsageStatsResponse(BaseModel):
    """Schema para estadísticas diarias de uso."""
    date: date
    total_tokens_input: int
    total_tokens_output: int
    total_cost_usd: float
    query_count: int

    model_config = ConfigDict(from_attributes=True)

class UserUsageResponse(BaseModel):
    """Schema para reporte de uso de un usuario."""
    user_id: Optional[UUID] = None
    user: Optional[UserResponse] = None
    
    date_from: date
    date_to: date
    
    total_tokens_input: int
    total_tokens_output: int
    total_cost_usd: float
    total_queries: int
    
    daily_stats: Optional[list[UsageStatsResponse]] = None

    model_config = ConfigDict(from_attributes=True)

class RealtimeUsageResponse(BaseModel):
    period_hours: int
    total_queries: int
    total_tokens: int
    total_cost_usd: float
    active_users: int
    last_updated: datetime

# ==========================================
# DOCUMENT SCHEMAS
# ==========================================

class DocumentInfo(BaseModel):
    filename: str
    size_bytes: int
    modified: datetime
    extension: str

class DocumentUploadResponse(BaseModel):
    uploaded: int
    files: List[str]

class ReindexResponse(BaseModel):
    status: str
    chunks_indexed: int
    time_seconds: float
    documents_processed: Optional[int] = 0

# ==========================================
# UTILITY SCHEMAS
# ==========================================

class ConversationTitleUpdate(BaseModel):
    title: str = Field(..., max_length=200)
