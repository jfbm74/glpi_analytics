# Guía de Integración del Módulo de IA
## Dashboard IT - Clínica Bonsana

Esta guía te ayudará a integrar el módulo de IA con tu aplicación Flask existente.

## 🚀 Pasos de Instalación

### 1. Ejecutar el Instalador

```bash
# Ejecutar el instalador automático
python install_ai_module.py

# Probar la instalación
python test_ai.py
```

### 2. Configurar API Key

Edita el archivo `.env`:

```bash
# Tu API key de Google AI Studio
GOOGLE_AI_API_KEY=AIzaSyALkC-uoOfpS3cB-vnaj8Zor3ccp5MVOBQ

# Modelo a utilizar (recomendado)
GOOGLE_AI_MODEL=gemini-2.0-flash-exp
```

### 3. Integrar con tu app.py Principal

Modifica tu archivo `app.py` existente:

```python
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import os

# AGREGAR: Importar el blueprint de IA
from ai_routes import ai_bp, init_ai_analyzer

def create_app():
    app = Flask(__name__)
    
    # Cargar configuración
    load_dotenv()
    app.config.update({
        'SECRET_KEY': os.getenv('SECRET_KEY', 'default-secret-key'),
        'DATA_DIRECTORY': os.getenv('DATA_DIRECTORY', 'data'),
        'GOOGLE_AI_API_KEY': os.getenv('GOOGLE_AI_API_KEY'),
        'AI_ANALYSIS_ENABLED': os.getenv('AI_ANALYSIS_ENABLED', 'True').lower() == 'true'
    })
    
    # AGREGAR: Registrar blueprint de IA
    app.register_blueprint(ai_bp)
    
    # AGREGAR: Inicializar analizador de IA
    if app.config['AI_ANALYSIS_ENABLED']:
        success = init_ai_analyzer(app.config['DATA_DIRECTORY'])
        if success:
            app.logger.info("Módulo de IA inicializado exitosamente")
        else:
            app.logger.warning("Error al inicializar módulo de IA")
    
    # Tus rutas existentes...
    @app.route('/')
    def index():
        # MODIFICAR: Pasar información de IA al template
        ai_enabled = app.config['AI_ANALYSIS_ENABLED']
        return render_template('index.html', ai_enabled=ai_enabled)
    
    # AGREGAR: Ruta de configuración de IA
    @app.route('/api/ai/config')
    def ai_config():
        return jsonify({
            'ai_enabled': app.config['AI_ANALYSIS_ENABLED'],
            'model': os.getenv('GOOGLE_AI_MODEL', 'gemini-2.0-flash-exp'),
            'api_configured': bool(app.config.get('GOOGLE_AI_API_KEY'))
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 4. Actualizar tu index.html

Agrega acceso al módulo de IA en tu `templates/index.html`:

```html
<!-- En el navbar, después del brand -->
<div class="navbar-nav">
    {% if ai_enabled %}
    <a class="nav-link text-white" href="{{ url_for('ai.ai_analysis_page') }}">
        <i class="bi bi-robot me-1"></i>Análisis de IA
    </a>
    {% endif %}
</div>

<!-- Antes del cierre del container principal -->
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
```

## 📁 Estructura Final de Archivos

```
tu-proyecto/
├── app.py                      # Tu aplicación principal (modificada)
├── ai_routes.py               # Rutas del módulo de IA
├── utils.py                   # Tus utilidades existentes
├── .env                       # Configuración (actualizada)
├── requirements.txt           # Dependencias (actualizada)
├── run_dashboard.py           # Script de inicio
├── test_ai.py                # Tests del módulo
├── install_ai_module.py       # Instalador
├── ai/                        # Módulo de IA
│   ├── __init__.py
│   ├── config.py
│   ├── gemini_client.py
│   ├── analyzer.py
│   ├── prompts.py
│   └── utils.py
├── data/
│   ├── glpi.csv              # Tus datos de tickets
│   ├── reports/              # Reportes de IA generados
│   └── cache/                # Cache de análisis
├── templates/
│   ├── index.html            # Dashboard principal (modificado)
│   └── ai_analysis.html      # Nueva página de IA
├── static/
│   └── style.css             # Tus estilos existentes
└── logs/
    └── dashboard.log         # Logs de la aplicación
