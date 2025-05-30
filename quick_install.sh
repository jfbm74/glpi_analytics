#!/bin/bash
# quick_install.sh - Instalación rápida del Dashboard IT con IA
# Dashboard IT - Clínica Bonsana

set -e  # Salir si cualquier comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}"
    echo "======================================================"
    echo "🏥 DASHBOARD IT - CLÍNICA BONSANA CON IA 🤖"
    echo "======================================================"
    echo -e "${NC}"
}

# Variables globales
PYTHON_MIN_VERSION="3.8"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
DATA_DIR="$PROJECT_DIR/data"
LOGS_DIR="$PROJECT_DIR/logs"

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Función para verificar versión de Python
check_python_version() {
    print_status "Verificando versión de Python..."
    
    if ! command_exists python3; then
        print_error "Python 3 no está instalado"
        echo "Instala Python 3.8+ desde: https://python.org"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        print_error "Python $PYTHON_VERSION encontrado, se requiere $PYTHON_MIN_VERSION+"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION - Compatible"
}

# Función para detectar el sistema operativo
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command_exists apt-get; then
            OS="ubuntu"
        elif command_exists yum; then
            OS="centos"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    
    print_status "Sistema operativo detectado: $OS"
}

# Función para instalar dependencias del sistema
install_system_dependencies() {
    print_status "Instalando dependencias del sistema..."
    
    case $OS in
        "ubuntu")
            sudo apt update
            sudo apt install -y python3-pip python3-venv python3-dev git curl
            ;;
        "centos")
            sudo yum install -y python3-pip python3-devel git curl
            ;;
        "macos")
            if command_exists brew; then
                brew install python git curl
            else
                print_warning "Homebrew no encontrado. Instala manualmente Python 3.8+"
            fi
            ;;
        "windows")
            print_warning "Windows detectado. Asegúrate de tener Python 3.8+ y Git instalados"
            ;;
        *)
            print_warning "Sistema operativo no reconocido. Asegúrate de tener Python 3.8+ instalado"
            ;;
    esac
    
    print_success "Dependencias del sistema instaladas"
}

# Función para crear entorno virtual
create_virtual_environment() {
    print_status "Creando entorno virtual..."
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Entorno virtual existe. Eliminando..."
        rm -rf "$VENV_DIR"
    fi
    
    python3 -m venv "$VENV_DIR"
    
    # Activar entorno virtual
    source "$VENV_DIR/bin/activate"
    
    # Actualizar pip
    pip install --upgrade pip
    
    print_success "Entorno virtual creado y activado"
}

# Función para instalar dependencias Python
install_python_dependencies() {
    print_status "Instalando dependencias de Python..."
    
    # Asegurar que el entorno virtual esté activado
    source "$VENV_DIR/bin/activate"
    
    # Instalar dependencias
    pip install -r requirements.txt
    
    # Verificar instalación de dependencias críticas
    python -c "import flask; print('✅ Flask instalado')"
    python -c "import pandas; print('✅ Pandas instalado')"
    python -c "import google.generativeai; print('✅ Google AI instalado')"
    
    print_success "Dependencias de Python instaladas"
}

# Función para crear directorios necesarios
create_directories() {
    print_status "Creando estructura de directorios..."
    
    mkdir -p "$DATA_DIR"
    mkdir -p "$LOGS_DIR"
    mkdir -p "$PROJECT_DIR/backups"
    mkdir -p "$PROJECT_DIR/temp"
    
    print_success "Directorios creados"
}

# Función para configurar archivo .env
setup_environment_file() {
    print_status "Configurando archivo de entorno..."
    
    ENV_FILE="$PROJECT_DIR/.env"
    
    if [ -f "$ENV_FILE" ]; then
        print_warning "Archivo .env existe. Creando backup..."
        cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Crear .env básico
    cat > "$ENV_FILE" << EOF
# Configuración del Dashboard IT - Clínica Bonsana con IA
# Generado por quick_install.sh - $(date)

# Configuración de Flask
FLASK_ENV=development
SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "change-this-secret-key-in-production")

# Configuración de Google AI Studio
GOOGLE_AI_API_KEY=
GOOGLE_AI_MODEL=gemini-1.5-pro
AI_ANALYSIS_ENABLED=True

# Configuración de datos
DATA_DIRECTORY=data
CSV_ENCODING=utf-8
LOG_LEVEL=INFO

# Configuración de IA
MAX_CSV_SIZE_MB=10
AI_ANALYSIS_TIMEOUT=300
EOF
    
    chmod 600 "$ENV_FILE"
    print_success "Archivo .env creado"
}

