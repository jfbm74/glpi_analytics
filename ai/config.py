"""
Configuración avanzada del módulo de IA
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class AnalysisType(Enum):
    """Tipos de análisis disponibles"""
    COMPREHENSIVE = "comprehensive"
    QUICK = "quick"
    TECHNICIAN = "technician"
    SLA = "sla"
    TRENDS = "trends"
    COST = "cost"
    CUSTOM = "custom"

class ModelType(Enum):
    """Modelos de IA disponibles"""
    GEMINI_2_FLASH = "gemini-2.0-flash-exp"
    GEMINI_15_PRO = "gemini-1.5-pro"
    GEMINI_15_FLASH = "gemini-1.5-flash"

@dataclass
class AIConfig:
    """Configuración del módulo de IA"""
    
    # Configuración de API
    api_key: str
    model_name: str = ModelType.GEMINI_2_FLASH.value
    
    # Límites de procesamiento
    max_csv_rows: int = 1000
    max_analysis_size_mb: int = 50
    max_concurrent_analyses: int = 3
    
    # Timeouts y reintentos
    request_timeout: int = 300
    retry_attempts: int = 3
    cache_timeout: int = 3600
    
    # Configuración de generación
    temperature: float = 0.1
    top_p: float = 0.95
    top_k: int = 40
    max_output_tokens: int = 8192
    
    # Directorios
    data_directory: str = "data"
    reports_directory: str = "data/reports"
    cache_directory: str = "data/cache"
    
    # Configuración de exportación
    export_pdf_enabled: bool = True
    export_word_enabled: bool = True
    export_json_enabled: bool = True
    
    # Configuración de seguridad
    enable_content_filtering: bool = True
    enable_audit_logging: bool = True
    
    # Configuración de desarrollo
    debug_mode: bool = False
    mock_responses: bool = False
    log_api_calls: bool = False

    @classmethod
    def from_env(cls) -> 'AIConfig':
        """Crear configuración desde variables de entorno"""
        return cls(
            api_key=os.getenv('GOOGLE_AI_API_KEY', ''),
            model_name=os.getenv('GOOGLE_AI_MODEL', ModelType.GEMINI_2_FLASH.value),
            max_csv_rows=int(os.getenv('AI_MAX_CSV_ROWS', '1000')),
            max_analysis_size_mb=int(os.getenv('MAX_ANALYSIS_SIZE_MB', '50')),
            max_concurrent_analyses=int(os.getenv('MAX_CONCURRENT_ANALYSES', '3')),
            request_timeout=int(os.getenv('AI_REQUEST_TIMEOUT', '300')),
            retry_attempts=int(os.getenv('AI_RETRY_ATTEMPTS', '3')),
            cache_timeout=int(os.getenv('AI_CACHE_TIMEOUT', '3600')),
            data_directory=os.getenv('DATA_DIRECTORY', 'data'),
            reports_directory=os.getenv('REPORTS_DIRECTORY', 'data/reports'),
            cache_directory=os.getenv('CACHE_DIRECTORY', 'data/cache'),
            export_pdf_enabled=os.getenv('EXPORT_PDF_ENABLED', 'True').lower() == 'true',
            export_word_enabled=os.getenv('EXPORT_WORD_ENABLED', 'True').lower() == 'true',
            export_json_enabled=os.getenv('EXPORT_JSON_ENABLED', 'True').lower() == 'true',
            enable_content_filtering=os.getenv('AI_CONTENT_FILTERING', 'True').lower() == 'true',
            enable_audit_logging=os.getenv('AI_AUDIT_LOGGING', 'True').lower() == 'true',
            debug_mode=os.getenv('DEBUG_AI_RESPONSES', 'False').lower() == 'true',
            mock_responses=os.getenv('MOCK_AI_RESPONSES', 'False').lower() == 'true',
            log_api_calls=os.getenv('LOG_AI_CALLS', 'False').lower() == 'true'
        )
    
    def validate(self) -> Dict[str, List[str]]:
        """Validar configuración"""
        errors = {
            'api_key': [],
            'model': [],
            'limits': [],
            'directories': []
        }
        
        # Validar API key
        if not self.api_key:
            errors['api_key'].append("API key es requerida")
        elif not self.api_key.startswith('AIza'):
            errors['api_key'].append("API key no parece válida (debe empezar con 'AIza')")
        
        # Validar modelo
        valid_models = [model.value for model in ModelType]
        if self.model_name not in valid_models:
            errors['model'].append(f"Modelo no válido. Modelos disponibles: {valid_models}")
        
        # Validar límites
        if self.max_csv_rows <= 0:
            errors['limits'].append("max_csv_rows debe ser mayor a 0")
        if self.max_analysis_size_mb <= 0:
            errors['limits'].append("max_analysis_size_mb debe ser mayor a 0")
        if self.request_timeout <= 0:
            errors['limits'].append("request_timeout debe ser mayor a 0")
        
        # Validar directorios
        for directory in [self.data_directory, self.reports_directory, self.cache_directory]:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    errors['directories'].append(f"No se puede crear directorio {directory}: {str(e)}")
        
        # Filtrar errores vacíos
        return {k: v for k, v in errors.items() if v}
    
    def get_generation_config(self) -> Dict:
        """Obtener configuración de generación para Gemini"""
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_output_tokens": self.max_output_tokens,
        }
    
    def get_safety_settings(self) -> List[Dict]:
        """Obtener configuración de seguridad para Gemini"""
        if not self.enable_content_filtering:
            return []
        
        return [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]

class PromptTemplates:
    """Plantillas de prompts predefinidas"""
    
    ANALYSIS_PREFIXES = {
        AnalysisType.COMPREHENSIVE: "Como Director de TI de Clínica Bonsana, realiza un análisis exhaustivo y estratégico",
        AnalysisType.QUICK: "Como Director de TI, proporciona un análisis rápido y conciso",
        AnalysisType.TECHNICIAN: "Como Director de TI, analiza el rendimiento individual de cada técnico",
        AnalysisType.SLA: "Como Director de TI en un entorno clínico crítico, analiza el cumplimiento de SLA",
        AnalysisType.TRENDS: "Como Director de TI, analiza las tendencias temporales",
        AnalysisType.COST: "Como Director de TI, analiza las oportunidades de optimización de costos"
    }
    
    CONTEXT_SUFFIXES = {
        'healthcare': "Considera el contexto de una clínica especializada en fracturas donde la continuidad del servicio es crítica.",
        'compliance': "Evalúa el cumplimiento con regulaciones de salud y seguridad de datos.",
        'efficiency': "Enfócate en eficiencia operacional y optimización de recursos.",
        'strategic': "Proporciona recomendaciones estratégicas para los próximos 6-12 meses."
    }

class ErrorMessages:
    """Mensajes de error estandarizados"""
    
    API_KEY_MISSING = "API key de Google AI no configurada"
    API_KEY_INVALID = "API key de Google AI no válida"
    MODEL_NOT_AVAILABLE = "Modelo de IA no disponible"
    CSV_FILE_NOT_FOUND = "Archivo CSV no encontrado"
    CSV_FILE_TOO_LARGE = "Archivo CSV excede el tamaño máximo permitido"
    ANALYSIS_TIMEOUT = "El análisis excedió el tiempo límite"
    QUOTA_EXCEEDED = "Cuota de API excedida"
    NETWORK_ERROR = "Error de conectividad con la API"
    INVALID_RESPONSE = "Respuesta inválida de la API"
    CONTENT_FILTERED = "Contenido filtrado por políticas de seguridad"
    
    @staticmethod
    def format_error(error_type: str, details: str = "") -> str:
        """Formatear mensaje de error con detalles"""
        base_message = getattr(ErrorMessages, error_type, "Error desconocido")
        if details:
            return f"{base_message}: {details}"
        return base_message

class MetricsConfig:
    """Configuración de métricas y KPIs"""
    
    # Benchmarks de la industria healthcare
    INDUSTRY_BENCHMARKS = {
        'resolution_rate': 95.0,  # %
        'sla_compliance': 98.0,   # %
        'avg_resolution_hours': 24.0,  # horas
        'csat_score': 4.2,        # 1-5
        'first_call_resolution': 75.0,  # %
    }
    
    # Umbrales de alertas
    ALERT_THRESHOLDS = {
        'critical': {
            'resolution_rate': 85.0,
            'sla_compliance': 90.0,
            'csat_score': 3.0
        },
        'warning': {
            'resolution_rate': 90.0,
            'sla_compliance': 95.0,
            'csat_score': 3.5
        }
    }
    
    # Pesos para scores compuestos
    COMPOSITE_WEIGHTS = {
        'efficiency_score': {
            'resolution_rate': 0.3,
            'sla_compliance': 0.4,
            'avg_resolution_time': 0.3
        },
        'quality_score': {
            'csat_score': 0.6,
            'sla_compliance': 0.4
        }
    }

# Instancia global de configuración
config = AIConfig.from_env()