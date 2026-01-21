#!/bin/bash

echo "🏥 Commercial RAG System - Health Check"
echo "========================================"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
    local service=$1
    local url=$2
    
    if curl -f -s -o /dev/null "$url"; then
        echo -e "${GREEN}✅ $service${NC} - OK"
        return 0
    else
        echo -e "${RED}❌ $service${NC} - ERROR"
        return 1
    fi
}

# Verificar contenedores
echo "📦 Verificando contenedores..."
if docker-compose ps | grep -q "Up"; then
    docker-compose ps
    echo ""
else
    echo -e "${RED}❌ No hay contenedores corriendo${NC}"
    exit 1
fi

# Verificar servicios
echo "🔍 Verificando servicios..."
check_service "PostgreSQL" "localhost:5432" || true
check_service "Backend API" "http://localhost:8000/health"
check_service "Frontend" "http://localhost:8501"

echo ""
echo "📊 Recursos utilizados:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo "✅ Health check completado"
