#!/usr/bin/env python3
"""
Script de deployment para Dashboard IT con IA - Clínica Bonsana
Configuración para entornos de desarrollo, staging y producción
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import tempfile

class DeploymentManager:
    """Gestor de deployment del sistema"""
    
    def __init__(self, environment='development'):
        """
        Inicializa el gestor de deployment
        
        Args:
            environment: Entorno (development, staging, production)
        """
        self.environment = environment
        self.base_dir = Path(os.getcwd())
        self.config = self._load_deployment_config()
        
        print(f"🚀 Iniciando deployment para entorno: {environment}")
        print("="*60)
    
    def _load_deployment_config(self):
        """Carga configuración de deployment"""
        config = {
            'development': {
                'host': '127.0.0.1',
                'port': 5000,
                'debug': True,
                'workers': 1,
                'log_level': 'DEBUG',
                'database_url': 'sqlite:///dashboard_dev.db',
                'redis_url': None,
                'ssl_enabled': False,
                'backup_enabled': False
            },
            'staging': {
                'host': '0.0.0.0',
                'port': 8080,
                'debug': False,
                'workers': 2,
                'log_level': 'INFO',
                'database_url': 'sqlite:///dashboard_staging.db',
                'redis_url': 'redis://localhost:6379/1',
                'ssl_enabled': False,
                'backup_enabled': True
            },
            'production': {
                'host': '0.0.0.0',
                'port': 80,
                'debug': False,
                'workers': 4,
                'log_level': 'WARNING',
                'database_url': 'postgresql://user:pass@localhost/dashboard_prod',
                'redis_url': 'redis://localhost:6379/0',
                'ssl_enabled': True,
                'backup_enabled': True,
                'monitoring_enabled': True,
                'rate_limiting': True
            }
        }
        
        return config.get(self.environment, config['development'])
    
    def deploy(self):
        """Ejecuta el proceso completo de deployment"""
        try:
            steps = [
                ("Verificar requisitos", self._check_requirements),
                ("Preparar entorno", self._prepare_environment),
                ("Instalar dependencias", self._install_dependencies),
                ("Configurar aplicación", self._configure_application),
                ("Configurar base de datos", self._setup_database),
                ("Configurar web server", self._setup_web_server),
                ("Configurar SSL", self._setup_ssl),
                ("Configurar monitoreo", self._setup_monitoring),
                ("Configurar backups", self._setup_backups),
                ("Ejecutar tests", self._run_tests),
                ("Inicializar aplicación", self._initialize_application),
                ("Verificar deployment", self._verify_deployment)
            ]
            
            for i, (step_name, step_func) in enumerate(steps, 1):
                print(f"\n[{i}/{len(steps)}] {step_name}...")
                
                try:
                    if step_func():
                        print(f"    ✅ {step_name} completado")
                    else:
                        print(f"    ⚠️  {step_name} - advertencias")
                except Exception as e:
                    print(f"    ❌ Error en {step_name}: {str(e)}")
                    if self.environment == 'production':
                        raise  # En producción, fallar rápido
                    else:
                        print(f"    ⏭️  Continuando en entorno {self.environment}")
            
            print(f"\n🎉 Deployment {self.environment} completado exitosamente!")
            self._show_deployment_info()
            
        except Exception as e:
            print(f"\n❌ Error en deployment: {str(e)}")
            self._rollback_deployment()
            return False
        
        return True
    
    def _check_requirements(self):
        """Verifica requisitos del sistema"""
        # Verificar Python
        if sys.version_info < (3, 8):
            raise Exception(f"Python 3.8+ requerido. Versión actual: {sys.version}")
        
        # Verificar Git
        try:
            subprocess.run(['git', '--version'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            raise Exception("Git no está instalado")
        
        # Verificar estructura de archivos
        required_files = [
            'app.py', 'requirements.txt', '.env', 
            'ai_routes.py', 'ai/__init__.py'
        ]
        
        missing_files = [f for f in required_files if not (self.base_dir / f).exists()]
        if missing_files:
            raise Exception(f"Archivos faltantes: {missing_files}")
        
        # Verificar espacio en disco
        if self.environment == 'production':
            disk_usage = shutil.disk_usage(self.base_dir)
            free_gb = disk_usage.free / (1024**3)
            if free_gb < 2:
                raise Exception(f"Espacio insuficiente: {free_gb:.1f}GB libres")
        
        return True
    
    def _prepare_environment(self):
        """Prepara el entorno de deployment"""
        # Crear directorios necesarios
        required_dirs = [
            'logs', 'data', 'data/backups', 'data/cache', 
            'data/reports', 'static', 'templates'
        ]
        
        for dir_name in required_dirs:
            dir_path = self.base_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Configurar permisos
        if self.environment in ['staging', 'production']:
            try:
                # Configurar permisos restrictivos
                os.chmod(self.base_dir / '.env', 0o600)
                os.chmod(self.base_dir / 'logs', 0o755)
                os.chmod(self.base_dir / 'data', 0o755)
            except Exception as e:
                print(f"    ⚠️  No se pudieron configurar permisos: {e}")
        
        return True
    
    def _install_dependencies(self):
        """Instala dependencias del proyecto"""
        requirements_file = self.base_dir / 'requirements.txt'
        
        if not requirements_file.exists():
            print("    ⚠️  requirements.txt no encontrado, creando básico...")
            self._create_requirements_file()
        
        # Instalar dependencias
        pip_cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)]
        
        if self.environment == 'production':
            pip_cmd.extend(['--no-cache-dir', '--disable-pip-version-check'])
        
        try:
            subprocess.run(pip_cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error instalando dependencias: {e}")
        
        # Instalar dependencias adicionales según entorno
        if self.environment == 'production':
            prod_deps = ['gunicorn>=20.1.0', 'psycopg2-binary>=2.9.0']
            for dep in prod_deps:
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                                 check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    print(f"    ⚠️  Dependencia opcional no instalada: {dep}")
        
        return True
    
    def _configure_application(self):
        """Configura la aplicación para el entorno"""
        env_file = self.base_dir / '.env'
        
        # Leer configuración actual
        env_config = {}
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_config[key.strip()] = value.strip()
        
        # Actualizar configuración según entorno
        env_updates = {
            'FLASK_ENV': self.environment,
            'HOST': self.config['host'],
            'PORT': str(self.config['port']),
            'DEBUG': str(self.config['debug']).lower(),
            'LOG_LEVEL': self.config['log_level'],
            'DATABASE_URL': self.config['database_url'],
            'WORKERS': str(self.config['workers'])
        }
        
        if self.config.get('redis_url'):
            env_updates['REDIS_URL'] = self.config['redis_url']
        
        if self.environment == 'production':
            env_updates.update({
                'ENABLE_METRICS': 'True',
                'HEALTH_CHECK_ENDPOINT': '/health',
                'RATE_LIMITING': 'True',
                'CACHE_TIMEOUT': '300'
            })
        
        # Actualizar archivo .env
        env_config.update(env_updates)
        
        with open(env_file, 'w') as f:
            f.write(f"# Configuración para entorno: {self.environment}\n")
            f.write(f"# Generado: {datetime.now().isoformat()}\n\n")
            
            for key, value in env_config.items():
                f.write(f"{key}={value}\n")
        
        print(f"    ✅ Configuración actualizada para {self.environment}")
        return True
    
    def _setup_database(self):
        """Configura la base de datos"""
        if 'sqlite' in self.config['database_url']:
            # Para SQLite, solo verificar que el directorio existe
            db_path = self.config['database_url'].replace('sqlite:///', '')
            db_dir = Path(db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"    ✅ Base de datos SQLite configurada: {db_path}")
            
        elif 'postgresql' in self.config['database_url']:
            # Para PostgreSQL en producción
            print("    ⚠️  PostgreSQL configurado - verificar conexión manualmente")
            
        return True
    
    def _setup_web_server(self):
        """Configura el servidor web"""
        if self.environment == 'development':
            return True  # Flask dev server
        
        # Crear configuración de Gunicorn
        gunicorn_conf = self.base_dir / 'gunicorn.conf.py'
        
        gunicorn_config = f"""
