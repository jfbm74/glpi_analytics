"""
Integración del módulo de IA en app.py principal
Agregar estas modificaciones al archivo app.py existente
"""

# AGREGAR ESTAS IMPORTACIONES al inicio del archivo app.py
import os
import logging
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# Importar el blueprint de IA
from ai_routes import ai_bp, init_ai_analyzer

# MODIFICAR LA CONFIGURACIÓN DE LA APP
def create_app():
    app = Flask(__name__)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Configuración de la aplicación
    app.config.update({
        'SECRET_KEY': os.getenv('SECRET_KEY', 'default-secret-key'),
        'DATA_DIRECTORY': os.getenv('DATA_DIRECTORY', 'data'),
        'GOOGLE_AI_API_KEY': os.getenv('GOOGLE_AI_API_KEY'),
        'AI_ANALYSIS_ENABLED': os.getenv('AI_ANALYSIS_ENABLED', 'True').lower() == 'true',
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'DEBUG': os.getenv('FLASK_ENV') == 'development'
    })
    
    # Configurar logging
    setup_logging(app)
    
    # Registrar blueprint de IA
    app.register_blueprint(ai_bp)
    
    # Inicializar analizador de IA
    if app.config['AI_ANALYSIS_ENABLED']:
        success = init_ai_analyzer(app.config['DATA_DIRECTORY'])
        if success:
            app.logger.info("Módulo de IA inicializado exitosamente")
        else:
            app.logger.warning("Error al inicializar módulo de IA")
    
    # AGREGAR NUEVA RUTA para la página de IA
    @app.route('/ai-analysis')
    def ai_analysis():
        """Página de análisis de IA"""
        if not app.config['AI_ANALYSIS_ENABLED']:
            return render_template('error.html', 
                                 message="Módulo de IA no habilitado"), 503
        return render_template('ai_analysis.html')
    
    # MODIFICAR LA RUTA PRINCIPAL para agregar botón de IA
    @app.route('/')
    def index():
        """Dashboard principal con acceso a IA"""
        ai_enabled = app.config['AI_ANALYSIS_ENABLED']
        return render_template('index.html', ai_enabled=ai_enabled)
    
    # AGREGAR RUTA DE CONFIGURACIÓN DE IA
    @app.route('/api/ai/config')
    def ai_config():
        """Configuración del módulo de IA"""
        return jsonify({
            'ai_enabled': app.config['AI_ANALYSIS_ENABLED'],
            'model': os.getenv('GOOGLE_AI_MODEL', 'gemini-2.0-flash-exp'),
            'api_configured': bool(app.config.get('GOOGLE_AI_API_KEY'))
        })
    
    return app

def setup_logging(app):
    """Configurar sistema de logging"""
    log_level = getattr(logging, app.config['LOG_LEVEL'], logging.INFO)
    
    # Configurar logger de la aplicación
    app.logger.setLevel(log_level)
    
    # Crear directorio de logs si no existe
    log_dir = os.path.dirname(os.getenv('LOG_FILE', 'logs/dashboard.log'))
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar handler para archivo
    if not app.debug:
        file_handler = logging.FileHandler(os.getenv('LOG_FILE', 'logs/dashboard.log'))
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
    
    # Configurar logger para el módulo de IA
    ai_logger = logging.getLogger('ai')
    ai_logger.setLevel(log_level)

# AGREGAR AL FINAL DEL ARCHIVO app.py
if __name__ == '__main__':
    app = create_app()
    
    # Crear directorios necesarios
    os.makedirs(app.config['DATA_DIRECTORY'], exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Ejecutar aplicación
    app.run(
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=5000
    )

# EJEMPLO DE MODIFICACIÓN DEL index.html PARA AGREGAR BOTÓN DE IA
"""
Agregar esto al navbar de templates/index.html:

<div class="navbar-nav">
    {% if ai_enabled %}
    <a class="nav-link text-white" href="{{ url_for('ai.ai_analysis_page') }}">
        <i class="bi bi-robot me-1"></i>Análisis de IA
    </a>
    {% endif %}
    <span class="navbar-text text-white">
        <i class="bi bi-calendar-today me-1"></i>
        <span id="currentDate"></span>
    </span>
</div>

Y agregar esta sección antes del cierre del container en index.html:

<!-- AI Analysis Quick Access -->
{% if ai_enabled %}
<div class="row mt-4">
    <div class="col-12">
        <div class="card border-primary">
            <div class="card-header bg-primary text-white">
                <h5 class="card-title mb-0">
                    <i class="bi bi-robot me-2"></i>
                    Análisis Inteligente con IA
                </h5>
            </div>
            <div class="card-body">
                <p class="card-text">
                    Obtén insights estratégicos avanzados usando inteligencia artificial. 
                    Analiza tendencias, identifica oportunidades de mejora y recibe recomendaciones personalizadas.
                </p>
                <div class="row g-2">
                    <div class="col-md-4">
                        <a href="{{ url_for('ai.ai_analysis_page') }}" class="btn btn-primary w-100">
                            <i class="bi bi-brain me-2"></i>Análisis Completo
                        </a>
                    </div>
                    <div class="col-md-4">
                        <a href="{{ url_for('ai.ai_analysis_page') }}?type=quick" class="btn btn-outline-primary w-100">
                            <i class="bi bi-lightning me-2"></i>Análisis Rápido
                        </a>
                    </div>
                    <div class="col-md-4">
                        <a href="{{ url_for('ai.ai_analysis_page') }}?type=sla" class="btn btn-outline-primary w-100">
                            <i class="bi bi-shield-check me-2"></i>Análisis SLA
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endif %}
"""