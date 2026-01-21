# Dockerfile para Commercial RAG System
# Multi-stage build para optimizar tamaño

# ============================================
# Stage 1: Base con dependencias de Python
# ============================================
FROM python:3.11-slim as python-base

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ============================================
# Stage 2: Aplicación
# ============================================
FROM python-base as application

# Copiar código fuente
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY .streamlit/ /app/.streamlit/
COPY tests/ /app/tests/

# Crear directorios necesarios
RUN mkdir -p /app/data/documents /app/data/chroma_db /app/data/logs

# Copiar archivos de configuración
COPY .env.example /app/.env.example

# Exponer puertos
# 8000: FastAPI Backend
# 8501: Streamlit Frontend
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Script de inicio
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Usuario no-root por seguridad
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Comando por defecto (se sobreescribe en docker-compose)
CMD ["/app/docker-entrypoint.sh"]