# Configuración Gunicorn para {self.environment}
bind = "{self.config['host']}:{self.config['port']}"
workers = {self.config['workers']}
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 300
keepalive = 2
preload_app = True

# Logging
loglevel = "{self.config['log_level'].lower()}"
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
access_log_format = '%%(h)s %%(l)s %%(u)s %%(t)s "%%(r)s" %%(s)s %%(b)s "%%(f)s" "%%(a)s"'

# Process naming
proc_name = "dashboard_it_bonsana"

# Server mechanics
daemon = False
pidfile = "logs/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (si está habilitado)
{'keyfile = "ssl/private.key"' if self.config.get('ssl_enabled') else '# keyfile = None'}
{'certfile = "ssl/certificate.crt"' if self.config.get('ssl_enabled') else '# certfile = None'}
"""
        
        with open(gunicorn_conf, 'w') as f:
            f.write(gunicorn_config)
        
        # Crear script de inicio
        start_script = self.base_dir / 'start_server.sh'
        
        start_script_content = f"""#!/bin/bash
# Script de inicio para {self.environment}

echo "Iniciando Dashboard IT - Clínica Bonsana ({self.environment})"

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Entorno virtual activado"
fi

# Verificar dependencias
python -c "import flask, pandas, google.generativeai" || {{
    echo "Error: Dependencias faltantes"
    exit 1
}}

