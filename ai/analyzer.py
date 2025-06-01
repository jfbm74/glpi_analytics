"""
Analizador principal de IA para el Dashboard IT
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

from .gemini_client import GeminiClient
from .prompts import PromptManager

class AIAnalyzer:
    """Analizador principal que combina datos del dashboard con análisis de IA"""
    
    def __init__(self, data_path: str = "data", api_key: str = None):
        """
        Inicializa el analizador de IA
        
        Args:
            data_path: Directorio donde se encuentran los datos
            api_key: API key de Google AI
        """
        self.data_path = data_path
        self.logger = logging.getLogger(__name__)
        
        # Inicializar cliente Gemini con el modelo especificado
        self.gemini = GeminiClient(
            api_key=api_key or "AIzaSyALkC-uoOfpS3cB-vnaj8Zor3ccp5MVOBQ",
            model_name="gemini-2.0-flash-exp"  # Modelo más reciente disponible
        )
        
        self.prompt_manager = PromptManager()
        
        # Cache para análisis recientes
        self.analysis_cache = {}
        
    def get_dashboard_context(self) -> Dict[str, Any]:
        """
        Obtiene el contexto actual del dashboard
        
        Returns:
            Contexto con métricas del dashboard
        """
        try:
            # Intentar cargar datos del CSV principal
            csv_path = os.path.join(self.data_path, "glpi.csv")
            if not os.path.exists(csv_path):
                self.logger.warning(f"No se encontró archivo CSV en {csv_path}")
                return {}
            
            df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')
            
            # Calcular métricas básicas
            total_tickets = len(df)
            resolved_tickets = len(df[df['Estado'].isin(['Resueltas', 'Cerrado'])])
            resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0
            
            # Distribución por tipo
            type_distribution = df['Tipo'].value_counts().to_dict()
            
            # Distribución por estado
            status_distribution = df['Estado'].value_counts().to_dict()
            
            # Distribución por prioridad
            priority_distribution = df['Prioridad'].value_counts().to_dict()
            
            # Carga por técnico
            technician_workload = df['Asignado a: - Técnico'].value_counts().to_dict()
            
            # SLA compliance
            sla_exceeded = len(df[df['Se superó el tiempo de resolución'] == 'Si'])
            sla_compliance = ((total_tickets - sla_exceeded) / total_tickets * 100) if total_tickets > 0 else 0
            
            # CSAT
            csat_scores = pd.to_numeric(df['Encuesta de satisfacción - Satisfacción'], errors='coerce').dropna()
            avg_csat = csat_scores.mean() if len(csat_scores) > 0 else 0
            
            context = {
                "timestamp": datetime.now().isoformat(),
                "total_tickets": total_tickets,
                "resolution_rate": round(resolution_rate, 2),
                "sla_compliance": round(sla_compliance, 2),
                "average_csat": round(avg_csat, 2),
                "distributions": {
                    "by_type": type_distribution,
                    "by_status": status_distribution,
                    "by_priority": priority_distribution,
                    "by_technician": technician_workload
                },
                "data_quality": {
                    "total_rows": total_tickets,
                    "columns_count": len(df.columns),
                    "missing_assignments": technician_workload.get('', 0),
                    "sla_exceeded_count": sla_exceeded,
                    "csat_responses": len(csat_scores)
                }
            }
            
            return context
            
        except Exception as e:
            self.logger.error(f"Error al obtener contexto del dashboard: {str(e)}")
            return {}
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Ejecuta análisis exhaustivo completo
        
        Returns:
            Resultado del análisis completo
        """
        try:
            self.logger.info("Iniciando análisis exhaustivo completo...")
            
            # Obtener contexto del dashboard
            context = self.get_dashboard_context()
            
            # Preparar datos del CSV
            csv_path = os.path.join(self.data_path, "glpi.csv")
            csv_data = self.gemini.prepare_csv_data(csv_path)
            
            # Obtener prompt comprehensivo
            prompt = self.prompt_manager.get_comprehensive_analysis_prompt()
            
            # Ejecutar análisis
            result = self.gemini.analyze_with_ai(prompt, csv_data, context)
            
            if result["success"]:
                # Guardar resultado en cache
                cache_key = f"comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.analysis_cache[cache_key] = result
                
                # Agregar metadatos adicionales
                result["analysis_type"] = "comprehensive"
                result["context_used"] = context
                result["cache_key"] = cache_key
                
                self.logger.info("Análisis exhaustivo completado exitosamente")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error en análisis exhaustivo: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "analysis_type": "comprehensive"
            }
    
    def run_quick_analysis(self) -> Dict[str, Any]:
        """
        Ejecuta análisis rápido de KPIs principales
        
        Returns:
            Resultado del análisis rápido
        """
        try:
            self.logger.info("Iniciando análisis rápido...")
            
            # Obtener contexto del dashboard
            context = self.get_dashboard_context()
            
            # Para análisis rápido, usar solo un subconjunto de datos
            csv_path = os.path.join(self.data_path, "glpi.csv")
            csv_data = self.gemini.prepare_csv_data(csv_path, max_rows=200)
            
            # Obtener prompt de análisis rápido
            prompt = self.prompt_manager.get_quick_analysis_prompt()
            
            # Ejecutar análisis
            result = self.gemini.analyze_with_ai(prompt, csv_data, context)
            
            if result["success"]:
                result["analysis_type"] = "quick"
                result["context_used"] = context
                
                self.logger.info("Análisis rápido completado exitosamente")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error en análisis rápido: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "analysis_type": "quick"
            }
    
    def run_custom_analysis(self, analysis_type: str) -> Dict[str, Any]:
        """
        Ejecuta análisis personalizado por tipo
        
        Args:
            analysis_type: Tipo de análisis (technician, sla, trends, cost)
            
        Returns:
            Resultado del análisis personalizado
        """
        try:
            self.logger.info(f"Iniciando análisis personalizado: {analysis_type}")
            
            # Mapear tipos de análisis a prompts
            prompt_mapping = {
                "technician": self.prompt_manager.get_technician_performance_prompt(),
                "sla": self.prompt_manager.get_sla_analysis_prompt(),
                "trends": self.prompt_manager.get_trend_analysis_prompt(),
                "cost": self.prompt_manager.get_cost_optimization_prompt()
            }
            
            if analysis_type not in prompt_mapping:
                return {
                    "success": False,
                    "error": f"Tipo de análisis no válido: {analysis_type}",
                    "available_types": list(prompt_mapping.keys())
                }
            
            # Obtener contexto y datos
            context = self.get_dashboard_context()
            csv_path = os.path.join(self.data_path, "glpi.csv")
            csv_data = self.gemini.prepare_csv_data(csv_path)
            
            # Ejecutar análisis
            prompt = prompt_mapping[analysis_type]
            result = self.gemini.analyze_with_ai(prompt, csv_data, context)
            
            if result["success"]:
                result["analysis_type"] = analysis_type
                result["context_used"] = context
                
                self.logger.info(f"Análisis {analysis_type} completado exitosamente")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error en análisis {analysis_type}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "analysis_type": analysis_type
            }
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """
        Obtiene historial de análisis realizados
        
        Returns:
            Lista de análisis previos
        """
        return [
            {
                "cache_key": key,
                "analysis_type": analysis.get("analysis_type", "unknown"),
                "timestamp": analysis.get("timestamp", "unknown"),
                "processing_time": analysis.get("processing_time", 0),
                "success": analysis.get("success", False)
            }
            for key, analysis in self.analysis_cache.items()
        ]
    
    def get_cached_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene análisis desde cache
        
        Args:
            cache_key: Clave del análisis en cache
            
        Returns:
            Análisis cacheado o None
        """
        return self.analysis_cache.get(cache_key)
    
    def save_analysis_to_file(self, analysis_result: Dict[str, Any], filename: str = None) -> str:
        """
        Guarda análisis en archivo
        
        Args:
            analysis_result: Resultado del análisis
            filename: Nombre del archivo (opcional)
            
        Returns:
            Ruta del archivo guardado
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                analysis_type = analysis_result.get('analysis_type', 'unknown')
                filename = f"analysis_{analysis_type}_{timestamp}.json"
            
            # Crear directorio de reportes si no existe
            reports_dir = os.path.join(self.data_path, "reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            filepath = os.path.join(reports_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Análisis guardado en: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error al guardar análisis: {str(e)}")
            raise
    
    def test_ai_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión con la API de IA
        
        Returns:
            Resultado de la prueba
        """
        return self.gemini.test_connection()
    
    def get_available_analysis_types(self) -> Dict[str, str]:
        """
        Obtiene tipos de análisis disponibles
        
        Returns:
            Diccionario con tipos y descripciones
        """
        return self.prompt_manager.get_available_prompts()
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información del modelo de IA
        
        Returns:
            Información del modelo
        """
        return self.gemini.get_model_info()