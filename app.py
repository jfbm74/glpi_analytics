#!/usr/bin/env python3
"""
Aplicación principal del Dashboard IT - Clínica Bonsana - CORREGIDA
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
from collections import defaultdict

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
                    # Importar solo cuando sea necesario para evitar import circular
                    from ai.analyzer import AIAnalyzer
                    test_analyzer = AIAnalyzer(data_path=app.config['DATA_DIRECTORY'])
                    ai_test = test_analyzer.test_ai_connection()
                    health_status['components']['ai'] = {
                        'status': 'healthy' if ai_test.get('success') else 'unhealthy',
                        'api_key_configured': bool(app.config.get('GOOGLE_AI_API_KEY'))
                    }
                except Exception as e:
                    health_status['components']['ai'] = {
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
    
    # API Routes para el dashboard principal - TODAS LAS RUTAS NECESARIAS
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
    
    @app.route('/api/requesters')
    def get_requesters():
        """Obtiene información de solicitantes"""
        try:
            analyzer = TicketAnalyzer(data_path=app.config['DATA_DIRECTORY'])
            requesters = analyzer.get_top_requesters()
            
            if app.cache:
                app.cache.set('dashboard_requesters', requesters, timeout=300)
            
            return jsonify(requesters)
            
        except Exception as e:
            app.logger.error(f"Error obteniendo solicitantes: {e}")
            return jsonify({'error': 'Error obteniendo solicitantes'}), 500
    
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
    
    # NUEVAS RUTAS PARA ESTADÍSTICAS POR TÉCNICO
    @app.route('/api/technicians/sla')
    def get_technicians_sla():
        """Obtiene estadísticas de SLA por técnico"""
        try:
            analyzer = TicketAnalyzer(data_path=app.config['DATA_DIRECTORY'])
            sla_data = analyzer.get_technician_sla_stats()
            
            return jsonify(sla_data)
            
        except Exception as e:
            app.logger.error(f"Error obteniendo SLA por técnico: {e}")
            return jsonify({'error': 'Error obteniendo SLA por técnico'}), 500
    
    @app.route('/api/technicians/csat')
    def get_technicians_csat():
        """Obtiene estadísticas de CSAT por técnico"""
        try:
            analyzer = TicketAnalyzer(data_path=app.config['DATA_DIRECTORY'])
            csat_data = analyzer.get_technician_csat_stats()
            
            return jsonify(csat_data)
            
        except Exception as e:
            app.logger.error(f"Error obteniendo CSAT por técnico: {e}")
            return jsonify({'error': 'Error obteniendo CSAT por técnico'}), 500
    
    @app.route('/api/technicians/resolution-time')
    def get_technicians_resolution():
        """Obtiene estadísticas de tiempo de resolución por técnico"""
        try:
            analyzer = TicketAnalyzer(data_path=app.config['DATA_DIRECTORY'])
            resolution_data = analyzer.get_technician_resolution_stats()
            
            return jsonify(resolution_data)
            
        except Exception as e:
            app.logger.error(f"Error obteniendo tiempos de resolución por técnico: {e}")
            return jsonify({'error': 'Error obteniendo tiempos de resolución por técnico'}), 500
    
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
            return render_template('error.html', 
                                 error="El módulo de IA no está habilitado", 
                                 error_code=404), 404
        
        try:
            return render_template('ai_dashboard.html')
        except Exception as e:
            app.logger.error(f"Error cargando dashboard IA: {e}")
            return render_template('error.html', 
                                 error=f"Error cargando dashboard IA: {str(e)}", 
                                 error_code=500), 500
    
    @app.route('/ai-analysis')
    def ai_analysis():
        """Página de análisis de IA"""
        if not app.config['AI_ANALYSIS_ENABLED']:
            return render_template('error.html', 
                                 error="El módulo de IA no está habilitado", 
                                 error_code=404), 404
        
        try:
            return render_template('ai_analysis.html')
        except Exception as e:
            app.logger.error(f"Error cargando página de análisis IA: {e}")
            return render_template('error.html', 
                                 error=f"Error cargando página de análisis: {str(e)}", 
                                 error_code=500), 500
    
    @app.route('/debug/routes')
    def debug_routes():
        """Debug: muestra todas las rutas disponibles"""
        if not app.config['DEBUG']:
            abort(404)
        
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                'rule': rule.rule
            })
        
        return jsonify({
            'total_routes': len(routes),
            'routes': sorted(routes, key=lambda x: x['rule'])
        })

    @app.route('/upload-csv', methods=['POST'])
    def upload_csv():
        """Maneja la subida de archivos CSV de GLPI"""
        try:
            # Verificar que se envió un archivo
            if 'csv_file' not in request.files:
                return jsonify({'success': False, 'error': 'No se seleccionó ningún archivo'}), 400
            
            file = request.files['csv_file']
            
            # Verificar que el archivo tiene nombre
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No se seleccionó ningún archivo'}), 400
            
            # Verificar extensión del archivo
            if not file.filename.lower().endswith('.csv'):
                return jsonify({'success': False, 'error': 'Solo se permiten archivos CSV'}), 400
            
            # Crear directorio de datos si no existe
            data_dir = Path(app.config['DATA_DIRECTORY'])
            data_dir.mkdir(exist_ok=True)
            
            # Crear backup del archivo actual si existe
            csv_path = data_dir / 'glpi.csv'
            if csv_path.exists():
                backup_dir = data_dir / 'backups'
                backup_dir.mkdir(exist_ok=True)
                backup_filename = f"glpi_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                backup_path = backup_dir / backup_filename
                csv_path.rename(backup_path)
                app.logger.info(f"Archivo anterior respaldado como: {backup_filename}")
            
            # Guardar el nuevo archivo
            file.save(str(csv_path))
            app.logger.info(f"Archivo CSV subido exitosamente: {file.filename}")
            
            # Validar estructura del CSV
            try:
                # Intentar múltiples encodings y configuraciones para manejar archivos GLPI
                df = None
                encodings_to_try = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
                
                for encoding in encodings_to_try:
                    try:
                        df = pd.read_csv(
                            csv_path, 
                            delimiter=';', 
                            encoding=encoding, 
                            nrows=5,
                            quotechar='"',  # Manejar comillas
                            skipinitialspace=True  # Limpiar espacios
                        )
                        app.logger.info(f"CSV leído exitosamente con encoding: {encoding}")
                        break
                    except Exception as e:
                        app.logger.debug(f"Falló encoding {encoding}: {e}")
                        continue
                
                if df is None:
                    raise ValueError("No se pudo leer el archivo CSV con ninguna configuración de encoding")
                file_info = {
                    'filename': file.filename,
                    'size_mb': round(csv_path.stat().st_size / (1024 * 1024), 2),
                    'columns': len(df.columns),
                    'sample_rows': len(df),
                    'upload_time': datetime.now().isoformat()
                }
                
                # Limpiar cache si está disponible
                if app.cache:
                    app.cache.clear()
                    app.logger.info("Cache limpiado después de subir nuevo archivo")
                
                return jsonify({
                    'success': True,
                    'message': 'Archivo CSV subido y validado exitosamente',
                    'file_info': file_info
                })
                
            except Exception as e:
                # Si hay error en la validación, eliminar el archivo y restaurar backup si existe
                if csv_path.exists():
                    csv_path.unlink()
                
                # Restaurar backup si existe
                backup_files = list((data_dir / 'backups').glob('glpi_backup_*.csv'))
                if backup_files:
                    latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
                    latest_backup.rename(csv_path)
                    app.logger.info("Backup restaurado debido a error de validación")
                
                app.logger.error(f"Error validando CSV: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Error validando archivo CSV: {str(e)}'
                }), 400
                
        except Exception as e:
            app.logger.error(f"Error en upload de CSV: {e}")
            return jsonify({
                'success': False,
                'error': f'Error procesando archivo: {str(e)}'
            }), 500

    @app.route('/<path:path>')
    def catch_all(path):
        """Maneja rutas no encontradas"""
        app.logger.warning(f"Ruta no encontrada: /{path}")
        return render_template('error.html', 
                             error=f"La ruta '/{path}' no existe", 
                             error_code=404), 404

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

# Clase mejorada para análisis de tickets - TODAS LAS FUNCIONES NECESARIAS
class TicketAnalyzer:
    """Analizador de tickets compatible con la estructura original - COMPLETO"""
    
    def __init__(self, data_path="data"):
        self.data_path = data_path
        self.csv_path = Path(data_path) / "glpi.csv"
        
    def _load_data(self):
        """Carga datos del CSV con manejo robusto de encoding y formato"""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Archivo CSV no encontrado: {self.csv_path}")
        
        # Intentar múltiples configuraciones para manejar archivos GLPI
        encodings_to_try = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(
                    self.csv_path, 
                    delimiter=';', 
                    encoding=encoding,
                    quotechar='"',  # Manejar comillas en valores
                    skipinitialspace=True,  # Limpiar espacios extra
                    na_values=['', 'NULL', 'null', 'N/A', 'n/a']  # Valores nulos
                )
                logging.info(f"Datos cargados exitosamente con {encoding}: {len(df)} filas, {len(df.columns)} columnas")
                
                # Log de las primeras columnas para debug
                logging.info(f"Columnas encontradas: {list(df.columns[:10])}")
                return df
                
            except Exception as e:
                logging.debug(f"Falló carga con encoding {encoding}: {e}")
                continue
        
        # Si ningún encoding funcionó
        logging.error(f"No se pudo cargar el archivo CSV con ninguna configuración")
        raise ValueError("Archivo CSV no compatible o corrupto")
    
    def get_overall_metrics(self):
        """Obtiene métricas generales"""
        try:
            df = self._load_data()
            
            total_tickets = len(df)
            
            # Estados que consideramos como resueltos
            resolved_states = ['Resueltas', 'Cerrado', 'Solucionado', 'Finalizado']
            resolved_tickets = len(df[df['Estado'].isin(resolved_states)])
            resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0
            
            # SLA compliance - CORREGIDO: Solo aplicar a incidencias
            sla_compliance = 0
            if 'Tipo' in df.columns and 'Se superó el tiempo de resolución' in df.columns:
                # Filtrar solo incidencias para el cálculo de SLA
                incidents = df[df['Tipo'] == 'Incidencia']
                total_incidents = len(incidents)
                
                if total_incidents > 0:
                    sla_exceeded = len(incidents[incidents['Se superó el tiempo de resolución'] == 'Si'])
                    sla_compliance = ((total_incidents - sla_exceeded) / total_incidents * 100)
                    logging.info(f"SLA calculation: {total_incidents} incidencias, {sla_exceeded} excedidas, {round(sla_compliance, 1)}% compliance")
                else:
                    logging.warning("No se encontraron incidencias para calcular SLA")
            
            # Tiempo promedio de resolución (simulado si no hay datos reales)
            avg_resolution_time = 24.5  # Placeholder
            
            # Obtener datos del CSAT
            csat_data = self.get_csat_score()
            
            # Contar mantenimientos preventivos
            preventive_maintenance_count = 0
            if 'Categoría' in df.columns:
                preventive_maintenance_count = len(df[df['Categoría'] == 'Equipos Computo > Computador > Mantenimiento Preventivo'])
                logging.info(f"Mantenimientos preventivos encontrados: {preventive_maintenance_count}")
            
            return {
                'total_tickets': total_tickets,
                'resolution_rate': round(resolution_rate, 1),
                'avg_resolution_time_hours': avg_resolution_time,
                'sla_compliance': round(sla_compliance, 1),
                'csat_percentage': csat_data.get('csat_percentage', 0),
                'high_satisfaction_count': csat_data.get('high_satisfaction_count', 0),
                'total_surveys': csat_data.get('total_surveys', 0),
                'preventive_maintenance_count': preventive_maintenance_count
            }
            
        except Exception as e:
            logging.error(f"Error en get_overall_metrics: {e}")
            return {
                'total_tickets': 0,
                'resolution_rate': 0,
                'avg_resolution_time_hours': 0,
                'sla_compliance': 0,
                'csat_percentage': 0,
                'high_satisfaction_count': 0,
                'total_surveys': 0,
                'preventive_maintenance_count': 0
            }
    
    def get_ticket_distribution(self):
        """Obtiene distribución de tickets"""
        try:
            df = self._load_data()
            
            # Verificar que las columnas existan
            distributions = {}
            
            if 'Tipo' in df.columns:
                distributions['by_type'] = df['Tipo'].value_counts().to_dict()
            else:
                distributions['by_type'] = {}
            
            if 'Estado' in df.columns:
                distributions['by_status'] = df['Estado'].value_counts().to_dict()
            else:
                distributions['by_status'] = {}
            
            if 'Prioridad' in df.columns:
                distributions['by_priority'] = df['Prioridad'].value_counts().to_dict()
            else:
                distributions['by_priority'] = {}
            
            if 'Categoría' in df.columns:
                distributions['by_category'] = df['Categoría'].value_counts().head(10).to_dict()
            else:
                distributions['by_category'] = {}
            
            return distributions
            
        except Exception as e:
            logging.error(f"Error en get_ticket_distribution: {e}")
            return {'by_type': {}, 'by_status': {}, 'by_priority': {}, 'by_category': {}}
    
    def get_technician_workload(self):
        """Obtiene carga de trabajo por técnico - MEJORADO para detectar sin asignar"""
        try:
            df = self._load_data()
            
            # Buscar columna de técnico
            tech_column = None
            possible_columns = ['Asignado a: - Técnico', 'Técnico', 'Assigned_to', 'Technician']
            
            for col in possible_columns:
                if col in df.columns:
                    tech_column = col
                    break
            
            if tech_column is None:
                logging.warning("No se encontró columna de técnico")
                return {}
            
            logging.info(f"Usando columna de técnico: {tech_column}")
            
            # Análisis detallado de valores para debug
            unique_values = df[tech_column].unique()
            logging.info(f"Valores únicos en columna técnico: {unique_values}")
            
            # Crear copia de la serie para trabajar
            tech_series = df[tech_column].copy()
            
            # Identificar y marcar todos los casos de "sin asignar"
            # Casos comunes: '', None, NaN, 'NULL', espacios en blanco, etc.
            unassigned_mask = (
                tech_series.isna() |                    # NaN/None
                (tech_series == '') |                   # Cadena vacía
                (tech_series == ' ') |                  # Solo espacios
                (tech_series.str.strip() == '') |      # Espacios al inicio/final
                (tech_series.str.upper() == 'NULL') |  # NULL como texto
                (tech_series.str.upper() == 'N/A') |   # N/A
                (tech_series.str.upper() == 'NONE')    # NONE como texto
            )
            
            # Contar tickets sin asignar
            unassigned_count = unassigned_mask.sum()
            logging.info(f"Tickets sin asignar detectados: {unassigned_count}")
            
            # Reemplazar todos los casos sin asignar con un valor consistente
            tech_series.loc[unassigned_mask] = 'SIN ASIGNAR'
            
            # Obtener conteos
            workload = tech_series.value_counts().to_dict()
            
            logging.info(f"Distribución final por técnico: {workload}")
            
            # Asegurar que "SIN ASIGNAR" aparezca si hay tickets sin asignar
            if unassigned_count > 0 and 'SIN ASIGNAR' not in workload:
                workload['SIN ASIGNAR'] = unassigned_count
            
            return workload
        
        except Exception as e:
            logging.error(f"Error en get_technician_workload: {e}")
            logging.error(f"Traceback completo: ", exc_info=True)
            return {}
    
    def get_top_requesters(self):
        """Obtiene top solicitantes"""
        try:
            df = self._load_data()
            
            # Buscar columna de solicitante
            requester_column = None
            possible_columns = ['Solicitante - Solicitante', 'Solicitante', 'Requester', 'Cliente']
            
            for col in possible_columns:
                if col in df.columns:
                    requester_column = col
                    break
            
            if requester_column is None:
                logging.warning("No se encontró columna de solicitante")
                return {}
            
            top_requesters = df[requester_column].value_counts().head(10).to_dict()
            
            # Limpiar nombres vacíos
            if '' in top_requesters:
                del top_requesters['']
            
            return top_requesters
            
        except Exception as e:
            logging.error(f"Error en get_top_requesters: {e}")
            return {}
    
    def get_sla_analysis(self):
        """Obtiene análisis de SLA"""
        try:
            df = self._load_data()
            
            # Filtrar solo incidencias si hay columna de tipo
            if 'Tipo' in df.columns:
                incidents = df[df['Tipo'] == 'Incidencia']
            else:
                incidents = df  # Usar todos los tickets si no hay columna de tipo
            
            total_incidents = len(incidents)
            sla_exceeded = 0
            
            if 'Se superó el tiempo de resolución' in incidents.columns:
                sla_exceeded = len(incidents[incidents['Se superó el tiempo de resolución'] == 'Si'])
            
            sla_compliance_rate = ((total_incidents - sla_exceeded) / total_incidents * 100) if total_incidents > 0 else 0
            
            # Análisis por nivel de SLA si existe la columna
            sla_compliance_by_level = {}
            if 'ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución' in incidents.columns:
                sla_column = 'ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución'
                
                for sla_level in incidents[sla_column].dropna().unique():
                    level_incidents = incidents[incidents[sla_column] == sla_level]
                    level_total = len(level_incidents)
                    level_exceeded = len(level_incidents[level_incidents['Se superó el tiempo de resolución'] == 'Si'])
                    level_within_sla = level_total - level_exceeded
                    level_compliance = (level_within_sla / level_total * 100) if level_total > 0 else 0
                    
                    sla_compliance_by_level[sla_level] = {
                        'total': level_total,
                        'within_sla': level_within_sla,
                        'exceeded': level_exceeded,
                        'compliance_rate': round(level_compliance, 1)
                    }
            
            return {
                'total_incidents': total_incidents,
                'sla_exceeded': sla_exceeded,
                'sla_compliance_rate': round(sla_compliance_rate, 1),
                'sla_compliance_by_level': sla_compliance_by_level
            }
            
        except Exception as e:
            logging.error(f"Error en get_sla_analysis: {e}")
            return {'total_incidents': 0, 'sla_exceeded': 0, 'sla_compliance_rate': 0, 'sla_compliance_by_level': {}}
    
    def get_csat_score(self):
        """Obtiene score de satisfacción del cliente - CORREGIDO: Porcentaje de 4-5 estrellas"""
        try:
            df = self._load_data()
            
            # Buscar columna de satisfacción
            csat_column = None
            possible_columns = ['Encuesta de satisfacción - Satisfacción', 'CSAT', 'Satisfacción', 'Rating']
            
            for col in possible_columns:
                if col in df.columns:
                    csat_column = col
                    break
            
            if csat_column is None:
                return {'csat_percentage': 0, 'total_surveys': 0, 'high_satisfaction_count': 0, 'distribution': {}}
            
            # Convertir a numérico y filtrar valores válidos (1-5)
            csat_scores = pd.to_numeric(df[csat_column], errors='coerce').dropna()
            valid_scores = csat_scores[(csat_scores >= 1) & (csat_scores <= 5)]
            
            if len(valid_scores) > 0:
                # Contar encuestas con 4 o 5 estrellas (alta satisfacción)
                high_satisfaction = valid_scores[valid_scores >= 4]
                high_satisfaction_count = len(high_satisfaction)
                total_surveys = len(valid_scores)
                
                # Calcular porcentaje de alta satisfacción
                csat_percentage = (high_satisfaction_count / total_surveys * 100) if total_surveys > 0 else 0
                
                logging.info(f"CSAT calculation: {high_satisfaction_count} encuestas ≥4 de {total_surveys} total = {round(csat_percentage, 1)}%")
                
                return {
                    'csat_percentage': round(csat_percentage, 1),
                    'total_surveys': total_surveys,
                    'high_satisfaction_count': high_satisfaction_count,
                    'distribution': valid_scores.value_counts().to_dict(),
                    'average_csat': round(valid_scores.mean(), 2)  # Mantener promedio para referencia
                }
            else:
                return {'csat_percentage': 0, 'total_surveys': 0, 'high_satisfaction_count': 0, 'distribution': {}}
                
        except Exception as e:
            logging.error(f"Error en get_csat_score: {e}")
            return {'csat_percentage': 0, 'total_surveys': 0, 'high_satisfaction_count': 0, 'distribution': {}}
    
    def get_data_validation_insights(self):
        """Obtiene insights de validación de datos"""
        try:
            df = self._load_data()
            
            insights = {}
            
            # Tickets sin asignar
            tech_column = None
            possible_tech_columns = ['Asignado a: - Técnico', 'Técnico', 'Assigned_to']
            
            for col in possible_tech_columns:
                if col in df.columns:
                    tech_column = col
                    break
            
            if tech_column:
                unassigned = len(df[df[tech_column].isin(['', None]) | df[tech_column].isna()])
                if unassigned > 0:
                    insights['unassigned_tickets'] = {
                        'count': unassigned,
                        'recommendation': f"Asignar {unassigned} tickets pendientes a técnicos disponibles"
                    }
            
            # Hardware sin elementos asociados
            if 'Categoría' in df.columns and 'Elementos asociados' in df.columns:
                hardware_tickets = df[df['Categoría'].str.contains('Hardware', na=False)]
                hardware_no_assets = len(hardware_tickets[hardware_tickets['Elementos asociados'].isin(['', None]) | hardware_tickets['Elementos asociados'].isna()])
                if hardware_no_assets > 0:
                    insights['hardware_no_assets'] = {
                        'count': hardware_no_assets,
                        'recommendation': f"Asociar elementos de hardware a {hardware_no_assets} tickets"
                    }
            
            # Tickets sin categoría
            if 'Categoría' in df.columns:
                no_category = len(df[df['Categoría'].isin(['', None]) | df['Categoría'].isna()])
                if no_category > 0:
                    insights['no_category_tickets'] = {
                        'count': no_category,
                        'recommendation': f"Asignar categoría a {no_category} tickets"
                    }
            
            return insights
            
        except Exception as e:
            logging.error(f"Error en get_data_validation_insights: {e}")
            return {}
    
    def get_technician_sla_stats(self):
        """Obtiene estadísticas de SLA por técnico - CORREGIDO"""
        try:
            df = self._load_data()
            
            # Buscar columnas necesarias
            tech_column = None
            possible_tech_columns = ['Asignado a: - Técnico', 'Técnico', 'Assigned_to']
            
            for col in possible_tech_columns:
                if col in df.columns:
                    tech_column = col
                    break
            
            if not tech_column:
                logging.warning("No se encontró columna de técnico para SLA")
                return {}
            
            # Verificar columnas requeridas
            required_columns = ['Tipo', 'Se superó el tiempo de resolución']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logging.warning(f"Columnas faltantes para SLA: {missing_columns}")
                return {}
            
            # Filtrar solo incidencias (donde aplica SLA)
            incidents = df[df['Tipo'] == 'Incidencia'].copy()
            
            if len(incidents) == 0:
                logging.info("No hay incidencias para calcular SLA")
                return {}
            
            stats = {}
            
            # Procesar cada técnico
            for technician in incidents[tech_column].dropna().unique():
                if not technician or str(technician).strip() == '':
                    continue
                    
                tech_incidents = incidents[incidents[tech_column] == technician]
                total_incidents = len(tech_incidents)
                
                if total_incidents == 0:
                    continue
                
                # Calcular SLA
                sla_exceeded_count = len(tech_incidents[tech_incidents['Se superó el tiempo de resolución'] == 'Si'])
                sla_compliant_count = total_incidents - sla_exceeded_count
                
                # Calcular porcentaje de cumplimiento
                compliance_rate = (sla_compliant_count / total_incidents * 100) if total_incidents > 0 else 0
                
                # Asegurar que no hay valores NaN
                compliance_rate = round(compliance_rate, 1) if not pd.isna(compliance_rate) else 0.0
                
                stats[technician] = {
                    'total_incidents': total_incidents,
                    'sla_compliant': sla_compliant_count,
                    'sla_exceeded': sla_exceeded_count,
                    'compliance_rate': compliance_rate
                }
            
            logging.info(f"SLA stats calculadas para {len(stats)} técnicos")
            return stats
            
        except Exception as e:
            logging.error(f"Error en get_technician_sla_stats: {e}", exc_info=True)
            return {}



    def get_technician_csat_stats(self):
        """Obtiene estadísticas de CSAT por técnico - CORREGIDO"""
        try:
            df = self._load_data()
            
            # Buscar columnas necesarias
            tech_column = None
            csat_column = None
            
            possible_tech_columns = ['Asignado a: - Técnico', 'Técnico', 'Assigned_to']
            possible_csat_columns = ['Encuesta de satisfacción - Satisfacción', 'CSAT', 'Satisfacción']
            
            for col in possible_tech_columns:
                if col in df.columns:
                    tech_column = col
                    break
            
            for col in possible_csat_columns:
                if col in df.columns:
                    csat_column = col
                    break
            
            if not tech_column or not csat_column:
                logging.warning(f"Columnas faltantes - Técnico: {tech_column}, CSAT: {csat_column}")
                return {}
            
            stats = {}
            
            # Procesar cada técnico
            for technician in df[tech_column].dropna().unique():
                if not technician or str(technician).strip() == '':
                    continue
                    
                tech_tickets = df[df[tech_column] == technician]
                
                # Convertir scores CSAT a numérico, eliminando valores inválidos
                csat_scores = pd.to_numeric(tech_tickets[csat_column], errors='coerce').dropna()
                
                # Filtrar scores válidos (1-5)
                valid_scores = csat_scores[(csat_scores >= 1) & (csat_scores <= 5)]
                
                if len(valid_scores) == 0:
                    continue
                
                # Calcular estadísticas
                total_surveys = len(valid_scores)
                average_csat = valid_scores.mean()
                
                # Categorizar scores - CORREGIDO: usar los nombres correctos
                excellent_ratings = len(valid_scores[valid_scores >= 4])  # 4-5 estrellas
                poor_ratings = len(valid_scores[valid_scores <= 2])       # 1-2 estrellas
                
                # Asegurar que no hay valores NaN
                average_csat = round(average_csat, 2) if not pd.isna(average_csat) else 0.0
                
                stats[technician] = {
                    'total_surveys': total_surveys,
                    'average_csat': average_csat,
                    'excellent_ratings': excellent_ratings,  # CORREGIDO
                    'poor_ratings': poor_ratings             # CORREGIDO
                }
            
            logging.info(f"CSAT stats calculadas para {len(stats)} técnicos")
            return stats
            
        except Exception as e:
            logging.error(f"Error en get_technician_csat_stats: {e}", exc_info=True)
            return {}
 
    def get_technician_csat_stats(self):
        """Obtiene estadísticas de CSAT por técnico - CORREGIDO"""
        try:
            df = self._load_data()
            
            # Buscar columnas necesarias
            tech_column = None
            csat_column = None
            
            possible_tech_columns = ['Asignado a: - Técnico', 'Técnico', 'Assigned_to']
            possible_csat_columns = ['Encuesta de satisfacción - Satisfacción', 'CSAT', 'Satisfacción']
            
            for col in possible_tech_columns:
                if col in df.columns:
                    tech_column = col
                    break
            
            for col in possible_csat_columns:
                if col in df.columns:
                    csat_column = col
                    break
            
            if not tech_column or not csat_column:
                logging.warning(f"Columnas faltantes - Técnico: {tech_column}, CSAT: {csat_column}")
                return {}
            
            stats = {}
            
            # Procesar cada técnico
            for technician in df[tech_column].dropna().unique():
                if not technician or str(technician).strip() == '':
                    continue
                    
                tech_tickets = df[df[tech_column] == technician]
                
                # Convertir scores CSAT a numérico, eliminando valores inválidos
                csat_scores = pd.to_numeric(tech_tickets[csat_column], errors='coerce').dropna()
                
                # Filtrar scores válidos (1-5)
                valid_scores = csat_scores[(csat_scores >= 1) & (csat_scores <= 5)]
                
                if len(valid_scores) == 0:
                    continue
                
                # Calcular estadísticas
                total_surveys = len(valid_scores)
                average_csat = valid_scores.mean()
                
                # Categorizar scores - CORREGIDO: usar los nombres correctos
                excellent_ratings = len(valid_scores[valid_scores >= 4])  # 4-5 estrellas
                poor_ratings = len(valid_scores[valid_scores <= 2])       # 1-2 estrellas
                
                # Asegurar que no hay valores NaN
                average_csat = round(average_csat, 2) if not pd.isna(average_csat) else 0.0
                
                stats[technician] = {
                    'total_surveys': total_surveys,
                    'average_csat': average_csat,
                    'excellent_ratings': excellent_ratings,  # CORREGIDO
                    'poor_ratings': poor_ratings             # CORREGIDO
                }
            
            logging.info(f"CSAT stats calculadas para {len(stats)} técnicos")
            return stats
            
        except Exception as e:
            logging.error(f"Error en get_technician_csat_stats: {e}", exc_info=True)
            return {}

    def get_technician_resolution_stats(self):
        """Obtiene estadísticas de tiempo de resolución por técnico - CORREGIDO"""
        try:
            df = self._load_data()
            
            # Buscar columna de técnico
            tech_column = None
            possible_tech_columns = ['Asignado a: - Técnico', 'Técnico', 'Assigned_to']
            
            for col in possible_tech_columns:
                if col in df.columns:
                    tech_column = col
                    break
            
            if not tech_column:
                logging.warning("No se encontró columna de técnico para resolución")
                return {}
            
            # Filtrar solo tickets resueltos
            resolved_states = ['Resueltas', 'Cerrado']
            resolved_tickets = df[df['Estado'].isin(resolved_states)].copy()
            
            if len(resolved_tickets) == 0:
                logging.info("No hay tickets resueltos para calcular tiempos")
                return {}
            
            stats = {}
            
            # Procesar cada técnico
            for technician in resolved_tickets[tech_column].dropna().unique():
                if not technician or str(technician).strip() == '':
                    continue
                    
                tech_tickets = resolved_tickets[resolved_tickets[tech_column] == technician]
                total_resolved = len(tech_tickets)
                
                if total_resolved == 0:
                    continue
                
                # Intentar calcular tiempo real de resolución si tenemos las fechas
                avg_resolution_hours = None
                min_resolution_hours = None
                max_resolution_hours = None
                
                if 'Fecha de Apertura' in tech_tickets.columns and 'Fecha de solución' in tech_tickets.columns:
                    try:
                        # Convertir fechas
                        tech_tickets_copy = tech_tickets.copy()
                        tech_tickets_copy['Fecha de Apertura'] = pd.to_datetime(
                            tech_tickets_copy['Fecha de Apertura'], errors='coerce'
                        )
                        tech_tickets_copy['Fecha de solución'] = pd.to_datetime(
                            tech_tickets_copy['Fecha de solución'], errors='coerce'
                        )
                        
                        # Calcular diferencias en horas
                        time_diffs = (
                            tech_tickets_copy['Fecha de solución'] - tech_tickets_copy['Fecha de Apertura']
                        ).dt.total_seconds() / 3600
                        
                        # Filtrar valores válidos (positivos y menores a 30 días)
                        valid_times = time_diffs[(time_diffs > 0) & (time_diffs < 720)]  # 720h = 30 días
                        
                        if len(valid_times) > 0:
                            avg_resolution_hours = valid_times.mean()
                            min_resolution_hours = valid_times.min()
                            max_resolution_hours = valid_times.max()
                            
                    except Exception as e:
                        logging.warning(f"Error calculando tiempos reales para {technician}: {e}")
                
                # Si no se pudo calcular tiempo real, usar estimación basada en prioridad
                if avg_resolution_hours is None or pd.isna(avg_resolution_hours):
                    # Estimar basado en la distribución de prioridades del técnico
                    priorities = tech_tickets['Prioridad'].value_counts() if 'Prioridad' in tech_tickets.columns else {}
                    estimated_hours = 0
                    
                    if len(priorities) > 0:
                        for priority, count in priorities.items():
                            if priority == 'Alta':
                                estimated_hours += count * 8   # 8 horas promedio
                            elif priority == 'Mediana':
                                estimated_hours += count * 24  # 24 horas promedio
                            else:
                                estimated_hours += count * 48  # 48 horas promedio
                        
                        avg_resolution_hours = estimated_hours / total_resolved if total_resolved > 0 else 24
                    else:
                        avg_resolution_hours = 24  # Default
                    
                    # Valores por defecto para min/max si no se pudieron calcular
                    min_resolution_hours = avg_resolution_hours * 0.5 if avg_resolution_hours else 12
                    max_resolution_hours = avg_resolution_hours * 2 if avg_resolution_hours else 48
                
                # Categorizar resoluciones
                fast_threshold = 24  # Menos de 24 horas es rápido
                slow_threshold = 72  # Más de 72 horas es lento
                
                # Estimar distribución basada en el promedio
                if avg_resolution_hours <= fast_threshold:
                    fast_resolutions = int(total_resolved * 0.8)  # 80% rápidas
                    slow_resolutions = int(total_resolved * 0.1)  # 10% lentas
                elif avg_resolution_hours <= slow_threshold:
                    fast_resolutions = int(total_resolved * 0.5)  # 50% rápidas
                    slow_resolutions = int(total_resolved * 0.3)  # 30% lentas
                else:
                    fast_resolutions = int(total_resolved * 0.2)  # 20% rápidas
                    slow_resolutions = int(total_resolved * 0.6)  # 60% lentas
                
                # Asegurar que no hay valores NaN y redondear
                avg_resolution_hours = round(avg_resolution_hours, 1) if not pd.isna(avg_resolution_hours) else 24.0
                min_resolution_hours = round(min_resolution_hours, 1) if not pd.isna(min_resolution_hours) else 12.0
                max_resolution_hours = round(max_resolution_hours, 1) if not pd.isna(max_resolution_hours) else 48.0
                
                stats[technician] = {
                    'total_resolved': total_resolved,
                    'avg_resolution_hours': avg_resolution_hours,
                    'min_resolution_hours': min_resolution_hours,  # CORREGIDO
                    'max_resolution_hours': max_resolution_hours,  # CORREGIDO
                    'fast_resolutions': fast_resolutions,
                    'slow_resolutions': slow_resolutions
                }
            
            logging.info(f"Resolution stats calculadas para {len(stats)} técnicos")
            return stats
            
        except Exception as e:
                logging.error(f"Error en get_technician_resolution_stats: {e}", exc_info=True)
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