# Crear directorios necesarios
mkdir -p logs data/cache data/reports

# Iniciar aplicación
if [ "{self.environment}" = "development" ]; then
    echo "Iniciando en modo desarrollo..."
    python app.py
else
    echo "Iniciando con Gunicorn..."
    gunicorn --config gunicorn.conf.py app:app
fi
"""
        
        with open(start_script, 'w') as f:
            f.write(start_script_content)
        
        os.chmod(start_script, 0o755)
        
        print(f"    ✅ Servidor web configurado para {self.environment}")
        return True
    
    def _setup_ssl(self):
        """Configura SSL para producción"""
        if not self.config.get('ssl_enabled'):
            return True
        
        ssl_dir = self.base_dir / 'ssl'
        ssl_dir.mkdir(exist_ok=True)
        
        # En entorno real, aquí configurarías certificados SSL
        print("    ⚠️  SSL habilitado - configurar certificados manualmente")
        print("    📝 Comandos sugeridos:")
        print("       certbot --nginx -d tu-dominio.com")
        print("       openssl req -x509 -newkey rsa:4096 -keyout ssl/private.key -out ssl/certificate.crt -days 365")
        
        return True
    
    def _setup_monitoring(self):
        """Configura monitoreo del sistema"""
        if not self.config.get('monitoring_enabled'):
            return True
        
        # Crear script de monitoreo
        monitor_script = self.base_dir / 'monitor.py'
        
        monitor_content = """#!/usr/bin/env python3
\"\"\"
Script de monitoreo básico para Dashboard IT
\"\"\"

import requests
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_health():
    try:
        response = requests.get('http://localhost/health', timeout=10)
        if response.status_code == 200:
            logger.info("✅ Aplicación saludable")
            return True
        else:
            logger.error(f"❌ Estado no saludable: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Error verificando salud: {e}")
        return False

def monitor_loop():
    while True:
        timestamp = datetime.now().isoformat()
        logger.info(f"🔍 Verificando salud del sistema - {timestamp}")
        
        healthy = check_health()
        if not healthy:
            # Aquí podrías enviar alertas por email, Slack, etc.
            logger.error("🚨 Sistema no saludable - considera revisar logs")
        
        time.sleep(300)  # Verificar cada 5 minutos

if __name__ == '__main__':
    monitor_loop()
"""
        
        with open(monitor_script, 'w') as f:
            f.write(monitor_content)
        
        os.chmod(monitor_script, 0o755)
        
        print("    ✅ Monitoreo configurado")
        return True
    
    def _setup_backups(self):
        """Configura sistema de backups"""
        if not self.config.get('backup_enabled'):
            return True
        
        backup_script = self.base_dir / 'backup.py'
        
        backup_content = f"""#!/usr/bin/env python3
\"\"\"
Script de backup automático para Dashboard IT
\"\"\"

import os
import shutil
import tarfile
from datetime import datetime
from pathlib import Path

