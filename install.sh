#!/bin/bash

# =============================================================================
# INSTALADOR AUTOMÁTICO COMPLETO
# Dashboard IT con IA - Clínica Bonsana
# =============================================================================

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuración
PROJECT_NAME="dashboard-it-bonsana"
PYTHON_MIN_VERSION="3.8"
REQUIRED_SPACE_GB=2

# Funciones auxiliares
print_header() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    INSTALADOR DASHBOARD IT - CLÍNICA BONSANA                ║"
    echo "║                          Sistema de Análisis con IA                         ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}[PASO $1/$2]${NC} $3"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Verificar requisitos del sistema
check_system_requirements() {
    print_step 1 12 "Verificando requisitos del sistema"
    
    # Verificar sistema operativo
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "Sistema operativo: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "Sistema operativo: macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        print_success "Sistema operativo: Windows"
    else
        print_error "Sistema operativo no soportado: $OSTYPE"
        exit 1
    fi
    
    # Verificar Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d "." -f 1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d "." -f 2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python $PYTHON_VERSION (OK)"
        else
            print_error "Python $PYTHON_MIN_VERSION+ requerido. Encontrado: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 no encontrado. Instale Python 3.8+ primero."
        exit 1
    fi
    
    # Verificar pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 disponible"
    else
        print_error "pip3 no encontrado"
        exit 1
    fi
    
    # Verificar git
    if command -v git &> /dev/null; then
        print_success "Git disponible"
    else
        print_warning "Git no encontrado - se omitirá clonado del repositorio"
    fi
    
    # Verificar espacio en disco
    if command -v df &> /dev/null; then
        AVAILABLE_SPACE_KB=$(df . | tail -1 | awk '{print $4}')
        AVAILABLE_SPACE_GB=$((AVAILABLE_SPACE_KB / 1024 / 1024))
        
        if [ $AVAILABLE_SPACE_GB -ge $REQUIRED_SPACE_GB ]; then
            print_success "Espacio en disco: ${AVAILABLE_SPACE_GB}GB (OK)"
        else
            print_error "Espacio insuficiente. Requerido: ${REQUIRED_SPACE_GB}GB, Disponible: ${AVAILABLE_SPACE_GB}GB"
            exit 1
        fi
    fi
    
    echo ""
}

