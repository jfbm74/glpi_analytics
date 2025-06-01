#!/usr/bin/env python3
"""
Aplicación principal del Dashboard IT - Clínica Bonsana
Integra todas las funcionalidades: Dashboard principal + IA + API + Monitoreo
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, jsonify, request, send_file, abort
from flask import redirect, url_for, flash, session
from dotenv import load_dotenv
import pandas as pd
import json

# Importar módulos del proyecto
try:
    from ai_routes import ai_bp, init_ai_analyzer
    from ai.monitoring import monitor
    from ai.export import ReportExporter
    from utils import validate_csv_structure, analyze_data_quality
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrate de que todos los archivos del proyecto estén presentes")
    sys.exit(1)

# Cargar variables de entorno
load_dotenv()

def create_app():
    """Factory function para crear la aplicación Flask"""
    
    app = Flask(__name__)
    
    # Configuración de la aplicación
    app.config.update({
        'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
        'DATA_DIRECTORY': os.getenv('DATA_DIRECTORY', 'data'),
        'CSV_ENCODING': os.getenv('CSV_ENCODING', 'utf-8'),
        'GOOGLE_AI_API_KEY': os.getenv('GOOGLE_AI_API_KEY'),
        'AI_ANALYSIS_ENABLED': os.getenv('AI_ANALYSIS_ENABLED', 'True').lower() == 'true',
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'HOST': os.getenv('HOST', '0.0.0.0'),
        'PORT': int(os.getenv('PORT', 5000)),
        'DEBUG': os.getenv('FLASK_ENV', 'production') == 'development',
        'DATABASE_URL': os.getenv('DATABASE_URL', 'sqlite:///dashboard.db'),
        'REDIS_URL': os.getenv('REDIS_URL'),
        'MAX_CONTENT_LENGTH': 50 * 1024 * 1024,  # 50MB max file upload
    })
    
    # Configurar logging
    setup_logging(app)
    
    # Inicializar extensiones
    setup_extensions(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Configurar rutas principales
    setup_main_routes(app)
    
    # Configurar manejadores de errores
    setup_error_handlers(app)
    
    # Inicializar servicios
    initialize_services(app)
    
    return app

def setup_logging(app):
    """Configura el sistema de logging"""
    
    # Crear directorio de logs si no existe
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Configurar nivel de logging
    log_level = getattr(logging, app.config['LOG_LEVEL'], logging.INFO)
    
    # Configurar formato de logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para archivo
    file_handler = logging.FileHandler('logs/dashboard.log')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Configurar logger de la aplicación
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    
    if app.config['DEBUG']:
        app.logger.addHandler(console_handler)
    
    # Configurar loggers de librerías
    for logger_name in ['werkzeug', 'ai.analyzer', 'ai.gemini_client']:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        logger.addHandler(file_handler)

def setup_extensions(app):
    """Configura extensiones de Flask"""
    
    # Configurar cache si Redis está disponible
    if app.config.get('REDIS_URL'):
        try:
            import redis
            from flask_caching import Cache
            
            cache_config = {
                'CACHE_TYPE': 'redis',
                'CACHE_REDIS_URL': app.config['REDIS_URL'],
                'CACHE_DEFAULT_TIMEOUT': 300
            }
            app.config.update(cache_config)
            
            cache = Cache(app)
            app.cache = cache
            app.logger.info("Redis cache configurado exitosamente")
            
        except ImportError:
            app.logger.warning("Redis no disponible, usando cache en memoria")
            app.cache = None
    else:
        app.cache = None

def register_blueprints(app):
    """Registra blueprints de la aplicación"""
    
    # Registrar blueprint de IA
    app.register_blueprint(ai_bp)
    app.logger.info("Blueprint de IA registrado")

def setup_main_routes(app):
    """Configura las rutas principales de la aplicación"""
    
    @app.route('/')
    def index():
        """Dashboard principal"""
        try:
            ai_enabled = app.config['AI_ANALYSIS_ENABLED']
            
            # Verificar si existe archivo CSV
            csv_path = Path(app.config['DATA_DIRECTORY']) / 'glpi.csv'
            csv_exists = csv_path.exists()
            
            # Obtener información básica del CSV si existe
            csv_info = None
            if csv_exists:
                try:
                    df = pd.read_csv(csv_path, delimiter=';', encoding=app.config['CSV_ENCODING'], nrows=5)
                    csv_info = {
                        'columns': len(df.columns),
                        'sample_rows': len(df),
                        'has_data': True
                    }
                except Exception as e:
                    app.logger.error(f"Error leyendo CSV: {e}")
                    csv_info = {'has_data': False, 'error': str(e)}
            
            return render_template('index.html', 
                                 ai_enabled=ai_enabled,
                                 csv_exists=csv_exists,
                                 csv_info=csv_info)
                                 
        except Exception as e:
            app.logger.error(f"Error en ruta principal: {e}")
            return render_template('error.html', error="Error cargando dashboard"), 500
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        try:
            # Verificar componentes críticos
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'components': {}
            }
            
            # Verificar archivos de datos
            csv_path = Path(app.config['DATA_DIRECTORY']) / 'glpi.csv'
            health_status['components']['data'] = {
                'status': 'healthy' if csv_path.exists() else 'warning',
                'csv_exists': csv_path.exists()
            }
            
            # Verificar IA si está habilitada
            if app.config['AI_ANALYSIS_ENABLED']:
                try:
                    from ai.analyzer import AIAnalyzer
                    analyzer = AIAnalyzer()
                    ai_test = analyzer.test_ai_connection()
                    health_status['components']['ai'] = {
                        'status': 'healthy' if ai_test.get('success') else 'unhealthy',
                        'api_key_configured': bool(app.config.get('GOOGLE_AI_API_KEY'))
                    }
                except Exception as e:
                    health_status['components']['ai'] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
            
            # Verificar cache
            if app.cache:
                try:
                    app.cache.set('health_test', 'ok', timeout=5)
                    cache_test = app.cache.get('health_test')
                    health_status['components']['cache'] = {
                        'status': 'healthy' if cache_test == 'ok' else 'unhealthy'
                    }
                except Exception as e:
                    health_status['components']['cache'] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
            
            # Determinar estado general
            component_statuses = [comp['status'] for comp in health_status['components'].values()]
            if 'unhealthy' in component_statuses:
                health_status['status'] = 'unhealthy'
                return jsonify(health_status), 503
            elif 'warning' in component_statuses:
                health_status['status'] = 'warning'
            
            return jsonify(health_status)
            
        except Exception as e:
            app.logger.error(f"Error en health check: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    # API Routes para el dashboard principal
    @app.route('/api/metrics')
    def get_metrics():
        """Obtiene métricas generales del dashboard"""
        try:
            analyzer = TicketAnalyzer(data_path=app.config['DATA_DIRECTORY'])
            metrics = analyzer.get_overall_metrics()
            
            # Cache por 5 minutos si está disponible
            if app.cache:
                app.cache.set('dashboard_metrics', metrics, timeout=300)
            
            return jsonify(metrics)
            
        except Exception as e:
            app.logger.error(f"Error obteniendo métricas: {e}")
            return jsonify({'error': 'Error obteniendo métricas'}), 500
    
    @app.route('/api/distributions')
    def get_distributions():
        """Obtiene distribuciones de tickets"""
        try:
            analyzer = TicketAnalyzer(data_path=app.config['DATA_DIRECTORY'])
            distributions = analyzer.get_ticket_distribution()
            
            if app.cache:
                app.cache.set('dashboard_distributions', distributions, timeout=300)
            
            return jsonify(distributions)
            
        except Exception as e:
            app.logger.error(f"Error obteniendo distribuciones: {e}")
            return jsonify({'error': 'Error obteniendo distribuciones'}), 500
    
    @app.route('/api/technicians')
    def get_technicians():
        """Obtiene información de técnicos"""
        try:
            analyzer = TicketAnalyzer(data_path=app.config['DATA_DIRECTORY'])
            technicians = analyzer.get_technician_workload()
            
            if app.cache:
                app.cache.set('dashboard_technicians', technicians, timeout=300)
            
            return jsonify(technicians)
            
        except Exception as e:
            app.logger.error(f"Error obteniendo técnicos: {e}")
            return jsonify({'error': 'Error obteniendo técnicos'}), 500
    
    @app.route('/api/sla')
    def get_sla():
        """Obtiene análisis de SLA"""
        try:
            analyzer = TicketAnalyzer(data_path=app.config['DATA_DIRECTORY'])
            sla_data = analyzer.get_sla_analysis()
            
            if app.cache:
                app.cache.set('dashboard_sla', sla_data, timeout=300)
            
            return jsonify(sla_data)
            
        except Exception as e:
            app.logger.error(f"Error obteniendo SLA: {e}")
            return jsonify({'error': 'Error obteniendo SLA'}), 500
    
    @app.route('/api/csat')
    def get_csat():
        """Obtiene datos de satisfacción del cliente"""
        try:
            analyzer = TicketAnalyzer(data_path=app.config['DATA_DIRECTORY'])
            csat_data = analyzer.get_csat_score()
            
            if app.cache:
                app.cache.set('dashboard_csat', csat_data, timeout=300)
            
            return jsonify(csat_data)
            
        except Exception as e:
            app.logger.error(f"Error obteniendo CSAT: {e}")
            return jsonify({'error': 'Error obteniendo CSAT'}), 500
    
    @app.route('/api/validation')
    def get_validation():
        """Obtiene insights de validación de datos"""
        try:
            analyzer = TicketAnalyzer(data_path=app.config['DATA_DIRECTORY'])
            validation_data = analyzer.get_data_validation_insights()
            
            if app.cache:
                app.cache.set('dashboard_validation', validation_data, timeout=600)
            
            return jsonify(validation_data)
            
        except Exception as e:
            app.logger.error(f"Error obteniendo validación: {e}")
            return jsonify({'error': 'Error obteniendo validación'}), 500
    
    @app.route('/api/config')
    def get_config():
        """Obtiene configuración de la aplicación"""
        return jsonify({
            'ai_enabled': app.config['AI_ANALYSIS_ENABLED'],
            'model': os.getenv('GOOGLE_AI_MODEL', 'gemini-2.0-flash-exp'),
            'api_configured': bool(app.config.get('GOOGLE_AI_API_KEY')),
            'debug': app.config['DEBUG'],
            'version': '1.0.0'
        })
    
    # Rutas adicionales
    @app.route('/dashboard')
    def dashboard():
        """Alias para el dashboard principal"""
        return redirect(url_for('index'))
    
    @app.route('/ai-dashboard')
    def ai_dashboard():
        """Dashboard de monitoreo de IA"""
        if not app.config['AI_ANALYSIS_ENABLED']:
            abort(404)
        return render_template('ai_dashboard.html')

def setup_error_handlers(app):
    """Configura manejadores de errores"""
    
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Endpoint no encontrado'}), 404
        return render_template('error.html', 
                             error="Página no encontrada",
                             error_code=404), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Error interno: {error}")
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Error interno del servidor'}), 500
        return render_template('error.html',
                             error="Error interno del servidor", 
                             error_code=500), 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({'error': 'Archivo demasiado grande'}), 413

def initialize_services(app):
    """Inicializa servicios de la aplicación"""
    
    with app.app_context():
        # Crear directorios necesarios
        required_dirs = [
            app.config['DATA_DIRECTORY'],
            f"{app.config['DATA_DIRECTORY']}/cache",
            f"{app.config['DATA_DIRECTORY']}/reports",
            f"{app.config['DATA_DIRECTORY']}/backups",
            f"{app.config['DATA_DIRECTORY']}/metrics",
            'logs'
        ]
        
        for dir_path in required_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Inicializar analizador de IA si está habilitado
        if app.config['AI_ANALYSIS_ENABLED']:
            try:
                success = init_ai_analyzer(app.config['DATA_DIRECTORY'])
                if success:
                    app.logger.info("Analizador de IA inicializado exitosamente")
                    
                    # Inicializar monitoreo de IA
                    monitor.start_monitoring()
                    app.logger.info("Sistema de monitoreo de IA iniciado")
                else:
                    app.logger.warning("Error inicializando analizador de IA")
            except Exception as e:
                app.logger.error(f"Error crítico inicializando IA: {e}")
        
        # Crear archivo CSV de muestra si no existe
        csv_path = Path(app.config['DATA_DIRECTORY']) / 'glpi.csv'
        if not csv_path.exists():
            app.logger.info("Creando archivo CSV de muestra...")
            try:
                from utils import generate_sample_csv
                generate_sample_csv(str(csv_path), num_records=50)
                app.logger.info("Archivo CSV de muestra creado exitosamente")
            except Exception as e:
                app.logger.error(f"Error creando CSV de muestra: {e}")

# Clase auxiliar para análisis de tickets (compatibilidad)
class TicketAnalyzer:
    """Analizador de tickets compatible con la estructura original"""
    
    def __init__(self, data_path="data"):
        self.data_path = data_path
        self.csv_path = Path(data_path) / "glpi.csv"
        
    def _load_data(self):
        """Carga datos del CSV"""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Archivo CSV no encontrado: {self.csv_path}")
        
        return pd.read_csv(self.csv_path, delimiter=';', encoding='utf-8')
    
    def get_overall_metrics(self):
        """Obtiene métricas generales"""
        try:
            df = self._load_data()
            
            total_tickets = len(df)
            resolved_tickets = len(df[df['Estado'].isin(['Resueltas', 'Cerrado'])])
            resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0
            
            # SLA compliance
            sla_exceeded = len(df[df['Se superó el tiempo de resolución'] == 'Si'])
            sla_compliance = ((total_tickets - sla_exceeded) / total_tickets * 100) if total_tickets > 0 else 0
            
            # Tiempo promedio de resolución (simulado)
            avg_resolution_time = 24.5  # Placeholder
            
            return {
                'total_tickets': total_tickets,
                'resolution_rate': round(resolution_rate, 1),
                'avg_resolution_time_hours': avg_resolution_time,
                'sla_compliance': round(sla_compliance, 1)
            }
            
        except Exception as e:
            logging.error(f"Error en get_overall_metrics: {e}")
            return {
                'total_tickets': 0,
                'resolution_rate': 0,
                'avg_resolution_time_hours': 0,
                'sla_compliance': 0
            }
    
    def get_ticket_distribution(self):
        """Obtiene distribución de tickets"""
        try:
            df = self._load_data()
            
            return {
                'by_type': df['Tipo'].value_counts().to_dict(),
                'by_status': df['Estado'].value_counts().to_dict(),
                'by_priority': df['Prioridad'].value_counts().to_dict(),
                'by_category': df['Categoría'].value_counts().head(10).to_dict()
            }
            
        except Exception as e:
            logging.error(f"Error en get_ticket_distribution: {e}")
            return {'by_type': {}, 'by_status': {}, 'by_priority': {}, 'by_category': {}}
    
    def get_technician_workload(self):
        """Obtiene carga de trabajo por técnico"""
        try:
            df = self._load_data()
            workload = df['Asignado a: - Técnico'].value_counts().to_dict()
            
            # Limpiar nombres de técnicos vacíos
            if '' in workload:
                workload['SIN ASIGNAR'] = workload.pop('')
            
            return workload
            
        except Exception as e:
            logging.error(f"Error en get_technician_workload: {e}")
            return {}
    
    def get_sla_analysis(self):
        """Obtiene análisis de SLA"""
        try:
            df = self._load_data()
            
            incidents = df[df['Tipo'] == 'Incidencia']
            total_incidents = len(incidents)
            sla_exceeded = len(incidents[incidents['Se superó el tiempo de resolución'] == 'Si'])
            
            return {
                'total_incidents': total_incidents,
                'sla_exceeded': sla_exceeded,
                'sla_compliance_rate': ((total_incidents - sla_exceeded) / total_incidents * 100) if total_incidents > 0 else 0
            }
            
        except Exception as e:
            logging.error(f"Error en get_sla_analysis: {e}")
            return {'total_incidents': 0, 'sla_exceeded': 0, 'sla_compliance_rate': 0}
    
    def get_csat_score(self):
        """Obtiene score de satisfacción del cliente"""
        try:
            df = self._load_data()
            
            csat_scores = pd.to_numeric(df['Encuesta de satisfacción - Satisfacción'], errors='coerce').dropna()
            
            if len(csat_scores) > 0:
                return {
                    'average_csat': round(csat_scores.mean(), 2),
                    'total_surveys': len(csat_scores),
                    'distribution': csat_scores.value_counts().to_dict()
                }
            else:
                return {'average_csat': 0, 'total_surveys': 0, 'distribution': {}}
                
        except Exception as e:
            logging.error(f"Error en get_csat_score: {e}")
            return {'average_csat': 0, 'total_surveys': 0, 'distribution': {}}
    
    def get_data_validation_insights(self):
        """Obtiene insights de validación de datos"""
        try:
            df = self._load_data()
            
            insights = {}
            
            # Tickets sin asignar
            unassigned = len(df[df['Asignado a: - Técnico'].isin(['', None])])
            if unassigned > 0:
                insights['unassigned_tickets'] = {
                    'count': unassigned,
                    'recommendation': f"Asignar {unassigned} tickets pendientes a técnicos disponibles"
                }
            
            # Hardware sin elementos asociados
            hardware_tickets = df[df['Categoría'].str.contains('Hardware', na=False)]
            hardware_no_assets = len(hardware_tickets[hardware_tickets['Elementos asociados'].isin(['', None])])
            if hardware_no_assets > 0:
                insights['hardware_no_assets'] = {
                    'count': hardware_no_assets,
                    'recommendation': f"Asociar elementos de hardware a {hardware_no_assets} tickets"
                }
            
            return insights
            
        except Exception as e:
            logging.error(f"Error en get_data_validation_insights: {e}")
            return {}

# Configurar aplicación para diferentes entornos
def configure_for_environment():
    """Configura la aplicación según el entorno"""
    
    env = os.getenv('FLASK_ENV', 'production')
    
    if env == 'development':
        os.environ.setdefault('DEBUG', 'True')
        os.environ.setdefault('LOG_LEVEL', 'DEBUG')
    elif env == 'production':
        os.environ.setdefault('DEBUG', 'False')
        os.environ.setdefault('LOG_LEVEL', 'WARNING')

# Crear instancia de la aplicación
configure_for_environment()
app = create_app()

if __name__ == '__main__':
    try:
        # Verificar requisitos básicos
        if not app.config.get('GOOGLE_AI_API_KEY') and app.config['AI_ANALYSIS_ENABLED']:
            app.logger.warning("API key de Google AI no configurada - funcionalidad de IA deshabilitada")
        
        # Información de inicio
        app.logger.info("="*60)
        app.logger.info("🏥 DASHBOARD IT - CLÍNICA BONSANA")
        app.logger.info("="*60)
        app.logger.info(f"🌍 Entorno: {os.getenv('FLASK_ENV', 'production')}")
        app.logger.info(f"🏠 Host: {app.config['HOST']}:{app.config['PORT']}")
        app.logger.info(f"🤖 IA Habilitada: {app.config['AI_ANALYSIS_ENABLED']}")
        app.logger.info(f"🐛 Debug: {app.config['DEBUG']}")
        app.logger.info(f"📁 Directorio datos: {app.config['DATA_DIRECTORY']}")
        app.logger.info("="*60)
        
        # URLs disponibles
        print("\n🔗 URLs disponibles:")
        base_url = f"http://{app.config['HOST']}:{app.config['PORT']}"
        print(f"   📊 Dashboard principal: {base_url}")
        print(f"   🤖 Análisis de IA: {base_url}/ai-analysis")
        print(f"   📈 Monitoreo de IA: {base_url}/ai-dashboard")
        print(f"   🔍 Health Check: {base_url}/health")
        print(f"   📡 API: {base_url}/api/")
        print()
        
        # Ejecutar aplicación
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'],
            threaded=True
        )
        
    except KeyboardInterrupt:
        app.logger.info("🛑 Aplicación detenida por el usuario")
        if 'monitor' in globals():
            monitor.stop_monitoring()
    except Exception as e:
        app.logger.error(f"❌ Error crítico iniciando aplicación: {e}")
        sys.exit(1)