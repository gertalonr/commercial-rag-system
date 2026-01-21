import logging
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import User, get_db, UserRole

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de seguridad
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Constantes de error
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciales de autenticación inválidas",
    headers={"WWW-Authenticate": "Bearer"},
)

INACTIVE_USER_EXCEPTION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Usuario inactivo"
)

FORBIDDEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="No tienes permisos suficientes"
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera hash de la contraseña usando bcrypt."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Crea un token JWT de acceso.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Decodifica y valida el token JWT.
    Raise HTTPException si es inválido o expirado.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise CREDENTIALS_EXCEPTION

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Busca usuario y verifica contraseña.
    Retorna el usuario si es válido, None en caso contrario.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependency para obtener el usuario actual desde el header Authorization.
    """
    payload = decode_access_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise CREDENTIALS_EXCEPTION
        
    # Buscar usuario en BD (podría cachearse)
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise CREDENTIALS_EXCEPTION
    if not user.is_active:
        raise INACTIVE_USER_EXCEPTION
        
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency para verificar que el usuario es administrador.
    """
    if current_user.role != UserRole.ADMIN:
        raise FORBIDDEN_EXCEPTION
    return current_user

def create_initial_admin(db: Session):
    """
    Crea el usuario administrador inicial si no existe.
    """
    try:
        user = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if user:
            logger.info(f"Admin user {settings.ADMIN_EMAIL} already exists.")
            return

        logger.info(f"Creating initial admin user {settings.ADMIN_EMAIL}...")
        new_admin = User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password_hash=get_password_hash(settings.ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        logger.info("Initial admin user created successfully.")
    except Exception as e:
        logger.error(f"Error creating initial admin: {e}")
        db.rollback()
