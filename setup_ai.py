#!/usr/bin/env python3
"""
Script de configuración e instalación del módulo de IA
Dashboard IT - Clínica Bonsana
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json

def print_header():
    """Imprime el header del script"""
    print("="*60)
    print("    CONFIGURACIÓN MÓDULO DE IA")
    print("    Dashboard IT - Clínica Bonsana")
    print("="*60)
    print()

def check_python_version():
    """Verifica la versión de Python"""
    print("🐍 Verificando versión de Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def create_directories():
    """Crea directorios necesarios"""
    print("\n📁 Creando directorios necesarios...")
    
    directories = [
        'ai',
        'data',
        'data/reports',
        'logs',
        'templates',
        'static'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ {directory}/")
    
    return True

def install_dependencies():
    """Instala dependencias de Python"""
    print("\n📦 Instalando dependencias...")
    
    dependencies = [
        "flask>=2.3.0",
        "pandas>=2.0.0",
        "python-dotenv>=1.0.0",
        "google-generativeai>=0.3.0",
        "markdown>=3.5.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0"
    ]
    
    try:
        for dep in dependencies:
            print(f"   📥 Instalando {dep}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], check=True, capture_output=True)
        
        print("✅ Todas las dependencias instaladas exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {e}")
        return False

def setup_environment():
    """Configura archivo de entorno"""
    print("\n🔧 Configurando archivo de entorno...")
    
    env_content = """# Configuración del Dashboard IT - Clínica Bonsana
# Configuración de Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this

# Configuración de datos
DATA_DIRECTORY=data
CSV_ENCODING=utf-8

# Configuración de Google AI Studio
GOOGLE_AI_API_KEY=AIzaSyALkC-uoOfpS3cB-vnaj8Zor3ccp5MVOBQ
GOOGLE_AI_MODEL=gemini-2.0-flash-exp
AI_ANALYSIS_ENABLED=True

# Configuración avanzada de IA
AI_MAX_CSV_ROWS=1000
AI_CACHE_TIMEOUT=3600
AI_RETRY_ATTEMPTS=3
AI_REQUEST_TIMEOUT=300

# Configuración de logs
LOG_LEVEL=INFO
LOG_FILE=logs/dashboard.log

# Configuración de cache
CACHE_TIMEOUT=300

# Configuración de reportes
REPORTS_DIRECTORY=data/reports
EXPORT_PDF_ENABLED=True
EXPORT_WORD_ENABLED=True

# Configuración de límites
MAX_ANALYSIS_SIZE_MB=50
MAX_CONCURRENT_ANALYSES=3
"""

    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("   ✅ Archivo .env creado")
    else:
        print("   ⚠️  Archivo .env ya existe, no se modificó")
    
    return True

def create_sample_data():
    """Crea datos de muestra si no existen"""
    print("\n📊 Verificando datos de muestra...")
    
    csv_path = "data/glpi.csv"
    
    if not os.path.exists(csv_path):
        print("   📝 Creando archivo CSV de muestra...")
        
        # Importar y usar la función de generación del utils.py
        try:
            from utils import generate_sample_csv
            generate_sample_csv(csv_path, num_records=100)
            print("   ✅ Archivo CSV de muestra creado")
        except ImportError:
            print("   ⚠️  No se pudo crear CSV de muestra (utils.py no encontrado)")
            # Crear CSV básico manualmente
            create_basic_csv(csv_path)
    else:
        print("   ✅ Archivo CSV ya existe")
    
    return True

def create_basic_csv(csv_path):
    """Crea un CSV básico de muestra"""
    csv_content = """ID;Título;Tipo;Categoría;Prioridad;Estado;Fecha de Apertura;Fecha de solución;Se superó el tiempo de resolución;Asignado a: - Técnico;Solicitante - Solicitante;Elementos asociados;ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución;Encuesta de satisfacción - Satisfacción
