from sqlalchemy import create_engine, Column, String, Boolean, DateTime, ForeignKey, Text, Integer, Numeric, Enum as SAEnum, UniqueConstraint, Date
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum
from typing import Generator
from backend.config import settings

# --- Enums ---
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"

# --- Database Setup ---
# Setup connection args based on the database type
connect_args = {}
# Assuming PostgreSQL for production as requested, but keeping it flexible if URL changes to sqlite for testing
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args=connect_args,
    # pool_pre_ping=True # Useful for Postgres to handle connection drops
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- Models ---

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    usage_stats = relationship("UsageStats", back_populates="user", cascade="all, delete-orphan")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(SAEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Metadata for usage tracking
    tokens_input = Column(Integer, nullable=True)
    tokens_output = Column(Integer, nullable=True)
    cost_usd = Column(Numeric(10, 6), nullable=True) # Precision for small costs

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class UsageStats(Base):
    __tablename__ = "usage_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    total_tokens_input = Column(Integer, default=0, nullable=False)
    total_tokens_output = Column(Integer, default=0, nullable=False)
    total_cost_usd = Column(Numeric(10, 6), default=0, nullable=False)
    query_count = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="usage_stats")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='uq_user_date_stats'),
    )

# --- Dependency ---
def get_db() -> Generator[Session, None, None]:
    """
    Dependency generator for database sessions.
    yields a SQLAlchemy Session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Initialization ---
def init_db():
    """
    Creates all tables in the database.
    """
    Base.metadata.create_all(bind=engine)
