#!/bin/bash
set -e

echo "🚀 Starting Commercial RAG System..."

# Iniciar servicios según el comando
if [ "$1" = "backend" ]; then
    # Esperar a que PostgreSQL esté listo (solo para backend)
    echo "⏳ Waiting for PostgreSQL..."
    while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
        sleep 1
    done
    echo "✅ PostgreSQL is ready"

    # Inicializar base de datos si es necesario
    echo "📊 Initializing database..."
    python -c "from backend.database import init_db; init_db()"

    # Crear usuario admin inicial
    echo "👤 Creating initial admin user..."
    python -c "
from backend.database import get_db
from backend.auth import create_initial_admin
db = next(get_db())
create_initial_admin(db)
db.close()
"

    # Indexar documentos si existen
    if [ -n "$(ls -A /app/data/documents/ 2>/dev/null)" ]; then
        echo "📚 Indexing documents..."
        python backend/init_rag.py --index-docs
    fi

    echo "✅ Initialization complete"
    echo "🔧 Starting FastAPI backend..."
    exec uvicorn backend.app:app --host 0.0.0.0 --port 8000

elif [ "$1" = "frontend" ]; then
    # Frontend no necesita esperar a la BD, solo al backend (manejado por docker-compose depends_on)
    echo "🎨 Starting Streamlit frontend..."
    exec streamlit run frontend/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
else
    echo "❌ Unknown service: $1"
    exit 1
fi
