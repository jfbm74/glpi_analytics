#!/usr/bin/env python3
"""
Script de instalación y configuración para Dashboard IT - Clínica Bonsana
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Muestra el banner de instalación"""
    print("=" * 60)
    print("🏥 DASHBOARD IT - CLÍNICA BONSANA")
    print("   Script de Instalación y Configuración")
    print("=" * 60)
    print()

def check_python_version():
    """Verifica la versión de Python"""
    print("🔍 Verificando versión de Python...")
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - OK")
    return True

def create_directory_structure():
    """Crea la estructura de directorios necesaria"""
    print("\n📁 Creando estructura de directorios...")
    
    directories = [
        'data',
        'static',
        'templates',
        'logs',
        'backups'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   ✅ Creado: {directory}/")
        else:
            print(f"   ✓ Existe: {directory}/")

def install_dependencies():
    """Instala las dependencias de Python"""
    print("\n📦 Instalando dependencias...")
    
    try:
        # Verificar si pip está disponible
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        
        # Instalar dependencias
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Dependencias instaladas correctamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {e}")
        return False
    except FileNotFoundError:
        print("❌ Error: pip no encontrado")
        return False

def create_sample_data():
    """Crea archivos de datos de muestra"""
    print("\n📊 Creando archivo de datos de muestra...")
    
    sample_csv_path = "data/sample_glpi.csv"
    
    if os.path.exists(sample_csv_path):
        response = input("   El archivo de muestra ya existe. ¿Sobrescribir? (y/N): ")
        if response.lower() != 'y':
            print("   ✓ Conservando archivo existente")
            return True
    
    try:
        # Usar el generador de datos del utils.py
        from utils import generate_sample_csv
        generate_sample_csv(sample_csv_path, num_records=100)
        print("✅ Archivo de datos de muestra creado")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear archivo de muestra: {e}")
        return False

def create_config_file():
    """Crea archivo de configuración"""
    print("\n⚙️ Creando archivo de configuración...")
    
    config_content = """# Configuración Dashboard IT - Clínica Bonsana

# Configuración del servidor Flask
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

# Configuración de datos
DATA_PATH = 'data'
ALLOWED_EXTENSIONS = ['.csv']

# Configuración de logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/dashboard.log'

# Configuración de la aplicación
APP_NAME = 'Dashboard IT - Clínica Bonsana'
VERSION = '1.0.0'

# Colores corporativos
CORPORATE_COLORS = {
    'primary': '#dc3545',
    'secondary': '#6c757d',
    'success': '#28a745',
    'warning': '#ffc107',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Configuración de métricas
METRICS_CONFIG = {
    'resolved_states': ['Resueltas', 'Cerrado'],
    'incident_types': ['Incidencia'],
    'sla_excellent_threshold': 90,
    'sla_good_threshold': 70,
    'csat_excellent_threshold': 4.0,
    'csat_good_threshold': 3.0
}
"""
    
    try:
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ Archivo de configuración creado")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear archivo de configuración: {e}")
        return False

def create_startup_script():
    """Crea script de inicio"""
    print("\n🚀 Creando script de inicio...")
    
    # Script para Windows
    batch_content = """@echo off
echo Iniciando Dashboard IT - Clinica Bonsana...
python app.py
pause
"""
    
    # Script para Linux/Mac
    bash_content = """#!/bin/bash
echo "Iniciando Dashboard IT - Clinica Bonsana..."
python3 app.py
"""
    
    try:
        # Windows
        with open('start_dashboard.bat', 'w') as f:
            f.write(batch_content)
        
        # Linux/Mac
        with open('start_dashboard.sh', 'w') as f:
            f.write(bash_content)
        
        # Hacer ejecutable en Linux/Mac
        if os.name != 'nt':
            os.chmod('start_dashboard.sh', 0o755)
        
        print("✅ Scripts de inicio creados")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear scripts de inicio: {e}")
        return False

def verify_installation():
    """Verifica la instalación"""
    print("\n🔍 Verificando instalación...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'utils.py',
        'static/style.css',
        'templates/index.html',
        'config.py'
    ]
    
    required_dirs = [
        'data',
        'static',
        'templates',
        'logs'
    ]
    
    all_good = True
    
    # Verificar archivos
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - FALTANTE")
            all_good = False
    
    # Verificar directorios
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/ - FALTANTE")
            all_good = False
    
    return all_good

def show_next_steps():
    """Muestra los próximos pasos"""
    print("\n" + "=" * 60)
    print("🎉 INSTALACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("📋 PRÓXIMOS PASOS:")
    print()
    print("1. 📁 Coloca tus archivos CSV de GLPI en el directorio 'data/'")
    print("   - El archivo debe usar ';' como delimitador")
    print("   - Debe tener las columnas requeridas (ver README.md)")
    print()
    print("2. 🚀 Inicia el dashboard:")
    if os.name == 'nt':
        print("   - Windows: doble clic en 'start_dashboard.bat'")
        print("   - O ejecuta: python app.py")
    else:
        print("   - Linux/Mac: ./start_dashboard.sh")
        print("   - O ejecuta: python3 app.py")
    print()
    print("3. 🌐 Abre tu navegador en: http://localhost:5000")
    print()
    print("4. 📊 ¡Disfruta analizando tus datos de soporte IT!")
    print()
    print("💡 CONSEJOS:")
    print("   - Revisa config.py para personalizar configuraciones")
    print("   - Usa utils.py para validar y generar datos de prueba")
    print("   - Consulta los logs en logs/dashboard.log para debugging")
    print()
    print("🆘 SOPORTE:")
    print("   - Consulta README.md para documentación completa")
    print("   - Revisa utils.py para herramientas de validación")
    print()

def main():
    """Función principal de instalación"""
    print_banner()
    
    # Verificar Python
    if not check_python_version():
        return False
    
    # Crear estructura de directorios
    create_directory_structure()
    
    # Instalar dependencias
    if not install_dependencies():
        print("\n❌ Instalación fallida: Error al instalar dependencias")
        return False
    
    # Crear archivo de configuración
    create_config_file()
    
    # Crear scripts de inicio
    create_startup_script()
    
    # Crear datos de muestra
    create_sample_data()
    
    # Verificar instalación
    if verify_installation():
        show_next_steps()
        return True
    else:
        print("\n❌ Instalación incompleta: Algunos archivos faltan")
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado durante la instalación: {e}")
        sys.exit(1)