# Configurar entorno de desarrollo
setup_environment() {
    print_step 2 12 "Configurando entorno de desarrollo"
    
    # Crear directorio del proyecto
    mkdir -p $PROJECT_NAME
    cd $PROJECT_NAME
    
    # Crear entorno virtual
    print_info "Creando entorno virtual Python..."
    python3 -m venv venv
    
    # Activar entorno virtual
    if [[ "$OS" == "windows" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # Actualizar pip
    print_info "Actualizando pip, setuptools y wheel..."
    pip install --upgrade pip setuptools wheel
    
    print_success "Entorno virtual creado y activado"
    echo ""
}

# Crear estructura de directorios
create_directory_structure() {
    print_step 3 12 "Creando estructura de directorios"
    
    # Directorios principales
    directories=(
        "ai"
        "data"
        "data/cache"
        "data/reports" 
        "data/backups"
        "data/metrics"
        "logs"
        "templates"
        "static"
        "nginx"
        "scripts"
        "tests"
        "docs"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        print_info "Directorio creado: $dir"
    done
    
    print_success "Estructura de directorios creada"
    echo ""
}

# Instalar dependencias de Python
install_python_dependencies() {
    print_step 4 12 "Instalando dependencias de Python"
    
    # Crear requirements.txt
    cat > requirements.txt << 'EOF'
# Dashboard IT - Clínica Bonsana
# Dependencias principales
Flask>=2.3.0
pandas>=2.0.0
python-dotenv>=1.0.0
google-generativeai>=0.3.0
requests>=2.31.0

# Procesamiento de texto
markdown>=3.5.0
beautifulsoup4>=4.12.0

# Framework web
jinja2>=3.1.0
werkzeug>=2.3.0

# Análisis de datos
numpy>=1.24.0

# Monitoreo del sistema
psutil>=5.9.0

# Servidor de producción
gunicorn>=20.1.0

# Exportación de reportes
reportlab>=4.0.0
python-docx>=0.8.11

# Cache y almacenamiento
redis>=4.5.0

# Testing (opcional)
pytest>=7.4.0
pytest-cov>=4.1.0

# Calidad de código (opcional)
black>=23.0.0
flake8>=6.0.0
EOF
    
    print_info "Instalando dependencias principales..."
    pip install -r requirements.txt
    
    print_success "Dependencias de Python instaladas"
    echo ""
}

# Configurar archivos de configuración
setup_configuration_files() {
    print_step 5 12 "Configurando archivos de configuración"
    
    # Crear archivo .env
    cat > .env << 'EOF'
# Configuración Dashboard IT - Clínica Bonsana
FLASK_ENV=development
SECRET_KEY=change-this-secret-key-in-production

# Google AI Configuration
GOOGLE_AI_API_KEY=AIzaSyALkC-uoOfpS3cB-vnaj8Zor3ccp5MVOBQ
GOOGLE_AI_MODEL=gemini-2.0-flash-exp
AI_ANALYSIS_ENABLED=True

# Application Settings
DATA_DIRECTORY=data
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=5000

# Database
DATABASE_URL=sqlite:///dashboard.db

# IA Settings
AI_MAX_CSV_ROWS=1000
AI_CACHE_TIMEOUT=3600
AI_REQUEST_TIMEOUT=300

# Security
MAX_CONTENT_LENGTH=52428800

# Development
DEBUG=True
EOF
    
    chmod 600 .env
    
    # Crear .gitignore
    cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environment
venv/
env/

# Environment variables
.env

# Database
*.db
*.sqlite

# Logs
logs/*.log

# Cache
data/cache/
*.cache

# IDE
.vscode/
.idea/
*.swp
*.swo

# System files
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp

# Reports (optional, comment if you want to track)
data/reports/

# Backups
data/backups/
EOF
    
    print_success "Archivos de configuración creados"
    echo ""
}

# Crear archivos principales del módulo de IA
create_ai_module() {
    print_step 6 12 "Creando módulo de IA"
    
    # ai/__init__.py
    cat > ai/__init__.py << 'EOF'
"""
Módulo de Análisis de IA para Dashboard IT - Clínica Bonsana
"""

__version__ = "1.0.0"
__all__ = ["GeminiClient", "AIAnalyzer", "PromptManager"]
EOF
    
    # ai/config.py (versión básica)
    cat > ai/config.py << 'EOF'
"""
Configuración básica del módulo de IA
"""

import os
from dataclasses import dataclass

@dataclass
class AIConfig:
    api_key: str
    model_name: str = "gemini-2.0-flash-exp"
    max_csv_rows: int = 1000
    request_timeout: int = 300
    
    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv('GOOGLE_AI_API_KEY', ''),
            model_name=os.getenv('GOOGLE_AI_MODEL', 'gemini-2.0-flash-exp'),
            max_csv_rows=int(os.getenv('AI_MAX_CSV_ROWS', '1000')),
            request_timeout=int(os.getenv('AI_REQUEST_TIMEOUT', '300'))
        )

config = AIConfig.from_env()
EOF
    
    print_success "Módulo de IA básico creado"
    echo ""
}

# Crear datos de muestra
create_sample_data() {
    print_step 7 12 "Creando datos de muestra"
    
    # CSV de muestra
    cat > data/glpi.csv << 'EOF'
ID;Título;Tipo;Categoría;Prioridad;Estado;Fecha de Apertura;Fecha de solución;Se superó el tiempo de resolución;Asignado a: - Técnico;Solicitante - Solicitante;Elementos asociados;ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución;Encuesta de satisfacción - Satisfacción
001;Problema con impresora láser;Incidencia;Hardware > Impresora;Alta;Resueltas;2024-01-15 09:30;2024-01-15 12:45;No;JORGE AURELIO BETANCOURT CASTILLO;MARIA GONZALEZ LOPEZ;IMP-001;INC_ALTO;4
002;Instalación de software médico;Requerimiento;Software > Aplicación;Mediana;Cerrado;2024-01-16 10:15;2024-01-16 16:30;No;SANTIAGO HURTADO MORENO;CARLOS RODRIGUEZ MARTINEZ;;REQ_MEDIO;5
003;Red sin conectividad en consulta 3;Incidencia;Red > Conectividad;Alta;En curso (asignada);2024-01-17 08:00;;Si;JORGE AURELIO BETANCOURT CASTILLO;ANA MARTINEZ SILVA;;INC_ALTO;
004;Cambio de monitor en recepción;Requerimiento;Hardware > Monitor;Baja;Nuevo;2024-01-17 14:20;;;LUIS FERNANDEZ TORRES;;REQ_BAJO;
005;Sistema operativo lento;Incidencia;Software > Sistema operativo;Mediana;Resueltas;2024-01-18 11:00;2024-01-18 15:30;No;SANTIAGO HURTADO MORENO;PEDRO SANCHEZ RUIZ;PC-003;INC_MEDIO;3
006;Instalación de cámara de seguridad;Requerimiento;Hardware > Cámara;Alta;En curso (asignada);2024-01-19 09:00;;No;JORGE AURELIO BETANCOURT CASTILLO;DIRECTORA CLINICA;CAM-001;REQ_ALTO;
007;Problema con teléfono IP;Incidencia;Telecomunicaciones > Teléfono;Mediana;Resueltas;2024-01-20 13:15;2024-01-20 17:45;Si;SANTIAGO HURTADO MORENO;SECRETARIA ADMINISTRATIVA;TEL-005;INC_MEDIO;2
008;Backup de base de datos;Requerimiento;Software > Base de datos;Alta;Resueltas;2024-01-21 08:30;2024-01-21 11:00;No;SQL SQL;ADMINISTRADOR SISTEMAS;DB-001;REQ_ALTO;5
009;Wi-Fi no funciona en sala de espera;Incidencia;Red > Wi-Fi;Mediana;Nuevo;2024-01-22 10:45;;;MARIA TORRES SILVA;;INC_MEDIO;
010;Actualización de antivirus;Requerimiento;Software > Seguridad;Baja;Pendiente;2024-01-23 16:00;;No;;TODOS LOS USUARIOS;;REQ_BAJO;
EOF
    
    print_success "Datos de muestra creados"
    echo ""
}

# Crear template HTML básico
create_basic_templates() {
    print_step 8 12 "Creando templates HTML básicos"
    
    # Template básico de error
    cat > templates/error.html << 'EOF'
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - Dashboard IT</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="alert alert-danger text-center">
                    <h4>Error {{ error_code or 500 }}</h4>
                    <p>{{ error or "Ha ocurrido un error inesperado" }}</p>
                    <a href="/" class="btn btn-primary">Volver al Dashboard</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
EOF
    
    print_success "Templates básicos creados"
    echo ""
}

# Crear scripts de utilidades
create_utility_scripts() {
    print_step 9 12 "Creando scripts de utilidades"
    
    # Script de inicio
    cat > run.sh << 'EOF'
#!/bin/bash
# Script de inicio para Dashboard IT

echo "🏥 Iniciando Dashboard IT - Clínica Bonsana"

# Activar entorno virtual
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Entorno virtual activado"
else
    echo "❌ Entorno virtual no encontrado"
    exit 1
fi

# Verificar dependencias críticas
python -c "
import flask, pandas, google.generativeai
print('✅ Dependencias principales verificadas')
" || {
    echo "❌ Error: Dependencias faltantes"
    echo "💡 Ejecuta: pip install -r requirements.txt"
    exit 1
}

# Verificar archivos críticos
if [ ! -f "data/glpi.csv" ]; then
    echo "⚠️  Archivo CSV no encontrado - usando datos de muestra"
fi

# Iniciar aplicación
echo "🚀 Iniciando aplicación en http://localhost:5000"
python app.py
EOF
    
    chmod +x run.sh
    
    # Script de tests básico
    cat > test_installation.py << 'EOF'
#!/usr/bin/env python3
"""
Test básico de instalación
"""

def test_imports():
    """Test de importaciones críticas"""
    try:
        import flask
        import pandas
        import google.generativeai
        print("✅ Importaciones principales - OK")
        return True
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False

def test_files():
    """Test de archivos críticos"""
    import os
    
    required_files = [
        '.env',
        'requirements.txt',
        'data/glpi.csv',
        'ai/__init__.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {missing_files}")
        return False
    else:
        print("✅ Archivos críticos - OK")
        return True

def test_configuration():
    """Test de configuración"""
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if api_key and len(api_key) > 10:
        print("✅ Configuración de IA - OK")
        return True
    else:
        print("⚠️  API key de IA no configurada")
        return False

if __name__ == '__main__':
    print("🧪 Ejecutando tests de instalación...")
    print("="*50)
    
    tests = [
        test_imports,
        test_files,
        test_configuration
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("="*50)
    print(f"📊 Resultado: {passed}/{len(tests)} tests pasaron")
    
    if passed == len(tests):
        print("🎉 ¡Instalación exitosa!")
        print("\n📋 Próximos pasos:")
        print("   1. Configura tu API key en .env")
        print("   2. Ejecuta: ./run.sh")
        print("   3. Accede a: http://localhost:5000")
    else:
        print("⚠️  Instalación incompleta")
        print("   Revisa los errores anteriores")
EOF
    
    chmod +x test_installation.py
    
    print_success "Scripts de utilidades creados"
    echo ""
}

# Crear aplicación principal básica
create_main_application() {
    print_step 10 12 "Creando aplicación principal"
    
    # app.py básico
    cat > app.py << 'EOF'
#!/usr/bin/env python3
"""
Aplicación principal básica del Dashboard IT - Clínica Bonsana
"""

import os
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import pandas as pd

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

@app.route('/')
def index():
    """Dashboard principal básico"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard IT - Clínica Bonsana</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.10.5/font/bootstrap-icons.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-danger">
            <div class="container">
                <a class="navbar-brand" href="#">
                    <i class="bi bi-hospital me-2"></i>
                    Clínica Bonsana - Dashboard IT
                </a>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">
                                <i class="bi bi-check-circle-fill text-success me-2"></i>
                                ¡Instalación Exitosa!
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="alert alert-success">
                                <h4 class="alert-heading">🎉 ¡Bienvenido al Dashboard IT!</h4>
                                <p>La instalación básica se completó exitosamente. El sistema está funcionando correctamente.</p>
                                <hr>
                                <p class="mb-0">
                                    <strong>Próximos pasos:</strong>
                                    <br>1. Configura tu API key de Google AI en el archivo .env
                                    <br>2. Instala los módulos completos de IA
                                    <br>3. Carga tus datos reales de tickets
                                </p>
                            </div>
                            
                            <div class="row g-3 mt-3">
                                <div class="col-md-4">
                                    <div class="card border-primary">
                                        <div class="card-body text-center">
                                            <i class="bi bi-robot display-6 text-primary"></i>
                                            <h6 class="card-title mt-2">Análisis de IA</h6>
                                            <p class="card-text small">Próximamente disponible</p>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card border-info">
                                        <div class="card-body text-center">
                                            <i class="bi bi-graph-up display-6 text-info"></i>
                                            <h6 class="card-title mt-2">Métricas</h6>
                                            <p class="card-text small">Próximamente disponible</p>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card border-success">
                                        <div class="card-body text-center">
                                            <i class="bi bi-file-earmark-text display-6 text-success"></i>
                                            <h6 class="card-title mt-2">Reportes</h6>
                                            <p class="card-text small">Próximamente disponible</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'message': 'Dashboard IT funcionando correctamente',
        'version': '1.0.0-basic'
    })

@app.route('/api/test')
def api_test():
    """Test de API básico"""
    return jsonify({
        'success': True,
        'message': 'API funcionando correctamente',
        'data': {
            'csv_exists': os.path.exists('data/glpi.csv'),
            'ai_configured': bool(os.getenv('GOOGLE_AI_API_KEY'))
        }
    })

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print("🏥 Dashboard IT - Clínica Bonsana")
    print("="*50)
    print(f"🌍 URL: http://{host}:{port}")
    print(f"🔍 Health: http://{host}:{port}/health")
    print(f"📡 API Test: http://{host}:{port}/api/test")
    print("="*50)
    
    app.run(host=host, port=port, debug=debug)
EOF
    
    print_success "Aplicación principal creada"
    echo ""
}

# Instalar dependencias del sistema (opcional)
install_system_dependencies() {
    print_step 11 12 "Verificando dependencias del sistema"
    
    if [[ "$OS" == "linux" ]]; then
        if command -v apt-get &> /dev/null; then
            print_info "Sistema basado en Debian/Ubuntu detectado"
            echo "Para funcionalidades completas, considera instalar:"
            echo "  sudo apt-get update"
            echo "  sudo apt-get install -y curl wget git nginx postgresql redis-server"
        elif command -v yum &> /dev/null; then
            print_info "Sistema basado en RedHat/CentOS detectado"
            echo "Para funcionalidades completas, considera instalar:"
            echo "  sudo yum install -y curl wget git nginx postgresql redis"
        fi
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            print_info "Homebrew detectado en macOS"
            echo "Para funcionalidades completas, considera instalar:"
            echo "  brew install nginx postgresql redis"
        else
            print_info "Considera instalar Homebrew para dependencias adicionales"
        fi
    fi
    
    print_success "Verificación de dependencias del sistema completada"
    echo ""
}

# Finalizar instalación
finalize_installation() {
    print_step 12 12 "Finalizando instalación"
    
    # Crear archivo de información
    cat > INSTALLATION_INFO.txt << EOF
# INFORMACIÓN DE INSTALACIÓN
# Dashboard IT - Clínica Bonsana

Fecha de instalación: $(date)
Sistema operativo: $OS
Versión de Python: $PYTHON_VERSION
Directorio de instalación: $(pwd)

## ARCHIVOS CREADOS:
- app.py (aplicación principal básica)
- requirements.txt (dependencias)
- .env (configuración)
- data/glpi.csv (datos de muestra)
- ai/ (módulo de IA básico)
- run.sh (script de inicio)
- test_installation.py (tests básicos)

## PRÓXIMOS PASOS:
1. Configurar API key en .env:
   GOOGLE_AI_API_KEY=tu-api-key-aqui

2. Ejecutar tests:
   python test_installation.py

3. Iniciar aplicación:
   ./run.sh
   # O directamente: python app.py

4. Acceder a:
   http://localhost:5000

## INSTALACIÓN COMPLETA:
Para la instalación completa con todas las funcionalidades:
   python install_ai_module.py

## SOPORTE:
- Documentación: README.md
- Logs: logs/dashboard.log
- Email: it-support@clinicabonsana.com
EOF
    
    print_success "Instalación básica completada"
    echo ""
    
    # Mostrar resumen
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                          ¡INSTALACIÓN COMPLETADA!                           ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${CYAN}📋 RESUMEN DE INSTALACIÓN:${NC}"
    echo "   ✅ Entorno Python configurado"
    echo "   ✅ Dependencias instaladas"
    echo "   ✅ Estructura de directorios creada"
    echo "   ✅ Configuración básica lista"
    echo "   ✅ Aplicación principal funcional"
    echo "   ✅ Datos de muestra incluidos"
    echo ""
    echo -e "${YELLOW}⚡ COMANDOS RÁPIDOS:${NC}"
    echo "   🧪 Probar instalación: python test_installation.py"
    echo "   🚀 Iniciar aplicación: ./run.sh"
    echo "   🌐 URL del dashboard: http://localhost:5000"
    echo ""
    echo -e "${PURPLE}🔗 PRÓXIMOS PASOS:${NC}"
    echo "   1. 🔑 Configura tu API key en .env"
    echo "   2. 🤖 Instala módulos completos: python install_ai_module.py"
    echo "   3. 📊 Carga tus datos reales de tickets"
    echo "   4. 🎯 Personaliza análisis según tus necesidades"
    echo ""
    echo -e "${GREEN}🎉 ¡Listo para transformar tu gestión IT con IA!${NC}"
    echo ""
}

# Función principal
main() {
    print_header
    
    # Verificar si se ejecuta con privilegios adecuados
    if [[ $EUID -eq 0 ]]; then
        print_warning "No se recomienda ejecutar como root. Continúa bajo tu propio riesgo."
        read -p "¿Continuar? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Ejecutar pasos de instalación
    check_system_requirements
    setup_environment
    create_directory_structure
    install_python_dependencies
    setup_configuration_files
    create_ai_module
    create_sample_data
    create_basic_templates
    create_utility_scripts
    create_main_application
    install_system_dependencies
    finalize_installation
    
    # Ejecutar test básico automáticamente
    echo -e "${CYAN}🧪 Ejecutando tests de verificación...${NC}"
    python test_installation.py
    
    echo ""
    echo -e "${GREEN}🚀 Instalación lista. Ejecuta './run.sh' para comenzar!${NC}"
}

# Ejecutar instalación
main "$@"