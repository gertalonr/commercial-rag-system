from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from typing import List, Dict, Any
import os
import shutil
from datetime import datetime
import logging

from backend.database import User, UserRole, Conversation
from backend.auth import get_password_hash
from backend.rag_engine import ClaudeRAG

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOCS_DIR = "data/documents"
os.makedirs(DOCS_DIR, exist_ok=True)

# ==========================================
# USER MANAGEMENT
# ==========================================

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Listar todos los usuarios."""
    return db.query(User).offset(skip).limit(limit).all()

def get_user_by_id(db: Session, user_id: str) -> User:
    """Obtener usuario por ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

def create_user_admin(db: Session, user_data: Any) -> User:
    """Crear usuario (permite asignar rol desde admin)."""
    # Verificar existencia
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username ya existe")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email ya existe")
        
    hashed_pass = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_pass,
        role=user_data.role, # Admin puede establecer rol
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user_password(db: Session, user_id: str, new_password: str):
    """Actualizar contraseña de un usuario."""
    user = get_user_by_id(db, user_id)
    
    if len(new_password) < 8:
         raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
         
    user.password_hash = get_password_hash(new_password)
    db.commit()
    return True

def toggle_user_active(db: Session, user_id: str, current_admin_id: str) -> User:
    """Activar/Desactivar usuario."""
    user = get_user_by_id(db, user_id)
    
    # Prevenir auto-bloqueo
    if str(user.id) == str(current_admin_id):
        raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta")
        
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: str, current_admin_id: str):
    """Eliminar usuario (y sus datos relacionados por Cascade)."""
    user = get_user_by_id(db, user_id)
    
    # Prevenir auto-eliminación
    if str(user.id) == str(current_admin_id):
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta")
        
    db.delete(user)
    db.commit()
    return True

# ==========================================
# DOCUMENT MANAGEMENT
# ==========================================

def list_documents() -> List[Dict[str, Any]]:
    """Listar archivos en el directorio de documentos."""
    files = []
    if not os.path.exists(DOCS_DIR):
        return []
        
    for filename in os.listdir(DOCS_DIR):
        filepath = os.path.join(DOCS_DIR, filename)
        if os.path.isfile(filepath):
            stats = os.stat(filepath)
            files.append({
                "filename": filename,
                "size_bytes": stats.st_size,
                "modified": datetime.fromtimestamp(stats.st_mtime),
                "extension": os.path.splitext(filename)[1].lower()
            })
    return files

def upload_documents(files: List[UploadFile]) -> List[str]:
    """Guardar archivos subidos."""
    saved_files = []
    valid_extensions = {'.pdf', '.docx', '.txt', '.md'}
    
    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in valid_extensions:
            continue
            
        file_path = os.path.join(DOCS_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file.filename)
        
    return saved_files

def delete_document(filename: str):
    """Eliminar un archivo físico."""
    # Validación básica de seguridad de path traversal
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(DOCS_DIR, safe_filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    else:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
