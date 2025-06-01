"""
Utilidades específicas para el módulo de IA
"""

import os
import re
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

class DataValidator:
    """Validador de datos para análisis de IA"""
    
    @staticmethod
    def validate_csv_structure(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Valida la estructura del DataFrame para análisis
        
        Args:
            df: DataFrame a validar
            
        Returns:
            Resultado de validación con errores y advertencias
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
            }
        }
        
        # Validar columnas requeridas
        required_columns = [
            'ID', 'Título', 'Tipo', 'Estado', 'Fecha de Apertura'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Columnas requeridas faltantes: {missing_columns}")
        
        # Validar tipos de datos
        if 'Fecha de Apertura' in df.columns:
            try:
                pd.to_datetime(df['Fecha de Apertura'], errors='coerce')
            except Exception as e:
                validation_result['warnings'].append(f"Problema con formato de fechas: {str(e)}")
        
        # Validar integridad de datos
        if len(df) == 0:
            validation_result['valid'] = False
            validation_result['errors'].append("DataFrame está vacío")
        
        # Detectar duplicados
        if 'ID' in df.columns:
            duplicates = df['ID'].duplicated().sum()
            if duplicates > 0:
                validation_result['warnings'].append(f"Se encontraron {duplicates} IDs duplicados")
        
        # Validar valores faltantes críticos
        critical_columns = ['Tipo', 'Estado']
        for col in critical_columns:
            if col in df.columns:
                missing_pct = (df[col].isnull().sum() / len(df)) * 100
                if missing_pct > 20:
                    validation_result['warnings'].append(
                        f"Columna '{col}' tiene {missing_pct:.1f}% de valores faltantes"
                    )
        
        return validation_result
    
    @staticmethod
    def clean_text_data(text: str) -> str:
        """
        Limpia texto para análisis
        
        Args:
            text: Texto a limpiar
            
        Returns:
            Texto limpio
        """
        if not isinstance(text, str):
            return str(text) if text is not None else ""
        
        # Remover caracteres especiales problemáticos
        text = re.sub(r'[^\w\s\-.,;:()\[\]@/]', '', text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limitar longitud
        max_length = 1000
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text

class CacheManager:
    """Gestor de cache para análisis de IA"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, data: Any) -> str:
        """Genera clave de cache basada en datos"""
        if isinstance(data, dict):
            content = json.dumps(data, sort_keys=True, default=str)
        else:
            content = str(data)
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos del cache
        
        Args:
            key: Clave del cache
            
        Returns:
            Datos cacheados o None
        """
        try:
            cache_file = self.cache_dir / f"{key}.json"
            
            if not cache_file.exists():
                return None
            
            # Verificar si el cache ha expirado
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - mtime > timedelta(hours=1):
                cache_file.unlink()  # Eliminar cache expirado
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.warning(f"Error al leer cache {key}: {str(e)}")
            return None
    
    def set(self, key: str, data: Dict[str, Any]) -> bool:
        """
        Guarda datos en cache
        
        Args:
            key: Clave del cache
            data: Datos a cachear
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            cache_file = self.cache_dir / f"{key}.json"
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            return True
            
        except Exception as e:
            logger.error(f"Error al guardar cache {key}: {str(e)}")
            return False
    
    def clear_expired(self) -> int:
        """
        Limpia archivos de cache expirados
        
        Returns:
            Número de archivos eliminados
        """
        deleted = 0
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            for cache_file in self.cache_dir.glob("*.json"):
                mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if mtime < cutoff_time:
                    cache_file.unlink()
                    deleted += 1
                    
        except Exception as e:
            logger.error(f"Error al limpiar cache: {str(e)}")
        
        return deleted

class ResponseFormatter:
    """Formateador de respuestas de IA"""
    
    @staticmethod
    def format_markdown_response(text: str) -> str:
        """
        Formatea respuesta markdown para mejor presentación
        
        Args:
            text: Texto en markdown
            
        Returns:
            Texto formateado
        """
        # Asegurar que los headers tengan saltos de línea apropiados
        text = re.sub(r'\n(#{1,6})', r'\n\n\1', text)
        
        # Mejorar formato de listas
        text = re.sub(r'\n(\d+\.)', r'\n\n\1', text)
        text = re.sub(r'\n(-|\*)', r'\n\n\1', text)
        
        # Asegurar espacios después de headers
        text = re.sub(r'(#{1,6}[^\n]+)\n([^\n#])', r'\1\n\n\2', text)
        
        return text.strip()
    
    @staticmethod
    def extract_sections(text: str) -> Dict[str, str]:
        """
        Extrae secciones del análisis basado en headers
        
        Args:
            text: Texto del análisis
            
        Returns:
            Diccionario con secciones
        """
        sections = {}
        current_section = "introduccion"
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            # Detectar headers (# ## ###)
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            
            if header_match:
                # Guardar sección anterior
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Iniciar nueva sección
                header_text = header_match.group(2)
                current_section = re.sub(r'[^\w\s]', '', header_text).lower().replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)
        
        # Guardar última sección
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    @staticmethod
    def generate_summary(text: str, max_sentences: int = 3) -> str:
        """
        Genera resumen del análisis
        
        Args:
            text: Texto completo
            max_sentences: Máximo número de oraciones
            
        Returns:
            Resumen
        """
        # Buscar sección de resumen ejecutivo
        if 'resumen ejecutivo' in text.lower():
            start = text.lower().find('resumen ejecutivo')
            end = text.find('\n##', start)
            if end == -1:
                end = text.find('\n#', start)
            if end != -1:
                summary_section = text[start:end]
            else:
                summary_section = text[start:start+500]
        else:
            # Tomar primeras oraciones
            sentences = re.split(r'[.!?]+', text)
            summary_section = '. '.join(sentences[:max_sentences])
        
        return summary_section.strip()

class MetricsCalculator:
    """Calculadora de métricas para análisis"""
    
    @staticmethod
    def calculate_efficiency_score(metrics: Dict[str, float]) -> float:
        """
        Calcula score de eficiencia basado en métricas
        
        Args:
            metrics: Diccionario con métricas
            
        Returns:
            Score de eficiencia (0-100)
        """
        weights = {
            'resolution_rate': 0.3,
            'sla_compliance': 0.4,
            'avg_resolution_time_score': 0.3
        }
        
        # Normalizar tiempo de resolución (menor es mejor)
        avg_time = metrics.get('avg_resolution_time_hours', 24)
        time_score = max(0, 100 - (avg_time - 4) * 5)  # Penalizar > 4 horas
        
        score_components = {
            'resolution_rate': metrics.get('resolution_rate', 0),
            'sla_compliance': metrics.get('sla_compliance', 0),
            'avg_resolution_time_score': time_score
        }
        
        weighted_score = sum(
            score_components[key] * weight 
            for key, weight in weights.items()
            if key in score_components
        )
        
        return min(100, max(0, weighted_score))
    
    @staticmethod
    def calculate_trend(values: List[float], periods: int = 5) -> Tuple[str, float]:
        """
        Calcula tendencia de una serie de valores
        
        Args:
            values: Lista de valores
            periods: Número de períodos a considerar
            
        Returns:
            Tupla con (tendencia, cambio_porcentual)
        """
        if len(values) < 2:
            return "sin_datos", 0.0
        
        # Tomar últimos períodos
        recent_values = values[-periods:] if len(values) >= periods else values
        
        if len(recent_values) < 2:
            return "estable", 0.0
        
        # Calcular cambio porcentual
        start_value = recent_values[0]
        end_value = recent_values[-1]
        
        if start_value == 0:
            return "sin_referencia", 0.0
        
        change_pct = ((end_value - start_value) / start_value) * 100
        
        # Clasificar tendencia
        if abs(change_pct) < 5:
            trend = "estable"
        elif change_pct > 0:
            trend = "creciente"
        else:
            trend = "decreciente"
        
        return trend, change_pct

class ErrorHandler:
    """Manejador de errores para IA"""
    
    ERROR_CODES = {
        'API_KEY_ERROR': 1001,
        'MODEL_ERROR': 1002,
        'DATA_ERROR': 1003,
        'TIMEOUT_ERROR': 1004,
        'QUOTA_ERROR': 1005,
        'NETWORK_ERROR': 1006,
        'PARSING_ERROR': 1007,
        'VALIDATION_ERROR': 1008
    }
    
    @staticmethod
    def classify_error(error: Exception) -> Tuple[str, int]:
        """
        Clasifica error y retorna código
        
        Args:
            error: Excepción a clasificar
            
        Returns:
            Tupla con (tipo_error, código)
        """
        error_str = str(error).lower()
        
        if 'api key' in error_str or 'authentication' in error_str:
            return 'API_KEY_ERROR', ErrorHandler.ERROR_CODES['API_KEY_ERROR']
        elif 'model' in error_str or 'not found' in error_str:
            return 'MODEL_ERROR', ErrorHandler.ERROR_CODES['MODEL_ERROR']
        elif 'timeout' in error_str:
            return 'TIMEOUT_ERROR', ErrorHandler.ERROR_CODES['TIMEOUT_ERROR']
        elif 'quota' in error_str or 'limit' in error_str:
            return 'QUOTA_ERROR', ErrorHandler.ERROR_CODES['QUOTA_ERROR']
        elif 'network' in error_str or 'connection' in error_str:
            return 'NETWORK_ERROR', ErrorHandler.ERROR_CODES['NETWORK_ERROR']
        elif 'data' in error_str or 'csv' in error_str:
            return 'DATA_ERROR', ErrorHandler.ERROR_CODES['DATA_ERROR']
        else:
            return 'UNKNOWN_ERROR', 9999
    
    @staticmethod
    def get_user_friendly_message(error_type: str) -> str:
        """
        Obtiene mensaje amigable para usuario
        
        Args:
            error_type: Tipo de error
            
        Returns:
            Mensaje para usuario
        """
        messages = {
            'API_KEY_ERROR': 'Error de autenticación con la API de IA. Verifica tu clave de API.',
            'MODEL_ERROR': 'El modelo de IA no está disponible. Intenta con otro modelo.',
            'DATA_ERROR': 'Error en los datos. Verifica que el archivo CSV sea válido.',
            'TIMEOUT_ERROR': 'El análisis tomó demasiado tiempo. Intenta con menos datos.',
            'QUOTA_ERROR': 'Has excedido tu cuota de la API. Espera o mejora tu plan.',
            'NETWORK_ERROR': 'Error de conexión. Verifica tu conexión a internet.',
            'PARSING_ERROR': 'Error al procesar la respuesta de la IA.',
            'VALIDATION_ERROR': 'Los datos no cumplen los requisitos mínimos.'
        }
        
        return messages.get(error_type, 'Error desconocido. Contacta al soporte técnico.')

def create_analysis_report(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea reporte estructurado del análisis
    
    Args:
        analysis_data: Datos del análisis
        
    Returns:
        Reporte estructurado
    """
    formatter = ResponseFormatter()
    
    # Extraer secciones del análisis
    sections = formatter.extract_sections(analysis_data.get('analysis', ''))
    
    # Generar resumen
    summary = formatter.generate_summary(analysis_data.get('analysis', ''))
    
    # Crear metadatos del reporte
    report = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'analysis_type': analysis_data.get('analysis_type', 'unknown'),
            'model_used': analysis_data.get('model_used', 'unknown'),
            'processing_time': analysis_data.get('processing_time', 0),
            'success': analysis_data.get('success', False)
        },
        'summary': summary,
        'sections': sections,
        'raw_analysis': analysis_data.get('analysis', ''),
        'context_used': analysis_data.get('context_used', {}),
        'stats': {
            'word_count': len(analysis_data.get('analysis', '').split()),
            'sections_count': len(sections),
            'response_tokens': analysis_data.get('response_tokens', 0)
        }
    }
    
    return report