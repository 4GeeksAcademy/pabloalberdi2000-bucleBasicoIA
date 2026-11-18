#!/usr/bin/env bash
# Script para arrancar el Agente

set -e

echo "=============================================="
echo "🏪 Agente de Inventario para Cafeterías"
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
pip install -q httpx anthropic openai 2>/dev/null || {
    echo "⚠️  Error instalando dependencias. Intenta:"
    echo "   pip install httpx anthropic openai"
    exit 1
}
echo "✓ Dependencias listas."

# Verifica las variables de entorno
echo ""
if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERROR: Ninguna clave de API está configurada."
    echo ""
    echo "   Para Anthropic Claude:"
    echo "   export ANTHROPIC_API_KEY='tu-clave-aqui'"
    echo ""
    echo "   Para OpenAI:"
    echo "   export OPENAI_API_KEY='tu-clave-aqui'"
    echo ""
    exit 1
fi

# Verifica la conectividad a la API
echo ""
echo "🔍 Verificando conectividad con la API en http://localhost:8000..."

if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ No se pudo conectar a la API."
    echo ""
    echo "   Asegúrate de que esté corriendo en otra terminal:"
    echo "   ./start-api.sh"
    echo ""
    exit 1
fi

echo "✓ API detectada."
echo ""

# Inicia el agente
echo "🚀 Iniciando Agente..."
echo ""
python agent.py
