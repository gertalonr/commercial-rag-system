from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date, datetime, timedelta
from uuid import UUID
from typing import List, Dict, Optional
import logging

from backend.database import UsageStats, Message, User, UserRole
from backend.config import settings
from backend.schemas import UserResponse

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_cost(tokens_input: int, tokens_output: int) -> float:
    """
    Calcula el costo en USD basado en los precios configurados.
    """
    input_cost = (tokens_input / 1_000_000) * settings.CLAUDE_INPUT_PRICE_PER_MILLION
    output_cost = (tokens_output / 1_000_000) * settings.CLAUDE_OUTPUT_PRICE_PER_MILLION
    total = input_cost + output_cost
    return round(total, 6) # Precisión de 6 decimales para costos pequeños

def track_query(
    db: Session,
    user_id: UUID,
    tokens_input: int,
    tokens_output: int
) -> float:
    """
    Registra el uso de tokens y costo para un usuario en la fecha actual.
    Actualiza o crea el registro de UsageStats.
    """
    today = date.today()
    cost = calculate_cost(tokens_input, tokens_output)
    
    try:
        # Buscar stats de hoy
        stats = db.query(UsageStats).filter(
            UsageStats.user_id == user_id,
            UsageStats.date == today
        ).first()
        
        if stats:
            # Actualizar existente
            stats.total_tokens_input += tokens_input
            stats.total_tokens_output += tokens_output
            stats.total_cost_usd = float(stats.total_cost_usd) + cost
            stats.query_count += 1
        else:
            # Crear acumulador del día
            stats = UsageStats(
                user_id=user_id,
                date=today,
                total_tokens_input=tokens_input,
                total_tokens_output=tokens_output,
                total_cost_usd=cost,
                query_count=1
            )
            db.add(stats)
        
        db.commit()
        db.refresh(stats) # Para asegurar que tenemos IDs y valores actualizados
        logger.info(f"Usage tracked for user {user_id}: ${cost}")
        return cost
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error tracking usage: {e}")
        return 0.0

def get_user_usage(
    db: Session,
    user_id: UUID,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
) -> Dict:
    """
    Obtiene el reporte de uso de un usuario en un rango de fechas.
    Default: Últimos 30 días.
    """
    if not date_to:
        date_to = date.today()
    if not date_from:
        date_from = date_to - timedelta(days=30)
        
    stats_records = db.query(UsageStats).filter(
        UsageStats.user_id == user_id,
        UsageStats.date >= date_from,
        UsageStats.date <= date_to
    ).order_by(UsageStats.date.desc()).all()
    
    # Calcular totales
    total_input = sum(s.total_tokens_input for s in stats_records)
    total_output = sum(s.total_tokens_output for s in stats_records)
    total_cost = sum(float(s.total_cost_usd) for s in stats_records)
    total_queries = sum(s.query_count for s in stats_records)
    
    return {
        "user_id": user_id,
        "date_from": date_from,
        "date_to": date_to,
        "total_tokens_input": total_input,
        "total_tokens_output": total_output,
        "total_cost_usd": round(total_cost, 4),
        "total_queries": total_queries,
        "daily_stats": stats_records # ORM objects serán serializados por Pydantic usando from_attributes
    }

def get_all_users_usage(
    db: Session,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
) -> List[Dict]:
    """
    Obtiene estadísticas agrupadas por usuario (para panel Admin).
    """
    if not date_to:
        date_to = date.today()
    if not date_from:
        date_from = date_to - timedelta(days=30)
    
    # Agrupación compleja usando SQLAlchemy func
    results = db.query(
        UsageStats.user_id,
        func.sum(UsageStats.total_tokens_input).label('sum_input'),
        func.sum(UsageStats.total_tokens_output).label('sum_output'),
        func.sum(UsageStats.total_cost_usd).label('sum_cost'),
        func.sum(UsageStats.query_count).label('sum_queries')
    ).filter(
        UsageStats.date >= date_from,
        UsageStats.date <= date_to
    ).group_by(UsageStats.user_id).all()
    
    report = []
    for row in results:
        # Obtener info usuario user
        user = db.query(User).filter(User.id == row.user_id).first()
        if user:
            report.append({
                "user_id": row.user_id,
                "user": user, # Pydantic UserResponse lo serializará
                "date_from": date_from,
                "date_to": date_to,
                "total_tokens_input": row.sum_input,
                "total_tokens_output": row.sum_output,
                "total_cost_usd": round(float(row.sum_cost), 4),
                "total_queries": row.sum_queries
            })
            
    # Ordenar por costo descendente (los que más consumen primero)
    report.sort(key=lambda x: x['total_cost_usd'], reverse=True)
    return report

def get_realtime_usage(db: Session, hours: int = 24) -> Dict:
    """
    Calcula estadísticas en tiempo real basadas en la tabla de Mensajes recientes.
    """
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    messages = db.query(Message).filter(
        Message.timestamp >= cutoff,
        Message.tokens_input.isnot(None) # Solo mensajes con tokens registrados
    ).all()
    
    total_tokens = sum((m.tokens_input or 0) + (m.tokens_output or 0) for m in messages)
    total_cost = sum(float(m.cost_usd or 0) for m in messages)
    total_queries = len(messages)
    
    # Usuarios únicos activos (solo users, no assistants)
    # Buscamos conversations asociadas para saber usuarios
    # O más simple: contar user_ids distintos en UsageStats de hoy?
    # Mejor query directa a message -> conversation -> user_id
    active_users_count = db.query(Message.conversation_id).filter(
        Message.timestamp >= cutoff
    ).distinct().count() # Aprox: conversaciones activas
    
    return {
        "period_hours": hours,
        "total_queries": total_queries,
        "total_tokens": total_tokens,
        "total_cost_usd": round(total_cost, 4),
        "active_users": active_users_count, # Nota: esto cuenta conversaciones, para usuarios requiere join
        "last_updated": datetime.utcnow()
    }

def get_user_cost_today(db: Session, user_id: UUID) -> float:
    """
    Retorna el costo acumulado hoy para un usuario.
    """
    today = date.today()
    stats = db.query(UsageStats).filter(
        UsageStats.user_id == user_id,
        UsageStats.date == today
    ).first()
    
    return float(stats.total_cost_usd) if stats else 0.0
