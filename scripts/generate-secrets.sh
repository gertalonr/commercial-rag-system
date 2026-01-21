#!/bin/bash

# Script para generar secretos seguros para el sistema

echo "🔐 Generando secretos seguros para Commercial RAG System..."
echo ""

# Generar JWT secret
JWT_SECRET=$(openssl rand -hex 32)
echo "JWT_SECRET_KEY=$JWT_SECRET"
echo ""

# Generar password de BD
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
echo "DB_PASSWORD=$DB_PASSWORD"
echo ""

# Generar password de admin
ADMIN_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-20)
echo "ADMIN_PASSWORD=$ADMIN_PASSWORD"
echo ""

echo "⚠️  IMPORTANTE: Guarda estos secretos en un lugar seguro"
echo "⚠️  Cópialos al archivo .env antes de desplegar"
echo ""

# Opción para escribir directamente al .env
read -p "¿Deseas escribir estos valores automáticamente en .env? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f .env ]; then
        echo "⚠️  El archivo .env ya existe. Creando backup..."
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
    cp .env.example .env
    
    # Reemplazar valores
    # Usamos sed con separador | para evitar conflictos con caracteres especiales
    # Forzamos backup con extensión vacía para compatibilidad mac/linux si fuera necesario, 
    # pero aquí asumimos entorno estándar o usamos sed -i '' en mac. 
    # Para ser portable:
    
    OSTYPE="$(uname -s)"
    if [[ "$OSTYPE" == "Darwin"* ]]; then
        # Mac requires empty string for backup extension
        SED_CMD="sed -i ''"
    else
        SED_CMD="sed -i"
    fi
    
    # Reemplazar valores (compatible con Mac y Linux)
    # Mac sed requiere extensión de backup, usamos temp file para compatibilidad
    sed "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET/" .env > .env.tmp && mv .env.tmp .env
    sed "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env > .env.tmp && mv .env.tmp .env
    sed "s/ADMIN_PASSWORD=.*/ADMIN_PASSWORD=$ADMIN_PASSWORD/" .env > .env.tmp && mv .env.tmp .env
    
    # Actualizar DATABASE_URL
    sed "s|DATABASE_URL=.*|DATABASE_URL=postgresql://raguser:$DB_PASSWORD@db:5432/commercial_rag|" .env > .env.tmp && mv .env.tmp .env
    
    echo "✅ Archivo .env creado con secretos seguros"
    echo "⚠️  Recuerda añadir tu ANTHROPIC_API_KEY al archivo .env"
else
    echo "Copia manualmente los valores al archivo .env"
fi

echo ""
echo "✅ Proceso completado"