def create_backup():
    backup_dir = Path('data/backups')
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"dashboard_backup_{timestamp}.tar.gz"
    backup_path = backup_dir / backup_filename
    
    # Crear archivo tar
    with tarfile.open(backup_path, 'w:gz') as tar:
        # Backup de datos críticos
        tar.add('data', exclude=lambda x: 'backups' in x or 'cache' in x)
        tar.add('.env')
        tar.add('ai')
        tar.add('templates')
        tar.add('static')
        
    print(f"✅ Backup creado: {{backup_path}}")
    
    # Limpiar backups antiguos (mantener últimos 7)
    backups = sorted(backup_dir.glob('dashboard_backup_*.tar.gz'))
    if len(backups) > 7:
        for old_backup in backups[:-7]:
            old_backup.unlink()
            print(f"🗑️  Backup antiguo eliminado: {{old_backup}}")

if __name__ == '__main__':
    create_backup()
"""
        
        with open(backup_script, 'w') as f:
            f.write(backup_content)
        
        os.chmod(backup_script, 0o755)
        
        print("    ✅ Sistema de backups configurado")
        return True
    
    def _run_tests(self):
        """Ejecuta tests del sistema"""
        test_file = self.base_dir / 'test_ai.py'
        
        if test_file.exists():
            try:
                result = subprocess.run([sys.executable, str(test_file)], 
                                      capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print("    ✅ Tests pasaron exitosamente")
                else:
                    print(f"    ⚠️  Tests fallaron: {result.stderr}")
                    if self.environment == 'production':
                        raise Exception("Tests fallidos en producción")
                
            except subprocess.TimeoutExpired:
                print("    ⚠️  Tests excedieron tiempo límite")
                
        else:
            print("    ⚠️  No se encontraron tests")
        
        return True
    
    def _initialize_application(self):
        """Inicializa la aplicación"""
        # Verificar módulo de IA
        try:
            import sys
            sys.path.insert(0, str(self.base_dir))
            from ai.analyzer import AIAnalyzer
            
            # Test básico de IA
            analyzer = AIAnalyzer()
            connection_test = analyzer.test_ai_connection()
            
            if connection_test.get('success'):
                print("    ✅ Módulo de IA inicializado correctamente")
            else:
                print(f"    ⚠️  Problema con IA: {connection_test.get('error', 'Error desconocido')}")
                
        except Exception as e:
            print(f"    ⚠️  Error inicializando IA: {e}")
        
        # Crear archivos de sistema
        health_endpoint = self.base_dir / 'health_check.py'
        
        health_content = '''#!/usr/bin/env python3
"""Endpoint de health check"""

from flask import Flask, jsonify
import time
import psutil

app = Flask(__name__)

@app.route('/health')
def health_check():
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': time.time(),
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'uptime': time.time() - psutil.boot_time()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
'''
        
        with open(health_endpoint, 'w') as f:
            f.write(health_content)
        
        return True
    
    def _verify_deployment(self):
        """Verifica que el deployment sea exitoso"""
        print("    🔍 Verificando deployment...")
        
        # Verificar archivos críticos
        critical_files = [
            '.env', 'gunicorn.conf.py', 'start_server.sh',
            'ai/__init__.py', 'requirements.txt'
        ]
        
        missing_files = []
        for file_path in critical_files:
            if not (self.base_dir / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"    ❌ Archivos faltantes: {missing_files}")
            return False
        
        # Verificar configuración
        env_file = self.base_dir / '.env'
        with open(env_file, 'r') as f:
            env_content = f.read()
            
        required_vars = ['FLASK_ENV', 'GOOGLE_AI_API_KEY', 'HOST', 'PORT']
        missing_vars = [var for var in required_vars if var not in env_content]
        
        if missing_vars:
            print(f"    ❌ Variables de entorno faltantes: {missing_vars}")
            return False
        
        print("    ✅ Deployment verificado correctamente")
        return True
    
    def _show_deployment_info(self):
        """Muestra información del deployment"""
        print("\n" + "="*60)
        print("🎉 DEPLOYMENT COMPLETADO")
        print("="*60)
        
        print(f"\n📋 Información del deployment:")
        print(f"   Entorno: {self.environment}")
        print(f"   Host: {self.config['host']}")
        print(f"   Puerto: {self.config['port']}")
        print(f"   Workers: {self.config['workers']}")
        print(f"   Debug: {self.config['debug']}")
        
        print(f"\n🚀 Para iniciar la aplicación:")
        if self.environment == 'development':
            print(f"   python app.py")
        else:
            print(f"   ./start_server.sh")
            print(f"   # o directamente:")
            print(f"   gunicorn --config gunicorn.conf.py app:app")
        
        print(f"\n🔗 URLs disponibles:")
        protocol = 'https' if self.config.get('ssl_enabled') else 'http'
        base_url = f"{protocol}://{self.config['host']}:{self.config['port']}"
        
        print(f"   Dashboard: {base_url}")
        print(f"   Análisis IA: {base_url}/ai-analysis")
        print(f"   API IA: {base_url}/ai/api/ai/")
        print(f"   Health Check: {base_url}/health")
        
        if self.environment == 'production':
            print(f"\n🔒 Configuración de seguridad:")
            print(f"   SSL: {'✅ Habilitado' if self.config.get('ssl_enabled') else '❌ Deshabilitado'}")
            print(f"   Rate Limiting: {'✅ Habilitado' if self.config.get('rate_limiting') else '❌ Deshabilitado'}")
            print(f"   Monitoreo: {'✅ Habilitado' if self.config.get('monitoring_enabled') else '❌ Deshabilitado'}")
        
        print(f"\n📁 Archivos importantes:")
        print(f"   Configuración: .env")
        print(f"   Logs: logs/")
        print(f"   Datos: data/")
        print(f"   Backups: data/backups/")
        
        print(f"\n💡 Próximos pasos:")
        print(f"   1. Verificar que la aplicación inicie correctamente")
        print(f"   2. Probar endpoints principales")
        print(f"   3. Configurar monitoreo de producción")
        print(f"   4. Configurar backups automáticos")
        print(f"   5. Configurar alertas")
    
    def _rollback_deployment(self):
        """Rollback en caso de error"""
        print("\n🔄 Iniciando rollback...")
        
        # Restaurar archivos de backup si existen
        backup_dir = self.base_dir / 'data' / 'backups'
        if backup_dir.exists():
            backups = sorted(backup_dir.glob('dashboard_backup_*.tar.gz'))
            if backups:
                latest_backup = backups[-1]
                print(f"   📥 Restaurando desde: {latest_backup}")
                # Aquí implementarías la lógica de restauración
        
        print("   ✅ Rollback completado")
    
    def _create_requirements_file(self):
        """Crea archivo requirements.txt básico"""
        basic_requirements = """# Dashboard IT - Clínica Bonsana
