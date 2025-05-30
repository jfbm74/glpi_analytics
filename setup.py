#!/usr/bin/env python3
"""
Script de instalación y configuración para Dashboard IT - Clínica Bonsana
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

class DashboardSetup:
    """Clase para manejar la instalación y configuración del dashboard"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.required_python_version = (3, 8)
        self.required_directories = [
            'data',
            'templates', 
            'static',
            'logs',
            'backups'
        ]
        self.required_files = [
            'requirements.txt',
            'app.py',
            'config.py'
        ]
        
    def check_python_version(self):
        """Verifica que la versión de Python sea compatible"""
        current_version = sys.version_info[:2]
        if current_version < self.required_python_version:
            print(f"❌ Error: Se requiere Python {self.required_python_version[0]}.{self.required_python_version[1]} o superior")
            print(f"   Versión actual: {current_version[0]}.{current_version[1]}")
            return False
        
        print(f"✅ Python {current_version[0]}.{current_version[1]} - Compatible")
        return True
    
    def check_required_files(self):
        """Verifica que todos los archivos requeridos existan"""
        missing_files = []
        
        for file_name in self.required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                missing_files.append(file_name)
        
        if missing_files:
            print(f"❌ Error: Archivos faltantes: {', '.join(missing_files)}")
            return False
        
        print("✅ Todos los archivos requeridos están presentes")
        return True
    
    def create_directories(self):
        """Crea los directorios necesarios"""
        print("📁 Creando directorios necesarios...")
        
        for directory in self.required_directories:
            dir_path = self.project_root / directory
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"   📂 Creado: {directory}/")
            else:
                print(f"   ✅ Existe: {directory}/")
    
    def install_dependencies(self):
        """Instala las dependencias de Python"""
        print("📦 Instalando dependencias...")
        
        requirements_file = self.project_root / 'requirements.txt'
        
        try:
            # Verificar si pip está disponible
            subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                         check=True, capture_output=True)
            
            # Instalar dependencias
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dependencias instaladas correctamente")
                return True
            else:
                print(f"❌ Error al instalar dependencias: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError:
            print("❌ Error: pip no está disponible")
            return False
        except FileNotFoundError:
            print("❌ Error: requirements.txt no encontrado")
            return False
    
    def create_sample_data(self):
        """Crea datos de muestra si no existe glpi.csv"""
        data_dir = self.project_root / 'data'
        glpi_file = data_dir / 'glpi.csv'
        
        if not glpi_file.exists():
            print("📊 Generando datos de muestra...")
            
            try:
                from utils import generate_sample_csv
                generate_sample_csv(str(glpi_file), num_records=100)
                print("✅ Datos de muestra generados en data/glpi.csv")
            except ImportError:
                print("⚠️  No se pudo importar el generador de datos de muestra")
                print("   Coloca manualmente el archivo glpi.csv en el directorio data/")
        else:
            print("✅ Archivo de datos existente encontrado")
    
    def create_config_file(self):
        """Crea archivo de configuración personalizado"""
        config_file = self.project_root / 'config.json'
        
        if not config_file.exists():
            print("⚙️  Creando archivo de configuración...")
            
            config_data = {
                "app": {
                    "name": "Dashboard IT - Clínica Bonsana",
                    "version": "1.0.0",
                    "debug": False
                },
                "data": {
                    "directory": "data",
                    "auto_backup": True,
                    "backup_retention_days": 30
                },
                "ui": {
                    "theme": "bonsana",
                    "auto_refresh": True,
                    "refresh_interval": 300
                },
                "security": {
                    "enable_auth": False,
                    "allowed_ips": []
                }
            }
            
            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                print("✅ Archivo de configuración creado")
            except Exception as e:
                print(f"⚠️  Error al crear configuración: {e}")
        else:
            print("✅ Archivo de configuración existente")
    
    def create_environment_file(self):
        """Crea archivo .env de ejemplo"""
        env_file = self.project_root / '.env.example'
        
        if not env_file.exists():
            print("🔧 Creando archivo de variables de entorno de ejemplo...")
            
            env_content = """# Configuración de Dashboard IT - Clínica Bonsana
# Copia este archivo como .env y personaliza los valores

# Configuración de Flask
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta-muy-segura-aqui

# Configuración de datos
DATA_DIRECTORY=data
CSV_ENCODING=utf-8

# Configuración de logs
LOG_LEVEL=INFO
LOG_FILE=logs/dashboard.log

# Configuración de cache
CACHE_TIMEOUT=300

# Configuración de base de datos (futuro)
DATABASE_URL=sqlite:///dashboard.db

# Configuración de email (futuro)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu-email@clinicabonsana.com
MAIL_PASSWORD=tu-password

# Configuración de seguridad
ENABLE_AUTH=False
ADMIN_USERS=admin@clinicabonsana.com

# Configuración de monitoreo
ENABLE_METRICS=True
HEALTH_CHECK_ENDPOINT=/health
"""
            
            try:
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(env_content)
                print("✅ Archivo .env.example creado")
            except Exception as e:
                print(f"⚠️  Error al crear .env.example: {e}")
    
    def test_installation(self):
        """Prueba básica de la instalación"""
        print("🧪 Probando instalación...")
        
        try:
            # Importar módulos principales
            import flask
            import pandas
            import numpy
            
            print("✅ Dependencias principales importadas correctamente")
            
            # Probar importación de módulos del proyecto
            sys.path.insert(0, str(self.project_root))
            
            try:
                import config
                print("✅ Módulo de configuración importado")
            except ImportError as e:
                print(f"⚠️  Error al importar configuración: {e}")
            
            try:
                import app
                print("✅ Aplicación principal importada")
            except ImportError as e:
                print(f"⚠️  Error al importar aplicación: {e}")
            
            return True
            
        except ImportError as e:
            print(f"❌ Error al importar dependencias: {e}")
            return False
    
    def create_startup_scripts(self):
        """Crea scripts de inicio para diferentes sistemas operativos"""
        print("🚀 Creando scripts de inicio...")
        
        # Script para Windows
        windows_script = self.project_root / 'start_dashboard.bat'
        windows_content = f'''@echo off
echo Iniciando Dashboard IT - Clinica Bonsana...
cd /d "{self.project_root}"
python app.py
pause
'''
        
        # Script para Linux/macOS
        unix_script = self.project_root / 'start_dashboard.sh'
        unix_content = f'''#!/bin/bash
echo "Iniciando Dashboard IT - Clinica Bonsana..."
cd "{self.project_root}"
python3 app.py
'''
        
        try:
            with open(windows_script, 'w', encoding='utf-8') as f:
                f.write(windows_content)
            print("✅ Script de Windows creado: start_dashboard.bat")
            
            with open(unix_script, 'w', encoding='utf-8') as f:
                f.write(unix_content)
            
            # Hacer ejecutable en sistemas Unix
            if os.name != 'nt':
                os.chmod(unix_script, 0o755)
            
            print("✅ Script de Unix creado: start_dashboard.sh")
            
        except Exception as e:
            print(f"⚠️  Error al crear scripts de inicio: {e}")
    
    def show_next_steps(self):
        """Muestra los próximos pasos después de la instalación"""
        print("\n" + "="*60)
        print("🎉 ¡INSTALACIÓN COMPLETADA!")
        print("="*60)
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Coloca tu archivo CSV en el directorio 'data/'")
        print("   - Nombre sugerido: glpi.csv")
        print("   - Delimitador: punto y coma (;)")
        print("   - Codificación: UTF-8")
        print()
        print("2. Inicia la aplicación:")
        if os.name == 'nt':
            print("   Windows: Ejecuta 'start_dashboard.bat'")
        else:
            print("   Linux/macOS: Ejecuta './start_dashboard.sh'")
        print("   O manualmente: python app.py")
        print()
        print("3. Abre tu navegador web en:")
        print("   http://localhost:5000")
        print()
        print("📁 ARCHIVOS CREADOS:")
        print("   - config.json: Configuración personalizable")
        print("   - .env.example: Variables de entorno de ejemplo")
        print("   - logs/: Directorio para archivos de log")
        print("   - backups/: Directorio para respaldos")
        print()
        print("🔧 CONFIGURACIÓN ADICIONAL:")
        print("   - Edita config.json para personalizar la aplicación")
        print("   - Crea archivo .env basado en .env.example")
        print("   - Consulta README.md para más información")
        print()
        print("📞 SOPORTE:")
        print("   - Consulta la documentación en README.md")
        print("   - Ejecuta 'python utils.py validate <archivo.csv>' para validar datos")
        print("   - Ejecuta 'python utils.py analyze-quality <archivo.csv>' para análisis")
        print()
    
    def run_setup(self):
        """Ejecuta el proceso completo de instalación"""
        print("🏥 Dashboard IT - Clínica Bonsana")
        print("=" * 50)
        print("Iniciando configuración del sistema...\n")
        
        # Verificaciones previas
        if not self.check_python_version():
            sys.exit(1)
        
        if not self.check_required_files():
            sys.exit(1)
        
        # Proceso de instalación
        self.create_directories()
        
        if not self.install_dependencies():
            print("\n⚠️  Instalación de dependencias falló. Intenta manualmente:")
            print("   pip install -r requirements.txt")
            sys.exit(1)
        
        self.create_sample_data()
        self.create_config_file()
        self.create_environment_file()
        self.create_startup_scripts()
        
        # Prueba final
        if not self.test_installation():
            print("\n⚠️  Algunas pruebas fallaron, pero la instalación básica está completa")
        
        self.show_next_steps()

def main():
    """Función principal"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Dashboard IT - Clínica Bonsana - Script de Instalación")
        print("\nUso: python setup.py")
        print("\nEste script configura automáticamente el dashboard:")
        print("- Verifica dependencias")
        print("- Crea directorios necesarios")
        print("- Instala paquetes de Python")
        print("- Genera configuración inicial")
        print("- Crea datos de muestra (si es necesario)")
        return
    
    setup = DashboardSetup()
    setup.run_setup()

if __name__ == '__main__':
    main()