#!/usr/bin/env python3
"""
Instalador completo del módulo de IA para Dashboard IT - Clínica Bonsana
Ejecuta este script para configurar todo automáticamente
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def print_banner():
    """Imprime banner del instalador"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                           INSTALADOR MÓDULO DE IA                           ║
║                         Dashboard IT - Clínica Bonsana                      ║
║                                                                              ║
║  Este script configurará automáticamente el módulo de análisis de IA        ║
║  incluyendo todas las dependencias y archivos necesarios.                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_requirements():
    """Verifica requisitos del sistema"""
    print("🔍 Verificando requisitos del sistema...")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print(f"❌ Error: Se requiere Python 3.8+. Versión actual: {sys.version}")
        return False
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Verificar pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("   ✅ pip disponible")
    except subprocess.CalledProcessError:
        print("   ❌ pip no disponible")
        return False
    
    # Verificar conexión a internet
    try:
        import urllib.request
        urllib.request.urlopen('https://pypi.org', timeout=5)
        print("   ✅ Conexión a internet")
    except Exception:
        print("   ⚠️  Sin conexión a internet (se usarán paquetes locales)")
    
    return True

def create_directory_structure():
    """Crea estructura de directorios"""
    print("\n📁 Creando estructura de directorios...")
    
    directories = [
        'ai',
        'data',
        'data/reports',
        'data/cache',
        'logs',
        'templates',
        'static',
        'tests'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   📂 {directory}/")
    
    print("   ✅ Estructura de directorios creada")
    return True

def install_dependencies():
    """Instala dependencias de Python"""
    print("\n📦 Instalando dependencias de Python...")
    
    dependencies = [
        "flask>=2.3.0",
        "pandas>=2.0.0", 
        "python-dotenv>=1.0.0",
        "google-generativeai>=0.3.0",
        "markdown>=3.5.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "jinja2>=3.1.0",
        "werkzeug>=2.3.0"
    ]
    
    try:
        for i, dep in enumerate(dependencies, 1):
            print(f"   📥 [{i}/{len(dependencies)}] Instalando {dep}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"   ⚠️  Advertencia instalando {dep}: {result.stderr}")
            
        print("   ✅ Dependencias instaladas")
        return True
        
    except Exception as e:
        print(f"   ❌ Error al instalar dependencias: {e}")
        return False

def create_ai_module_files():
    """Crea archivos del módulo de IA"""
    print("\n🤖 Creando archivos del módulo de IA...")
    
    # Lista de archivos a crear (los contenidos se obtuvieron de los artifacts anteriores)
    files_to_create = {
        'ai/__init__.py': '''"""
Módulo de Análisis de IA para Dashboard IT - Clínica Bonsana
"""

from .gemini_client import GeminiClient
from .analyzer import AIAnalyzer
from .prompts import PromptManager

__version__ = "1.0.0"
__all__ = ["GeminiClient", "AIAnalyzer", "PromptManager"]
''',
        
        '.env': '''# Configuración del Dashboard IT - Clínica Bonsana
FLASK_ENV=development
SECRET_KEY=change-this-secret-key-in-production

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

# Configuración de reportes
REPORTS_DIRECTORY=data/reports
EXPORT_PDF_ENABLED=True
EXPORT_WORD_ENABLED=True
''',
        
        'requirements.txt': '''# Dashboard IT - Clínica Bonsana - Módulo de IA
Flask>=2.3.0
pandas>=2.0.0
python-dotenv>=1.0.0
google-generativeai>=0.3.0
markdown>=3.5.0
beautifulsoup4>=4.12.0
requests>=2.31.0
jinja2>=3.1.0
werkzeug>=2.3.0
numpy>=1.24.0
''',
        
        'run_dashboard.py': '''#!/usr/bin/env python3
"""
Script de inicio para Dashboard IT con IA
"""

import os
import sys

def main():
    print("🏥 Dashboard IT - Clínica Bonsana")
    print("🤖 Módulo de IA activado")
    print("="*50)
    
    # Verificar módulo de IA
    try:
        from ai.analyzer import AIAnalyzer
        print("✅ Módulo de IA cargado correctamente")
    except ImportError as e:
        print(f"⚠️  Advertencia: {e}")
    
    # Importar y ejecutar aplicación
    try:
        # Aquí deberías importar tu app principal
        # from app import create_app
        # app = create_app()
        
        print("\\n🌐 Para iniciar el dashboard:")
        print("   1. Implementa tu app.py principal")
        print("   2. Configura las rutas de IA")
        print("   3. Ejecuta: python app.py")
        print("\\n🔗 URLs disponibles:")
        print("   - Dashboard: http://localhost:5000")
        print("   - Análisis IA: http://localhost:5000/ai-analysis")
        
    except ImportError:
        print("\\n📝 Próximos pasos:")
        print("   1. Crea tu archivo app.py principal")
        print("   2. Integra las rutas de IA")
        print("   3. Configura tus templates")

if __name__ == '__main__':
    main()
''',
        
        'README.md': '''# Dashboard IT - Clínica Bonsana
## Módulo de Análisis Inteligente con IA

### 🚀 Inicio Rápido

1. **Configurar el módulo de IA:**
   ```bash
   python install_ai_module.py
   ```

2. **Probar la instalación:**
   ```bash
   python test_ai.py
   ```

3. **Ejecutar el dashboard:**
   ```bash
   python run_dashboard.py
   ```

### 🤖 Características del Módulo de IA

- **Análisis Exhaustivo Completo**: Evaluación estratégica de todo el departamento IT
- **Análisis Rápido**: Insights inmediatos de KPIs principales  
- **Análisis por Técnico**: Rendimiento individual del equipo
- **Análisis de SLA**: Cumplimiento y optimización de acuerdos de servicio
- **Análisis de Tendencias**: Patrones temporales y predicciones
- **Optimización de Costos**: Eficiencia y retorno de inversión

### 📊 Tipos de Insights Generados

1. **Rendimiento Actual**: Métricas clave y benchmarking con la industria
2. **Análisis Profundo**: Patrones ocultos, anomalías y tendencias
3. **Benchmarking Clínico**: Comparación con estándares healthcare
4. **Fortalezas y Debilidades**: Identificación de áreas críticas
5. **Análisis de Riesgos**: Continuidad del servicio y vulnerabilidades
6. **Plan de Acción**: Recomendaciones estratégicas implementables

### ⚙️ Configuración

Edita el archivo `.env`:

```bash
# Tu API key de Google AI
GOOGLE_AI_API_KEY=tu-api-key-aqui

# Modelo a utilizar
GOOGLE_AI_MODEL=gemini-2.0-flash-exp

# Configuración de análisis
AI_MAX_CSV_ROWS=1000
AI_CACHE_TIMEOUT=3600
```

### 📁 Estructura del Proyecto

```
├── ai/                     # Módulo de IA
│   ├── __init__.py
│   ├── config.py          # Configuración avanzada
│   ├── gemini_client.py   # Cliente Google AI
│   ├── analyzer.py        # Analizador principal
│   ├── prompts.py         # Gestión de prompts
│   └── utils.py           # Utilidades
├── data/                  # Datos y reportes
│   ├── glpi.csv          # Datos de tickets
│   ├── reports/          # Reportes generados
│   └── cache/            # Cache de análisis
├── templates/            # Plantillas HTML
│   ├── index.html        # Dashboard principal
│   └── ai_analysis.html  # Página de IA
├── static/              # CSS, JS, imágenes
├── logs/               # Archivos de log
├── .env               # Configuración
└── requirements.txt   # Dependencias
```

### 🔧 Solución de Problemas

1. **Error de API Key:**
   - Obtén una API key válida de Google AI Studio
   - Configúrala en el archivo `.env`

2. **Error de módulos:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Error de datos:**
   - Asegúrate de tener el archivo `data/glpi.csv`
   - Usa el generador de datos de muestra

### 📞 Soporte

Para soporte técnico, consulta la documentación o contacta al equipo de desarrollo.
'''
    }
    
    created_count = 0
    for file_path, content in files_to_create.items():
        try:
            # Crear directorio padre si no existe
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Escribir archivo solo si no existe
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   ✅ {file_path}")
                created_count += 1
            else:
                print(f"   ⏭️  {file_path} (ya existe)")
                
        except Exception as e:
            print(f"   ❌ Error creando {file_path}: {e}")
    
    print(f"   📝 {created_count} archivos creados")
    return True

def create_sample_data():
    """Crea datos de muestra"""
    print("\n📊 Creando datos de muestra...")
    
    csv_path = "data/glpi.csv"
    
    if os.path.exists(csv_path):
        print(f"   ⏭️  {csv_path} ya existe")
        return True
    
    # Crear CSV básico de muestra
    sample_data = """ID;Título;Tipo;Categoría;Prioridad;Estado;Fecha de Apertura;Fecha de solución;Se superó el tiempo de resolución;Asignado a: - Técnico;Solicitante - Solicitante;Elementos asociados;ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución;Encuesta de satisfacción - Satisfacción
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
"""
    
    try:
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(sample_data)
        print(f"   ✅ {csv_path} creado")
        return True
    except Exception as e:
        print(f"   ❌ Error creando {csv_path}: {e}")
        return False

def test_installation():
    """Prueba la instalación"""
    print("\n🧪 Probando instalación...")
    
    # Test 1: Verificar importaciones
    try:
        from ai.config import AIConfig
        from ai.prompts import PromptManager
        print("   ✅ Importaciones de módulos AI exitosas")
    except ImportError as e:
        print(f"   ❌ Error de importación: {e}")
        return False
    
    # Test 2: Verificar configuración
    try:
        config = AIConfig.from_env()
        if config.api_key:
            print("   ✅ API key configurada")
        else:
            print("   ⚠️  API key no configurada (configúrala en .env)")
    except Exception as e:
        print(f"   ❌ Error en configuración: {e}")
        return False
    
    # Test 3: Verificar datos
    if os.path.exists("data/glpi.csv"):
        print("   ✅ Datos de muestra disponibles")
    else:
        print("   ⚠️  No hay datos de muestra")
    
    # Test 4: Verificar prompts
    try:
        prompts = PromptManager.get_available_prompts()
        print(f"   ✅ {len(prompts)} tipos de análisis disponibles")
    except Exception as e:
        print(f"   ❌ Error en prompts: {e}")
        return False
    
    print("   ✅ Instalación verificada")
    return True

def show_next_steps():
    """Muestra pasos siguientes"""
    print("\n" + "="*80)
    print("🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!")
    print("="*80)
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("\n1. 🔑 Configurar API Key:")
    print("   - Obtén tu API key de Google AI Studio: https://makersuite.google.com/app/apikey")
    print("   - Edita el archivo .env y actualiza GOOGLE_AI_API_KEY")
    
    print("\n2. 🧪 Probar el módulo:")
    print("   python test_ai.py")
    
    print("\n3. 📊 Verificar datos:")
    print("   - Revisa el archivo data/glpi.csv")
    print("   - Reemplázalo con tus datos reales si es necesario")
    
    print("\n4. 🚀 Integrar con tu aplicación:")
    print("   - Agrega las rutas de IA a tu app.py")
    print("   - Integra ai_routes.py en tu aplicación Flask")
    print("   - Actualiza tus templates con botones de acceso a IA")
    
    print("\n5. 🌐 Ejecutar:")
    print("   python run_dashboard.py")
    
    print("\n📖 DOCUMENTACIÓN:")
    print("   - README.md: Guía completa de uso")
    print("   - ai/: Código fuente del módulo")
    print("   - templates/ai_analysis.html: Interfaz de IA")
    
    print("\n🔗 URLS DISPONIBLES:")
    print("   - Dashboard principal: http://localhost:5000")
    print("   - Análisis de IA: http://localhost:5000/ai-analysis")
    
    print("\n💡 CONSEJOS:")
    print("   - Mantén actualizada tu API key")
    print("   - Revisa los logs en logs/dashboard.log")
    print("   - Los análisis se guardan en data/reports/")
    
    print("\n📞 SOPORTE:")
    print("   - Ejecuta test_ai.py para diagnosticar problemas")
    print("   - Revisa la documentación en README.md")
    
    print("\n🏥 ¡Listo para analizar el departamento IT de Clínica Bonsana!")

def main():
    """Función principal del instalador"""
    print_banner()
    
    steps = [
        ("Verificar requisitos", check_requirements),
        ("Crear estructura de directorios", create_directory_structure),
        ("Instalar dependencias", install_dependencies),
        ("Crear archivos del módulo de IA", create_ai_module_files),
        ("Crear datos de muestra", create_sample_data),
        ("Probar instalación", test_installation)
    ]
    
    print(f"📅 Iniciando instalación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success_count = 0
    total_steps = len(steps)
    
    for i, (step_name, step_func) in enumerate(steps, 1):
        print(f"\n[{i}/{total_steps}] {step_name}...")
        
        try:
            if step_func():
                success_count += 1
                print(f"     ✅ Completado")
            else:
                print(f"     ❌ Falló")
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    # Mostrar resultados
    print(f"\n{'='*80}")
    print(f"INSTALACIÓN: {success_count}/{total_steps} pasos completados")
    print(f"{'='*80}")
    
    if success_count == total_steps:
        show_next_steps()
        return 0
    else:
        print("\n⚠️  INSTALACIÓN INCOMPLETA")
        print("   Algunos pasos fallaron. Revisa los errores anteriores.")
        print("   Puedes ejecutar el script nuevamente para reintentar.")
        return 1

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        sys.exit(1)