# Función para generar datos de muestra
generate_sample_data() {
    print_status "Generando datos de muestra..."
    
    CSV_FILE="$DATA_DIR/glpi.csv"
    
    if [ -f "$CSV_FILE" ]; then
        print_warning "Archivo CSV existe. Manteniendo datos existentes."
        return
    fi
    
    # Activar entorno virtual
    source "$VENV_DIR/bin/activate"
    
    # Generar datos de muestra usando utils.py
    if [ -f "$PROJECT_DIR/utils.py" ]; then
        python "$PROJECT_DIR/utils.py" generate-sample "$CSV_FILE" --records 50
        print_success "Datos de muestra generados"
    else
        # Crear CSV básico manualmente
        cat > "$CSV_FILE" << 'EOF'
ID;Título;Tipo;Categoría;Prioridad;Estado;Fecha de Apertura;Fecha de solución;Se superó el tiempo de resolución;Asignado a: - Técnico;Solicitante - Solicitante;Elementos asociados;ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución;Encuesta de satisfacción - Satisfacción
1;Falla impresora consultorio 1;Incidencia;Hardware > Impresora;Alta;Resueltas;2025-05-01 09:00;2025-05-01 11:30;No;Juan Pérez;Dr. García;IMP-001;INC_ALTO;5
2;Instalación software médico;Requerimiento;Software > Aplicación;Mediana;Cerrado;2025-05-02 14:00;2025-05-03 10:00;Si;Ana López;Enfermera Silva;;REQ_MEDIO;4
3;Red lenta en urgencias;Incidencia;Red > Conectividad;Alta;En curso (asignada);2025-05-03 16:00;;No;Carlos Ruiz;Dr. Martínez;SW-005;INC_ALTO;
4;Actualización sistema HIS;Requerimiento;Software > Sistema;Alta;Resueltas;2025-05-04 08:00;2025-05-04 18:00;No;Juan Pérez;Administración;SRV-MED;REQ_ALTO;5
5;Mantenimiento PCs recepción;Incidencia;Hardware > Computador;Baja;Cerrado;2025-05-05 13:00;2025-05-05 15:00;No;Ana López;Recepción;PC-003;INC_BAJO;3
EOF
        print_success "CSV básico creado"
    fi
}

# Función para crear scripts de inicio
create_startup_scripts() {
    print_status "Creando scripts de inicio..."
    
    # Script para Unix/Linux/macOS
    cat > "$PROJECT_DIR/start.sh" << EOF
#!/bin/bash
# Script de inicio para Dashboard IT - Clínica Bonsana

cd "\$(dirname "\$0")"

# Activar entorno virtual
source venv/bin/activate

# Verificar configuración
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('🔍 Verificando configuración...')
if not os.getenv('GOOGLE_AI_API_KEY'):
    print('⚠️  GOOGLE_AI_API_KEY no configurada')
    print('   Edita el archivo .env para agregar tu API Key')
else:
    print('✅ API Key configurada')

print('🚀 Iniciando Dashboard IT...')
"

# Iniciar aplicación
echo "Dashboard disponible en: http://localhost:5000"
python app.py
EOF
    
    chmod +x "$PROJECT_DIR/start.sh"
    
    # Script para Windows
    cat > "$PROJECT_DIR/start.bat" << 'EOF'
@echo off
echo 🏥 Dashboard IT - Clínica Bonsana
echo Iniciando aplicación...

cd /d "%~dp0"

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Verificar configuración
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('⚠️  Configura GOOGLE_AI_API_KEY en .env' if not os.getenv('GOOGLE_AI_API_KEY') else '✅ Configuración OK')"

REM Iniciar aplicación
echo Dashboard disponible en: http://localhost:5000
python app.py

pause
EOF
    
    print_success "Scripts de inicio creados"
}

# Función para probar la instalación
test_installation() {
    print_status "Probando instalación..."
    
    # Activar entorno virtual
    source "$VENV_DIR/bin/activate"
    
    # Probar importaciones
    python -c "
import sys
import flask
import pandas
import google.generativeai
from app import TicketAnalyzer

print('✅ Todas las importaciones exitosas')
print(f'Python: {sys.version}')
print(f'Flask: {flask.__version__}')
print(f'Pandas: {pandas.__version__}')
"
    
    # Probar carga de datos
    python -c "
from app import TicketAnalyzer
analyzer = TicketAnalyzer()
metrics = analyzer.get_overall_metrics()
print(f'✅ Datos cargados: {metrics[\"total_tickets\"]} tickets')
"
    
    print_success "Instalación probada exitosamente"
}

# Función para configurar API Key interactivamente
configure_api_key() {
    print_status "Configuración de Google AI Studio..."
    
    echo ""
    echo "Para usar la funcionalidad de IA necesitas una API Key de Google AI Studio:"
    echo "1. Visita: https://makersuite.google.com/app/apikey"
    echo "2. Inicia sesión con tu cuenta de Google"
    echo "3. Crea una nueva API Key"
    echo "4. Copia la API Key generada"
    echo ""
    
    read -p "¿Tienes una API Key de Google AI Studio? (s/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        echo ""
        read -p "Ingresa tu API Key: " API_KEY
        
        if [ ! -z "$API_KEY" ]; then
            # Actualizar .env
            sed -i.bak "s/GOOGLE_AI_API_KEY=.*/GOOGLE_AI_API_KEY=$API_KEY/" "$PROJECT_DIR/.env"
            print_success "API Key configurada"
            
            # Probar API Key
            source "$VENV_DIR/bin/activate"
            python -c "
import os
from dotenv import load_dotenv
load_dotenv()

try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))
    models = list(genai.list_models())
    print(f'✅ API Key válida ({len(models)} modelos disponibles)')