001;Problema con impresora;Incidencia;Hardware > Impresora;Alta;Resueltas;2024-01-15 09:30;2024-01-15 12:45;No;JORGE AURELIO BETANCOURT CASTILLO;MARIA GONZALEZ;IMP-001;INC_ALTO;4
002;Instalación de software;Requerimiento;Software > Aplicación;Mediana;Cerrado;2024-01-16 10:15;2024-01-16 16:30;No;SANTIAGO HURTADO MORENO;CARLOS RODRIGUEZ;;REQ_MEDIO;5
003;Red sin conectividad;Incidencia;Red > Conectividad;Alta;En curso (asignada);2024-01-17 08:00;;Si;JORGE AURELIO BETANCOURT CASTILLO;ANA MARTINEZ;;INC_ALTO;
004;Cambio de monitor;Requerimiento;Hardware > Monitor;Baja;Nuevo;2024-01-17 14:20;;;LUIS FERNANDEZ;;REQ_BAJO;
005;Sistema lento;Incidencia;Software > Sistema operativo;Mediana;Resueltas;2024-01-18 11:00;2024-01-18 15:30;No;SANTIAGO HURTADO MORENO;PEDRO SANCHEZ;PC-003;INC_MEDIO;3
"""
    
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write(csv_content)
    
    print("   ✅ CSV básico creado")

def test_ai_connection():
    """Prueba la conexión con la API de IA"""
    print("\n🤖 Probando conexión con IA...")
    
    try:
        # Importar y probar conexión
        from ai.gemini_client import GeminiClient
        
        client = GeminiClient()
        result = client.test_connection()
        
        if result.get('success', False):
            print("   ✅ Conexión con IA exitosa")
            print(f"   🧠 Modelo: {result.get('model', 'N/A')}")
            return True
        else:
            print(f"   ❌ Error de conexión: {result.get('error', 'Error desconocido')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error al probar IA: {str(e)}")
        print("   💡 Verifica que la API key sea válida")
        return False

def create_startup_script():
    """Crea script de inicio"""
    print("\n🚀 Creando script de inicio...")
    
    startup_content = """#!/usr/bin/env python3
\"\"\"
Script de inicio para Dashboard IT con IA
\"\"\"

import os
import sys
from app import create_app

if __name__ == '__main__':
    # Verificar que el módulo de IA esté disponible
    try:
        from ai.analyzer import AIAnalyzer
        print("✅ Módulo de IA cargado correctamente")
    except ImportError as e:
        print(f"⚠️  Advertencia: Módulo de IA no disponible: {e}")
    
    # Crear y ejecutar aplicación
    app = create_app()
    
    print("🏥 Iniciando Dashboard IT - Clínica Bonsana")
    print("🌐 Accede a: http://localhost:5000")
    print("🤖 Análisis de IA: http://localhost:5000/ai-analysis")
    print("⏹️  Presiona Ctrl+C para detener")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
"""
    
    with open('run_dashboard.py', 'w') as f:
        f.write(startup_content)
    
    # Hacer ejecutable en sistemas Unix
    if os.name != 'nt':
        os.chmod('run_dashboard.py', 0o755)
    
    print("   ✅ Script de inicio creado: run_dashboard.py")
    return True

def create_readme():
    """Crea documentación README"""
    print("\n📖 Creando documentación...")
    
    readme_content = """# Dashboard IT - Clínica Bonsana
## Análisis Inteligente con IA

### 🚀 Inicio Rápido

1. **Ejecutar el dashboard:**
   ```bash
   python run_dashboard.py
   ```

2. **Acceder a la aplicación:**
   - Dashboard principal: http://localhost:5000
   - Análisis de IA: http://localhost:5000/ai-analysis

### 🤖 Funcionalidades de IA

- **Análisis Exhaustivo Completo**: Evaluación estratégica completa
- **Análisis Rápido**: KPIs principales y insights inmediatos
- **Análisis por Técnico**: Rendimiento individual del equipo
- **Análisis de SLA**: Cumplimiento y optimización
- **Análisis de Tendencias**: Patrones temporales y predicciones
- **Optimización de Costos**: Eficiencia y ROI

### 📊 Tipos de Insights

1. **Rendimiento Actual**: Métricas clave y benchmarking
2. **Análisis Profundo**: Patrones, anomalías y tendencias
3. **Benchmarking Clínico**: Comparación con estándares healthcare
4. **Fortalezas y Debilidades**: Identificación de áreas críticas
5. **Análisis de Riesgos**: Continuidad y vulnerabilidades
6. **Plan de Acción**: Recomendaciones estratégicas

