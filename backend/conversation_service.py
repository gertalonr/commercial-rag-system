from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from uuid import UUID
from datetime import datetime
from typing import List, Dict, Optional
import logging

from backend.database import Conversation, Message, User
from backend.schemas import ConversationCreate, MessageCreate

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_conversation(db: Session, user_id: UUID, title: str) -> Conversation:
    """
    Crea una nueva conversación para el usuario.
    """
    try:
        # Validar usuario (opcional si ya viene autenticado, pero buena práctica)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        new_conversation = Conversation(
            user_id=user_id,
            title=title
        )
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
        logger.info(f"Conversation created: {new_conversation.id} for user {user_id}")
        return new_conversation
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating conversation: {e}")
        raise e

def get_user_conversations(db: Session, user_id: UUID, skip: int = 0, limit: int = 50) -> List[Conversation]:
    """
    Obtiene todas las conversaciones del usuario ordenadas por fecha reciente.
    """
    conversations = db.query(Conversation)\
        .filter(Conversation.user_id == user_id)\
        .order_by(desc(Conversation.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()
    return conversations

def get_conversation(db: Session, conversation_id: UUID, user_id: UUID) -> Conversation:
    """
    Obtiene una conversación específica validando pertenencia.
    Incluye eager loading de mensajes (por defecto en SQLAlchemy si relationship está configurada, 
    pero aquí confiamos en lazy loading o config del modelo).
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversación no encontrada"
        )
    
    if conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes acceso a esta conversación"
        )
        
    return conversation

def add_message(
    db: Session,
    conversation_id: UUID,
    role: str,
    content: str,
    tokens_input: Optional[int] = None,
    tokens_output: Optional[int] = None,
    cost_usd: Optional[float] = None
) -> Message:
    """
    Agrega un mensaje a una conversación existente.
    """
    try:
        # Verificar existencia de conversación (opcional, FK lo valida, pero mejor manejo de error)
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")

        new_message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost_usd=cost_usd,
            timestamp=datetime.utcnow()
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        return new_message
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding message: {e}")
        raise e

def delete_conversation(db: Session, conversation_id: UUID, user_id: UUID) -> bool:
    """
    Elimina una conversación y sus mensajes (Cascade).
    """
    try:
        conversation = get_conversation(db, conversation_id, user_id) # Reusa validación
        
        db.delete(conversation)
        db.commit()
        logger.info(f"Conversation deleted: {conversation_id}")
        return True
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting conversation: {e}")
        raise e

def get_conversation_history(db: Session, conversation_id: UUID) -> List[Dict[str, str]]:
    """
    Obtiene el historial de mensajes formateado para la API de Claude/Anthropic.
    Retorna: [{"role": "user", "content": "..."}, ...]
    """
    messages = db.query(Message)\
        .filter(Message.conversation_id == conversation_id)\
        .order_by(Message.timestamp.asc())\
        .all()
    
    history = []
    for msg in messages:
        # Extrar valor si es Enum, sino usar string directo
        role_val = msg.role.value if hasattr(msg.role, 'value') else str(msg.role)
        history.append({
            "role": role_val,
            "content": msg.content
        })
    return history

def update_conversation_title(db: Session, conversation_id: UUID, title: str, user_id: UUID) -> Conversation:
    """
    Actualiza el título de una conversación.
    """
    try:
        conversation = get_conversation(db, conversation_id, user_id) # Reusa validación
        
        conversation.title = title
        db.commit()
        db.refresh(conversation)
        return conversation
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating conversation title: {e}")
        raise e
