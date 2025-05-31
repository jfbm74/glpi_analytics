#!/usr/bin/env python3
"""
Configuración para Dashboard IT - Clínica Bonsana
"""

import os
from datetime import timedelta

class Config:
    """Configuración base"""
    
    # Configuración del servidor Flask
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    SECRET_KEY = os.environ.get('SECRET_KEY', 'bonsana-dashboard-secret-key-2024')
    
    # Configuración de datos
    DATA_PATH = os.environ.get('DATA_PATH', 'data')
    ALLOWED_EXTENSIONS = ['.csv']
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join('logs', 'dashboard.log')
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Configuración de la aplicación
    APP_NAME = 'Dashboard IT - Clínica Bonsana'
    VERSION = '1.0.0'
    TIMEZONE = 'America/Bogota'
    
    # Configuración de cache
    CACHE_TIMEOUT = timedelta(minutes=5)
    ENABLE_CACHE = True
    
    # Colores corporativos Clínica Bonsana
    CORPORATE_COLORS = {
        'primary': '#dc3545',           # Rojo Bonsana
        'primary_light': '#f8d7da',     # Rojo claro
        'primary_dark': '#b02a37',      # Rojo oscuro
        'secondary': '#6c757d',         # Gris
        'success': '#28a745',           # Verde
        'warning': '#ffc107',           # Amarillo
        'info': '#17a2b8',             # Azul
        'light': '#f8f9fa',            # Gris claro
        'dark': '#343a40',             # Gris oscuro
        'white': '#ffffff'             # Blanco
    }
    
    # Configuración de métricas y KPIs
    METRICS_CONFIG = {
        # Estados considerados como resueltos
        'resolved_states': ['Resueltas', 'Cerrado'],
        
        # Tipos de ticket que son incidencias (para SLA)
        'incident_types': ['Incidencia'],
        
        # Umbrales de rendimiento SLA
        'sla_excellent_threshold': 90,  # >= 90% es excelente
        'sla_good_threshold': 70,       # >= 70% es bueno
        'sla_poor_threshold': 50,       # < 50% es pobre
        
        # Umbrales de satisfacción CSAT
        'csat_excellent_threshold': 4.0,  # >= 4.0 es excelente
        'csat_good_threshold': 3.0,       # >= 3.0 es bueno
        'csat_poor_threshold': 2.0,       # < 2.0 es pobre
        
        # Umbrales de tiempo de resolución (en horas)
        'resolution_fast_threshold': 24,    # <= 24h es rápido
        'resolution_slow_threshold': 72,    # > 72h es lento
        
        # Límites para gráficos y tablas
        'max_categories_chart': 10,
        'max_technicians_chart': 10,
        'max_requesters_list': 15,
        
        # Configuración de tendencias
        'trend_period_days': 30,
        'min_data_points': 5
    }
    
    # Configuración de columnas CSV
    CSV_COLUMNS = {
        'required': [
            'ID',
            'Título',
            'Tipo',
            'Categoría',
            'Prioridad',
            'Estado',
            'Fecha de Apertura',
            'Fecha de solución',
            'Se superó el tiempo de resolución',
            'Asignado a: - Técnico',
            'Solicitante - Solicitante'
        ],
        'optional': [
            'Elementos asociados',
            'ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución',
            'Encuesta de satisfacción - Satisfacción',
            'Tiempo de solución',
            'Duración total',
            'Última actualización',
            'Estadísticas - Tiempo de solución',
            'Costo - Costo de material',
            'Costo - Costo total'
        ],
        'aliases': {
            # Mapeo de nombres alternativos de columnas
            'Tecnico': 'Asignado a: - Técnico',
            'Solicitante': 'Solicitante - Solicitante',
            'SLA': 'Se superó el tiempo de resolución',
            'CSAT': 'Encuesta de satisfacción - Satisfacción',
            'ANS': 'ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución'
        }
    }
    
    # Configuración de formato de datos
    DATA_FORMATS = {
        'date_format': '%Y-%m-%d %H:%M',
        'csv_delimiter': ';',
        'csv_encoding': 'utf-8',
        'decimal_places': 2,
        'percentage_decimal_places': 1
    }
    
    # Configuración de la interfaz de usuario
    UI_CONFIG = {
        'charts_height': {
            'small': 250,
            'medium': 300,
            'large': 400
        },
        'table_page_size': 50,
        'animation_duration': 300,
        'refresh_interval': 300000,  # 5 minutos en millisegundos
        'chart_colors': [
            '#dc3545', '#17a2b8', '#28a745', '#ffc107', 
            '#6c757d', '#e83e8c', '#fd7e14', '#6f42c1'
        ]
    }
    
    # Configuración de exportación
    EXPORT_CONFIG = {
        'formats': ['json', 'csv', 'xlsx'],
        'max_records': 10000,
        'filename_prefix': 'dashboard_export_',
        'include_metadata': True
    }
    
    # Configuración de seguridad
    SECURITY_CONFIG = {
        'enable_cors': True,
        'allowed_origins': ['http://localhost:*', 'http://127.0.0.1:*'],
        'rate_limit': '100/minute',
        'enable_csrf': False,  # Deshabilitado para API
        'max_request_size': 16 * 1024 * 1024  # 16MB
    }
    
    # Configuración de backup
    BACKUP_CONFIG = {
        'enable_auto_backup': True,
        'backup_interval_hours': 24,
        'max_backup_files': 7,
        'backup_path': 'backups',
        'include_logs': True
    }

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    CACHE_TIMEOUT = timedelta(seconds=30)  # Cache más corto en desarrollo

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    HOST = '0.0.0.0'
    PORT = 80
    CACHE_TIMEOUT = timedelta(minutes=15)  # Cache más largo en producción
    
    # Configuración de seguridad para producción
    SECURITY_CONFIG = {
        **Config.SECURITY_CONFIG,
        'enable_csrf': True,
        'rate_limit': '50/minute',  # Más restrictivo
        'allowed_origins': []  # Debe configurarse específicamente
    }

class TestingConfig(Config):
    """Configuración para testing"""
    DEBUG = True
    TESTING = True
    DATA_PATH = 'test_data'
    LOG_LEVEL = 'ERROR'
    CACHE_TIMEOUT = timedelta(seconds=1)  # Cache muy corto para tests

# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtiene la configuración basada en la variable de entorno"""
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, DevelopmentConfig)

# Configuración activa
active_config = get_config()