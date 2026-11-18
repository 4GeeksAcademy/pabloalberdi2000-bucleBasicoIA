#!/usr/bin/env bash
# Script para arrancar la API y el Agente en modo desarrollo

set -e

echo "=============================================="
echo "🏪 Sistema de Inventario para Cafeterías"
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
pip install -q fastapi uvicorn pydantic httpx anthropic openai 2>/dev/null || {
    echo "⚠️  Error instalando dependencias. Intenta:"
    echo "   pip install fastapi uvicorn pydantic httpx anthropic openai"
    exit 1
}
echo "✓ Dependencias listas."

# Verifica las variables de entorno
echo ""
if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  ADVERTENCIA: Ninguna clave de API está configurada."
    echo "   Por favor, configura una de estas variables de entorno:"
    echo ""
    echo "   Para Anthropic Claude:"
    echo "   export ANTHROPIC_API_KEY='tu-clave-aqui'"
    echo ""
    echo "   Para OpenAI:"
    echo "   export OPENAI_API_KEY='tu-clave-aqui'"
    echo ""
    echo "   Luego ejecuta este script de nuevo."
    exit 1
fi

echo "✓ Clave de API detectada."

# Verifica si la API está disponible
echo ""
echo "🚀 Iniciando API FastAPI..."
echo "   Ejecuta en OTRA terminal:"
echo ""
echo "   cd $(pwd)"
echo "   source venv/bin/activate"
echo "   python -m uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "⏳ Presiona ENTER una vez que hayas iniciado la API..."
read -r

# Verifica la conectividad a la API
echo "🔍 Verificando conectividad con la API..."
max_attempts=10
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ API detectada en http://localhost:8000"
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
    echo "  Intento $attempt de $max_attempts..."
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ No se pudo conectar a la API."
    echo "   Asegúrate de que esté corriendo en otra terminal."
    exit 1
fi

# Inicia el agente
echo ""
echo "🏃 Iniciando Agente..."
echo ""
python agent.py