except Exception as e:
    print(f'❌ Error con API Key: {e}')
"
        else
            print_warning "API Key vacía. Puedes configurarla después en el archivo .env"
        fi
    else
        print_warning "Sin API Key. La funcionalidad IA estará deshabilitada."
        echo "Puedes configurarla después editando el archivo .env"
    fi
}

# Función para mostrar resumen final
show_completion_summary() {
    print_header
    print_success "¡INSTALACIÓN COMPLETADA EXITOSAMENTE!"
    echo ""
    echo "📂 Ubicación del proyecto: $PROJECT_DIR"
    echo "🐍 Entorno virtual: $VENV_DIR"
    echo "📊 Datos de muestra: $DATA_DIR/glpi.csv"
    echo "⚙️  Configuración: $PROJECT_DIR/.env"
    echo ""
    echo "🚀 PARA INICIAR EL DASHBOARD:"
    echo ""
    if [[ "$OS" == "windows" ]]; then
        echo "   Windows: Ejecuta start.bat"
    else
        echo "   Unix/Linux/macOS: ./start.sh"
    fi
    echo "   O manualmente:"
    echo "     source venv/bin/activate"
    echo "     python app.py"
    echo ""
    echo "🌐 ACCESO AL DASHBOARD:"
    echo "   http://localhost:5000"
    echo ""
    echo "🤖 CONFIGURACIÓN IA:"
    if grep -q "GOOGLE_AI_API_KEY=$" "$PROJECT_DIR/.env"; then
        echo "   ⚠️  Configura tu API Key en el archivo .env"
        echo "   Edita la línea: GOOGLE_AI_API_KEY=tu-api-key-aqui"
    else
        echo "   ✅ API Key configurada"
    fi
    echo ""
    echo "📚 DOCUMENTACIÓN:"
    echo "   README.md - Información general"
    echo "   AI_TROUBLESHOOTING.md - Solución de problemas IA"
    echo ""
    echo "🛠️  HERRAMIENTAS ÚTILES:"
    echo "   python ai_utils.py status    # Verificar estado IA"
    echo "   python ai_utils.py test      # Probar análisis IA"
    echo "   python setup_ai.py          # Configuración automática IA"
    echo ""
    print_success "¡Disfruta usando el Dashboard IT con IA!"
}

# Función principal
main() {
    print_header
    
    print_status "Iniciando instalación rápida..."
    echo "Directorio del proyecto: $PROJECT_DIR"
    echo ""
    
    # Verificar prerrequisitos
    detect_os
    check_python_version
    
    # Instalar dependencias del sistema (opcional)
    if [[ "$OS" != "windows" && "$OS" != "unknown" ]]; then
        read -p "¿Instalar dependencias del sistema? (s/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[SsYy]$ ]]; then
            install_system_dependencies
        fi
    fi
    
    # Crear entorno virtual e instalar dependencias
    create_virtual_environment
    install_python_dependencies
    
    # Configurar proyecto
    create_directories
    setup_environment_file
    generate_sample_data
    create_startup_scripts
    
    # Probar instalación
    test_installation
    
    # Configurar API Key
    configure_api_key
    
    # Mostrar resumen
    show_completion_summary
}

# Función para mostrar ayuda
show_help() {
    echo "Dashboard IT - Clínica Bonsana - Instalación Rápida"
    echo ""
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Opciones:"
    echo "  -h, --help     Mostrar esta ayuda"
    echo "  --no-deps      No instalar dependencias del sistema"
    echo "  --no-api       No configurar API Key interactivamente"
    echo "  --uninstall    Desinstalar completamente"
    echo ""
    echo "Este script instala automáticamente:"
    echo "  • Entorno virtual de Python"
    echo "  • Dependencias del proyecto"
    echo "  • Configuración básica"
    echo "  • Datos de muestra"
    echo "  • Scripts de inicio"
    echo ""
}

# Función para desinstalar
uninstall() {
    print_status "Desinstalando Dashboard IT..."
    
    read -p "¿Estás seguro? Esto eliminará el entorno virtual y datos generados (s/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        rm -rf "$VENV_DIR"
        rm -f "$PROJECT_DIR/.env"
        rm -f "$PROJECT_DIR/start.sh"
        rm -f "$PROJECT_DIR/start.bat"
        rm -rf "$LOGS_DIR"
        
        print_success "Desinstalación completada"
        print_warning "Los datos en $DATA_DIR se mantuvieron"
    else
        print_status "Desinstalación cancelada"
    fi
}

# Procesar argumentos de línea de comandos
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --no-deps)
            SKIP_DEPS=true
            shift
            ;;
        --no-api)
            SKIP_API=true
            shift
            ;;
        --uninstall)
            uninstall
            exit 0
            ;;
        *)
            print_error "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Verificar que estamos en el directorio correcto
if [ ! -f "$PROJECT_DIR/app.py" ]; then
    print_error "No se encontró app.py. Ejecuta este script desde el directorio del proyecto."
    exit 1
fi

# Ejecutar instalación principal
main

exit 0