#!/bin/bash
# Script para iniciar la aplicación localmente

echo "🚀 Iniciando Dashboard IT - Clínica Bonsana (Local)"
echo "=================================================="

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "❌ No se encontró el entorno virtual. Creándolo..."
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Verificar si las dependencias están instaladas
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Instalando dependencias..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Dependencias instaladas"
fi

# Verificar archivo .env
if [ ! -f ".env" ]; then
    echo "⚠️  No se encontró archivo .env"
    echo "📝 Creando .env desde .env.example..."
    cp .env.example .env
    echo "✅ Archivo .env creado"
    echo ""
    echo "⚠️  IMPORTANTE: Edita el archivo .env y agrega tu GOOGLE_AI_API_KEY"
    echo "   nano .env"
    echo ""
    read -p "Presiona Enter cuando hayas configurado el .env..."
fi

# Crear directorios necesarios
echo "📁 Verificando directorios..."
mkdir -p data/{cache,reports,backups,metrics} logs/{nginx}
echo "✅ Directorios verificados"

# Mostrar información de inicio
echo ""
echo "🏥 Dashboard IT - Clínica Bonsana"
echo "================================="
echo "🌍 Entorno: desarrollo local"
echo "🏠 URL: http://localhost:5000"
echo "🤖 Análisis IA: http://localhost:5000/ai-analysis"
echo "📊 Dashboard: http://localhost:5000"
echo ""
echo "💡 Tip: Usa Ctrl+C para detener el servidor"
echo ""

# Iniciar aplicación
export FLASK_ENV=development
python run_dashboard.py