```

## 🔗 URLs Disponibles

Una vez integrado, tendrás estas URLs:

- **Dashboard principal**: `http://localhost:5000/`
- **Análisis de IA**: `http://localhost:5000/ai-analysis`
- **API de IA**: `http://localhost:5000/ai/api/ai/*`

## ⚙️ Configuración Avanzada

### Variables de Entorno

```bash
# Configuración básica
GOOGLE_AI_API_KEY=tu-api-key-aqui
GOOGLE_AI_MODEL=gemini-2.0-flash-exp
AI_ANALYSIS_ENABLED=True

# Configuración avanzada
AI_MAX_CSV_ROWS=1000           # Máximo filas para análisis
AI_CACHE_TIMEOUT=3600          # Cache en segundos
AI_REQUEST_TIMEOUT=300         # Timeout de requests
AI_RETRY_ATTEMPTS=3            # Reintentos en caso de error

# Límites de recursos
MAX_ANALYSIS_SIZE_MB=50        # Tamaño máximo de archivo
MAX_CONCURRENT_ANALYSES=3      # Análisis concurrentes

# Desarrollo
DEBUG_AI_RESPONSES=False       # Debug de respuestas de IA
MOCK_AI_RESPONSES=False        # Usar respuestas simuladas
```

### Personalizar Prompts

Puedes personalizar los prompts editando `ai/prompts.py`:

```python
# Ejemplo: Agregar prompt personalizado
@staticmethod
def get_custom_clinic_prompt():
    return """
    Como Director de TI de Clínica Bonsana especializada en fracturas,
    analiza específicamente el impacto en operaciones médicas...
    """
```

## 🧪 Testing

```bash
# Probar instalación completa
python test_ai.py

# Probar conexión con API
curl http://localhost:5000/ai/api/ai/test-connection

# Probar análisis rápido
curl -X POST http://localhost:5000/ai/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"analysis_type": "quick"}'
```

## 🔧 Solución de Problemas

### Error: "Module 'ai' not found"

1. Verifica que la carpeta `ai/` exista
2. Asegúrate de que `ai/__init__.py` esté presente
3. Ejecuta desde el directorio raíz del proyecto

### Error: "API key not valid"

1. Verifica tu API key en Google AI Studio
2. Asegúrate de que esté correctamente configurada en `.env`
3. Verifica que tengas créditos disponibles

### Error: "CSV file not found"

1. Asegúrate de que `data/glpi.csv` exista
2. Verifica que el archivo tenga las columnas requeridas
3. Usa el generador de datos de muestra si es necesario

### Error de memoria o timeout

1. Reduce `AI_MAX_CSV_ROWS` en `.env`
2. Aumenta `AI_REQUEST_TIMEOUT`
3. Verifica tu conexión a internet

## 📊 Uso del Módulo

### Tipos de Análisis Disponibles

1. **Comprehensive**: Análisis exhaustivo completo
2. **Quick**: Análisis rápido de KPIs principales
3. **Technician**: Rendimiento por técnico
4. **SLA**: Análisis de cumplimiento de SLA
5. **Trends**: Análisis de tendencias temporales
6. **Cost**: Optimización de costos

### Ejemplo de Uso Programático

```python
from ai.analyzer import AIAnalyzer

# Crear analizador
analyzer = AIAnalyzer(data_path="data")

# Ejecutar análisis
result = analyzer.run_comprehensive_analysis()

if result['success']:
    print("Análisis:", result['analysis'])
    # Guardar reporte
    analyzer.save_analysis_to_file(result)
```

## 🎯 Próximos Pasos

1. **Personalizar**: Adapta los prompts a las necesidades específicas de tu clínica
2. **Integrar**: Conecta con tus sistemas existentes (GLPI, bases de datos, etc.)
3. **Monitorear**: Configura alertas basadas en análisis de IA
4. **Expandir**: Agrega nuevos tipos de análisis según necesidades

## 📞 Soporte

- Ejecuta `python test_ai.py` para diagnosticar problemas
- Revisa los logs en `logs/dashboard.log`
- Consulta la documentación completa en `README.md`

¡El módulo de IA está listo para proporcionar insights estratégicos avanzados para tu departamento IT! 🚀