### ⚙️ Configuración

Edita el archivo `.env` para personalizar:

```bash
# API de Google AI
GOOGLE_AI_API_KEY=tu-api-key-aqui
GOOGLE_AI_MODEL=gemini-2.0-flash-exp

# Configuración de análisis
AI_MAX_CSV_ROWS=1000
AI_CACHE_TIMEOUT=3600
```

### 📁 Estructura del Proyecto

```
├── ai/                     # Módulo de IA
│   ├── __init__.py
│   ├── gemini_client.py    # Cliente Google AI
│   ├── prompts.py          # Gestión de prompts
│   └── analyzer.py         # Analizador principal
├── data/                   # Datos y reportes
│   ├── glpi.csv           # Datos de tickets
│   └── reports/           # Reportes generados
├── templates/             # Plantillas HTML
│   ├── index.html         # Dashboard principal
│   └── ai_analysis.html   # Página de IA
├── static/               # Archivos estáticos
├── logs/                 # Archivos de log
└── .env                  # Configuración
```

### 🔧 Solución de Problemas

1. **Error de API Key:**
   - Verifica que la API key de Google AI sea válida
   - Asegúrate de tener créditos disponibles

2. **Error de módulos:**
   ```bash
   pip install -r requirements_ai.txt
   ```

3. **Error de datos:**
   - Verifica que exista el archivo `data/glpi.csv`
   - Ejecuta: `python utils.py generate-sample data/sample.csv`

### 📞 Soporte

Para soporte técnico, contacta al equipo de desarrollo.
"""
    
    with open('README_AI.md', 'w') as f:
        f.write(readme_content)
    
    print("   ✅ Documentación creada: README_AI.md")
    return True

def generate_requirements():
    """Genera archivo de requirements completo"""
    print("\n📋 Generando requirements.txt...")
    
    requirements_content = """# Dashboard IT - Clínica Bonsana
# Dependencias principales
Flask>=2.3.0
pandas>=2.0.0
python-dotenv>=1.0.0

# Análisis de IA
google-generativeai>=0.3.0
markdown>=3.5.0
beautifulsoup4>=4.12.0

# Utilidades
requests>=2.31.0
Jinja2>=3.1.0
Werkzeug>=2.3.0

# Procesamiento de datos
numpy>=1.24.0
python-dateutil>=2.8.0

# Exportación y reportes
reportlab>=4.0.0
fpdf2>=2.7.0
xlsxwriter>=3.1.0

# Opcional: desarrollo
pytest>=7.4.0
black>=23.0.0
flake8>=6.0.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements_content)
    
    print("   ✅ requirements.txt actualizado")
    return True

def main():
    """Función principal del setup"""
    print_header()
    
    steps = [
        ("Verificar Python", check_python_version),
        ("Crear directorios", create_directories),
        ("Instalar dependencias", install_dependencies),
        ("Configurar entorno", setup_environment),
        ("Crear datos de muestra", create_sample_data),
        ("Probar conexión IA", test_ai_connection),
        ("Crear script de inicio", create_startup_script),
        ("Crear documentación", create_readme),
        ("Generar requirements", generate_requirements)
    ]
    
    success_count = 0
    
    for step_name, step_func in steps:
        try:
            if step_func():
                success_count += 1
            else:
                print(f"❌ Falló: {step_name}")
        except Exception as e:
            print(f"❌ Error en {step_name}: {str(e)}")
    
    print("\n" + "="*60)
    print(f"CONFIGURACIÓN COMPLETADA: {success_count}/{len(steps)} pasos exitosos")
    print("="*60)
    
    if success_count == len(steps):
        print("\n🎉 ¡Configuración exitosa!")
        print("\n📋 Próximos pasos:")
        print("   1. Verifica tu API key en .env")
        print("   2. Ejecuta: python run_dashboard.py")
        print("   3. Accede a: http://localhost:5000")
        print("   4. Prueba el análisis de IA: http://localhost:5000/ai-analysis")
    else:
        print("\n⚠️  Configuración incompleta")
        print("   Revisa los errores anteriores y ejecuta el script nuevamente")
    
    print()

if __name__ == '__main__':
    main()