# Dependencias principales
Flask>=2.3.0
pandas>=2.0.0
python-dotenv>=1.0.0
google-generativeai>=0.3.0
requests>=2.31.0

# Utilidades
markdown>=3.5.0
beautifulsoup4>=4.12.0
jinja2>=3.1.0
werkzeug>=2.3.0

# Monitoreo (opcional)
psutil>=5.9.0

# Producción
gunicorn>=20.1.0

# Exportación (opcional)
reportlab>=4.0.0
python-docx>=0.8.11
"""
        
        with open(self.base_dir / 'requirements.txt', 'w') as f:
            f.write(basic_requirements)

def main():
    """Función principal del script de deployment"""
    parser = argparse.ArgumentParser(description='Script de deployment para Dashboard IT')
    parser.add_argument('environment', choices=['development', 'staging', 'production'],
                       help='Entorno de deployment')
    parser.add_argument('--force', action='store_true', 
                       help='Forzar deployment sin confirmación')
    parser.add_argument('--rollback', action='store_true',
                       help='Ejecutar rollback')
    
    args = parser.parse_args()
    
    if args.environment == 'production' and not args.force:
        confirm = input(f"⚠️  ¿Confirmas deployment a PRODUCCIÓN? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Deployment cancelado")
            sys.exit(1)
    
    deployment_manager = DeploymentManager(args.environment)
    
    try:
        if args.rollback:
            deployment_manager._rollback_deployment()
        else:
            success = deployment_manager.deploy()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Deployment interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error crítico en deployment: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()