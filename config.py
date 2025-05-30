#!/usr/bin/env python3
"""
Configuración de la aplicación Dashboard IT - Clínica Bonsana
"""

import os
from datetime import timedelta

class Config:
    """Configuración base para la aplicación"""
    
    # Configuración básica de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-clinica-bonsana-2025'
    DEBUG = False
    TESTING = False
    
    # Configuración de datos
    DATA_DIRECTORY = os.environ.get('DATA_DIRECTORY') or 'data'
    CSV_ENCODING = 'utf-8'
    CSV_DELIMITER = ';'
    
    # Configuración de cache (para futuras implementaciones)
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 300))  # 5 minutos
    
    # Configuración de logs
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'dashboard.log')
    
    # Configuración de la aplicación
    APP_NAME = 'Dashboard IT - Clínica Bonsana'
    APP_VERSION = '1.0.0'
    
    # Configuración de métricas
    METRICS_CONFIG = {
        'resolution_states': ['Resueltas', 'Cerrado'],
        'sla_incident_type': 'Incidencia',
        'satisfaction_scale': {'min': 1, 'max': 5},
        'csat_target': 4.0,
        'sla_compliance_target': 95.0,
        'resolution_rate_target': 90.0
    }
    
    # Configuración de visualización
    CHART_CONFIG = {
        'default_colors': [
            '#dc3545',  # Bonsana Red
            '#28a745',  # Success Green
            '#ffc107',  # Warning Yellow
            '#17a2b8',  # Info Blue
            '#6c757d',  # Gray
            '#fd7e14',  # Orange
            '#6f42c1',  # Purple
            '#20c997'   # Teal
        ],
        'max_categories_display': 10,
        'max_technicians_display': 8,
        'max_requesters_display': 5
    }
    
    # Configuración de calidad de datos
    DATA_QUALITY_CONFIG = {
        'completeness_threshold': 90.0,  # % mínimo de completitud
        'required_fields': [
            'ID', 'Título', 'Tipo', 'Estado', 'Fecha de Apertura'
        ],
        'hardware_keywords': [
            'Impresora', 'Computador', 'Equipo', 'Hardware', 'PC', 
            'Monitor', 'Servidor', 'Router', 'Switch'
        ]
    }
    
    # Configuración de reportes
    REPORT_CONFIG = {
        'auto_refresh_interval': 300000,  # 5 minutos en millisegundos
        'date_format': '%Y-%m-%d %H:%M',
        'export_formats': ['json', 'csv', 'pdf'],
        'max_export_records': 10000
    }

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # Configuración de desarrollo
    FLASK_ENV = 'development'
    TEMPLATES_AUTO_RELOAD = True
    
    # Base de datos en memoria para desarrollo rápido
    USE_SAMPLE_DATA = os.environ.get('USE_SAMPLE_DATA', 'False').lower() == 'true'

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    
    # Configuración de seguridad
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Configuración de logging para producción
    LOG_LEVEL = 'WARNING'
    LOG_TO_FILE = True
    LOG_ROTATION = True
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Configuración de rendimiento
    CACHE_TIMEOUT = 600  # 10 minutos en producción
    COMPRESS_RESPONSES = True
    
    # Configuración de monitoreo
    ENABLE_METRICS = True
    HEALTH_CHECK_ENDPOINT = '/health'

class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    DEBUG = True
    
    # Datos de prueba
    DATA_DIRECTORY = 'tests/data'
    USE_SAMPLE_DATA = True
    
    # Configuración de logs para pruebas
    LOG_LEVEL = 'ERROR'
    SUPPRESS_LOGS = True

# Configuración de la base de datos (para futuras expansiones)
class DatabaseConfig:
    """Configuración para conexión a base de datos (futuro)"""
    
    # SQLite para desarrollo
    SQLITE_DATABASE = os.environ.get('SQLITE_DATABASE', 'dashboard.db')
    
    # PostgreSQL para producción
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'dashboard_user')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', '')
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
    POSTGRES_DATABASE = os.environ.get('POSTGRES_DATABASE', 'dashboard_db')
    
    @property
    def postgres_url(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}"

# Configuración de email (para futuras notificaciones)
class EmailConfig:
    """Configuración para notificaciones por email (futuro)"""
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'dashboard@clinicabonsana.com')
    
    # Configuración de alertas
    ALERT_RECIPIENTS = os.environ.get('ALERT_RECIPIENTS', '').split(',')
    SLA_BREACH_ALERT = os.environ.get('SLA_BREACH_ALERT', 'True').lower() == 'true'
    DAILY_REPORT_ENABLED = os.environ.get('DAILY_REPORT_ENABLED', 'False').lower() == 'true'

