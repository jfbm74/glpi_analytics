"""
Rutas de Flask para el módulo de IA
"""

from flask import Blueprint, request, jsonify, render_template
import os
import logging
from datetime import datetime
import traceback

from ai.analyzer import AIAnalyzer

# Crear blueprint para las rutas de IA
ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

# Configurar logging
logger = logging.getLogger(__name__)

# Inicializar analizador de IA
analyzer = None

def init_ai_analyzer(data_path="data"):
    """Inicializa el analizador de IA"""
    global analyzer
    try:
        analyzer = AIAnalyzer(data_path=data_path)
        logger.info("Analizador de IA inicializado exitosamente")
        return True
    except Exception as e:
        logger.error(f"Error al inicializar analizador de IA: {str(e)}")
        return False

@ai_bp.route('/')
def ai_analysis_page():
    """Página principal de análisis de IA"""
    return render_template('ai_analysis.html')

@ai_bp.route('/api/ai/test-connection', methods=['GET'])
def test_ai_connection():
    """Prueba la conexión con la API de IA"""
    try:
        if not analyzer:
            return jsonify({
                "success": False,
                "error": "Analizador de IA no inicializado"
            }), 500
        
        result = analyzer.test_ai_connection()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error en test de conexión: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_bp.route('/api/ai/model-info', methods=['GET'])
def get_model_info():
    """Obtiene información del modelo de IA"""
    try:
        if not analyzer:
            return jsonify({
                "success": False,
                "error": "Analizador de IA no inicializado"
            }), 500
        
        model_info = analyzer.get_model_info()
        return jsonify({
            "success": True,
            "model_info": model_info
        })
        
    except Exception as e:
        logger.error(f"Error al obtener info del modelo: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_bp.route('/api/ai/analyze', methods=['POST'])
def run_analysis():
    """Ejecuta análisis de IA"""
    try:
        if not analyzer:
            return jsonify({
                "success": False,
                "error": "Analizador de IA no inicializado"
            }), 500
        
        data = request.get_json()
        analysis_type = data.get('analysis_type', 'comprehensive')
        
        logger.info(f"Iniciando análisis tipo: {analysis_type}")
        
        # Ejecutar análisis según el tipo
        if analysis_type == 'comprehensive':
            result = analyzer.run_comprehensive_analysis()
        elif analysis_type == 'quick':
            result = analyzer.run_quick_analysis()
        else:
            # Análisis personalizado
            result = analyzer.run_custom_analysis(analysis_type)
        
        logger.info(f"Análisis completado. Éxito: {result.get('success', False)}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error en análisis: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc() if logger.level == logging.DEBUG else None
        }), 500

@ai_bp.route('/api/ai/history', methods=['GET'])
def get_analysis_history():
    """Obtiene historial de análisis"""
    try:
        if not analyzer:
            return jsonify({
                "success": False,
                "error": "Analizador de IA no inicializado"
            }), 500
        
        history = analyzer.get_analysis_history()
        return jsonify({
            "success": True,
            "history": history
        })
        
    except Exception as e:
        logger.error(f"Error al obtener historial: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_bp.route('/api/ai/save-analysis', methods=['POST'])
def save_analysis():
    """Guarda análisis en archivo"""
    try:
        if not analyzer:
            return jsonify({
                "success": False,
                "error": "Analizador de IA no inicializado"
            }), 500
        
        analysis_data = request.get_json()
        
        if not analysis_data:
            return jsonify({
                "success": False,
                "error": "No se proporcionaron datos del análisis"
            }), 400
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        analysis_type = analysis_data.get('analysis_type', 'unknown')
        filename = f"analysis_{analysis_type}_{timestamp}.json"
        
        # Guardar archivo
        filepath = analyzer.save_analysis_to_file(analysis_data, filename)
        
        return jsonify({
            "success": True,
            "message": "Análisis guardado exitosamente",
            "filepath": filepath,
            "filename": filename
        })
        
    except Exception as e:
        logger.error(f"Error al guardar análisis: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_bp.route('/api/ai/available-types', methods=['GET'])
def get_available_analysis_types():
    """Obtiene tipos de análisis disponibles"""
    try:
        if not analyzer:
            return jsonify({
                "success": False,
                "error": "Analizador de IA no inicializado"
            }), 500
        
        available_types = analyzer.get_available_analysis_types()
        return jsonify({
            "success": True,
            "analysis_types": available_types
        })
        
    except Exception as e:
        logger.error(f"Error al obtener tipos de análisis: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_bp.route('/api/ai/cached-analysis/<cache_key>', methods=['GET'])
def get_cached_analysis(cache_key):
    """Obtiene análisis desde cache"""
    try:
        if not analyzer:
            return jsonify({
                "success": False,
                "error": "Analizador de IA no inicializado"
            }), 500
        
        cached_analysis = analyzer.get_cached_analysis(cache_key)
        
        if cached_analysis:
            return jsonify({
                "success": True,
                "analysis": cached_analysis
            })
        else:
            return jsonify({
                "success": False,
                "error": "Análisis no encontrado en cache"
            }), 404
        
    except Exception as e:
        logger.error(f"Error al obtener análisis cacheado: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_bp.route('/api/ai/custom-analysis', methods=['POST'])
def run_custom_analysis():
    """Ejecuta análisis personalizado con prompt custom"""
    try:
        if not analyzer:
            return jsonify({
                "success": False,
                "error": "Analizador de IA no inicializado"
            }), 500
        
        data = request.get_json()
        focus_area = data.get('focus_area', '')
        specific_questions = data.get('specific_questions', [])
        
        if not focus_area:
            return jsonify({
                "success": False,
                "error": "Área de enfoque es requerida"
            }), 400
        
        # Crear prompt personalizado
        from ai.prompts import PromptManager
        custom_prompt = PromptManager.get_custom_prompt(focus_area, specific_questions)
        
        # Obtener contexto y datos
        context = analyzer.get_dashboard_context()
        csv_path = os.path.join(analyzer.data_path, "glpi.csv")
        csv_data = analyzer.gemini.prepare_csv_data(csv_path)
        
        # Ejecutar análisis
        result = analyzer.gemini.analyze_with_ai(custom_prompt, csv_data, context)
        
        if result["success"]:
            result["analysis_type"] = "custom"
            result["focus_area"] = focus_area
            result["specific_questions"] = specific_questions
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error en análisis personalizado: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Manejo de errores
@ai_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint no encontrado"
    }), 404

@ai_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Error interno del servidor"
    }), 500

# Middleware para logging de requests
@ai_bp.before_request
def log_request_info():
    logger.debug(f"Request: {request.method} {request.url}")
    if request.get_json():
        logger.debug(f"Request body: {request.get_json()}")

@ai_bp.after_request
def log_response_info(response):
    logger.debug(f"Response: {response.status_code}")
    return response