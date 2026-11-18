#!/usr/bin/env bash
# Script para arrancar la API FastAPI

set -e

echo "=============================================="
echo "🏪 API de Inventario para Cafeterías"
echo "=============================================="
echo ""

# Verifica si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado."
    exit 1
fi

# Verifica si existe el venv
if [ ! -d "venv" ]; then
    echo "⚠️  Entorno virtual no encontrado. Creando..."
    python3 -m venv venv
    echo "✓ Entorno virtual creado."
fi

# Activa el venv
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# Instala dependencias si es necesario
echo ""
echo "📦 Verificando e instalando dependencias..."
pip install -q fastapi uvicorn pydantic 2>/dev/null || {
    echo "⚠️  Error instalando dependencias. Intenta:"
    echo "   pip install fastapi uvicorn pydantic"
    exit 1
}
echo "✓ Dependencias listas."

# Inicia la API
echo ""
echo "🚀 Iniciando API en http://localhost:8000"
echo ""
echo "   📊 Panel de API: http://localhost:8000/docs"
echo "   🔍 Healthcheck:  http://localhost:8000/health"
echo ""
echo "   Presiona Ctrl+C para detener."
echo ""

python -m uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