# Configuración de seguridad
class SecurityConfig:
    """Configuración de seguridad (para futuras implementaciones)"""
    
    # Autenticación
    ENABLE_AUTH = os.environ.get('ENABLE_AUTH', 'False').lower() == 'true'
    AUTH_METHOD = os.environ.get('AUTH_METHOD', 'basic')  # basic, ldap, oauth
    
    # LDAP (para integración con Active Directory)
    LDAP_HOST = os.environ.get('LDAP_HOST', '')
    LDAP_PORT = int(os.environ.get('LDAP_PORT', 389))
    LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN', '')
    LDAP_USER_OBJECT_FILTER = os.environ.get('LDAP_USER_OBJECT_FILTER', '(objectclass=person)')
    
    # Roles y permisos
    ADMIN_USERS = os.environ.get('ADMIN_USERS', '').split(',')
    READONLY_USERS = os.environ.get('READONLY_USERS', '').split(',')
    
    # Rate limiting
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'False').lower() == 'true'
    RATE_LIMIT_DEFAULT = os.environ.get('RATE_LIMIT_DEFAULT', '100 per hour')

# Función para obtener la configuración apropiada
def get_config():
    """
    Retorna la configuración apropiada basada en el entorno
    """
    env = os.environ.get('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()

# Configuraciones adicionales por entorno
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def load_config_from_file(config_file_path):
    """
    Carga configuración adicional desde archivo JSON
    
    Args:
        config_file_path (str): Ruta al archivo de configuración
        
    Returns:
        dict: Configuración cargada
    """
    try:
        import json
        with open(config_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: No se pudo cargar configuración desde {config_file_path}: {e}")
        return {}

# Validación de configuración
def validate_config(config):
    """
    Valida que la configuración sea correcta
    
    Args:
        config: Objeto de configuración
        
    Returns:
        list: Lista de errores encontrados
    """
    errors = []
    
    # Validar directorio de datos
    if not os.path.exists(config.DATA_DIRECTORY):
        errors.append(f"Directorio de datos no existe: {config.DATA_DIRECTORY}")
    
    # Validar configuración de métricas
    metrics_config = config.METRICS_CONFIG
    if not isinstance(metrics_config.get('satisfaction_scale', {}).get('min'), int):
        errors.append("Configuración de escala de satisfacción inválida")
    
    # Validar configuración de colores
    chart_config = config.CHART_CONFIG
    if not isinstance(chart_config.get('default_colors'), list):
        errors.append("Configuración de colores de gráficos inválida")
    
    return errors

# Configuración por defecto para nuevas instalaciones
DEFAULT_CONFIG_FILE = {
    "app": {
        "name": "Dashboard IT - Clínica Bonsana",
        "version": "1.0.0",
        "description": "Sistema de monitoreo y análisis de tickets de soporte IT"
    },
    "data": {
        "auto_backup": True,
        "backup_retention_days": 30,
        "data_validation_enabled": True
    },
    "ui": {
        "theme": "bonsana",
        "auto_refresh": True,
        "refresh_interval": 300
    },
    "alerts": {
        "sla_breach_threshold": 80,
        "backlog_threshold": 50,
        "low_satisfaction_threshold": 3.0
    }
}

def create_default_config_file(file_path):
    """
    Crea un archivo de configuración por defecto
    
    Args:
        file_path (str): Ruta donde crear el archivo
    """
    import json
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG_FILE, f, indent=2, ensure_ascii=False)
        print(f"Archivo de configuración creado: {file_path}")
    except Exception as e:
        print(f"Error al crear archivo de configuración: {e}")

if __name__ == '__main__':
    # Crear archivo de configuración por defecto si no existe
    config_file = 'config.json'
    if not os.path.exists(config_file):
        create_default_config_file(config_file)
    
    # Validar configuración actual
    current_config = get_config()
    errors = validate_config(current_config)
    
    if errors:
        print("Errores en la configuración:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuración válida")
        print(f"Entorno: {current_config.__class__.__name__}")
        print(f"Debug: {current_config.DEBUG}")
        print(f"Directorio de datos: {current_config.DATA_DIRECTORY}")