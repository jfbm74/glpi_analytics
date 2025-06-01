"""
Cliente para Google AI Gemini API - CORREGIDO Y VERIFICADO
"""

import google.generativeai as genai
import os
import pandas as pd
import json
import time
from typing import Dict, Any, Optional, List
import logging

class GeminiClient:
    """Cliente para interactuar con Google AI Gemini"""
    
    def __init__(self, api_key: str = None, model_name: str = "gemini-2.0-flash-exp"):
        """
        Inicializa el cliente de Gemini
        
        Args:
            api_key: API key de Google AI
            model_name: Nombre del modelo a usar
        """
        self.api_key = api_key or os.getenv('GOOGLE_AI_API_KEY')
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        
        if not self.api_key:
            raise ValueError("API key de Google AI es requerida. Configura GOOGLE_AI_API_KEY en el archivo .env")
        
        # Log de configuración
        self.logger.info(f"Inicializando GeminiClient con API key: {self.api_key[:20]}...")
        
        # Configurar Google AI
        genai.configure(api_key=self.api_key)
        
        # Configuración del modelo
        self.generation_config = {
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        self.safety_settings = [
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
        
        try:
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            self.logger.info(f"Cliente Gemini inicializado exitosamente con modelo {self.model_name}")
        except Exception as e:
            self.logger.error(f"Error al inicializar Gemini: {str(e)}")
            raise
    
    def prepare_csv_data(self, csv_path: str, max_rows: int = 1000) -> str:
        """
        Prepara los datos del CSV para el análisis
        
        Args:
            csv_path: Ruta al archivo CSV
            max_rows: Máximo número de filas a incluir
            
        Returns:
            Datos formateados como string
        """
        try:
            # Verificar que el archivo existe
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"Archivo CSV no encontrado: {csv_path}")
            
            self.logger.info(f"Preparando datos CSV desde: {csv_path}")
            
            # Leer CSV
            df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')
            
            # Limitar filas si es necesario
            original_rows = len(df)
            if len(df) > max_rows:
                df = df.head(max_rows)
                self.logger.warning(f"CSV limitado a {max_rows} filas (original: {original_rows} filas)")
            
            # Información básica del dataset
            data_info = {
                "total_rows": len(df),
                "original_rows": original_rows,
                "columns": list(df.columns),
                "summary_stats": {}
            }
            
            # Estadísticas básicas para columnas numéricas y categóricas clave
            key_columns = [
                'Tipo', 'Estado', 'Prioridad', 'Categoría',
                'Asignado a: - Técnico', 'Se superó el tiempo de resolución',
                'Encuesta de satisfacción - Satisfacción'
            ]
            
            for col in key_columns:
                if col in df.columns:
                    try:
                        if df[col].dtype == 'object':
                            data_info["summary_stats"][col] = df[col].value_counts().head(10).to_dict()
                        else:
                            data_info["summary_stats"][col] = {
                                "mean": float(df[col].mean()) if not df[col].isna().all() else 0,
                                "median": float(df[col].median()) if not df[col].isna().all() else 0,
                                "std": float(df[col].std()) if not df[col].isna().all() else 0
                            }
                    except Exception as e:
                        self.logger.warning(f"Error procesando columna {col}: {str(e)}")
                        data_info["summary_stats"][col] = "Error al procesar"
            
            # Convertir a formato de texto estructurado
            formatted_data = f"""
INFORMACIÓN DEL DATASET:
- Total de registros analizados: {data_info['total_rows']} (de {data_info['original_rows']} originales)
- Columnas disponibles: {', '.join(data_info['columns'])}

ESTADÍSTICAS RESUMIDAS:
{json.dumps(data_info['summary_stats'], indent=2, ensure_ascii=False, default=str)}

MUESTRA DE DATOS (primeras 20 filas):
{df.head(20).to_string(index=False)}

DATOS COMPLETOS PARA ANÁLISIS:
{df.to_string(index=False)}
"""
            
            self.logger.info(f"Datos CSV preparados: {len(df)} filas, {len(df.columns)} columnas")
            return formatted_data
            
        except Exception as e:
            self.logger.error(f"Error al preparar datos CSV: {str(e)}")
            raise
    
    def analyze_with_ai(self, prompt: str, csv_data: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Realiza análisis usando Gemini AI
        
        Args:
            prompt: Prompt para el análisis
            csv_data: Datos del CSV formateados
            context: Contexto adicional del dashboard
            
        Returns:
            Resultado del análisis
        """
        try:
            # Construir prompt completo
            full_prompt = f"""
{prompt}

CONTEXTO DEL DASHBOARD:
{json.dumps(context, indent=2, ensure_ascii=False, default=str) if context else 'No disponible'}

DATOS DETALLADOS PARA ANÁLISIS:
{csv_data}

INSTRUCCIONES ESPECÍFICAS:
- Proporciona un análisis exhaustivo y estructurado siguiendo exactamente las secciones solicitadas
- Usa formato Markdown para una mejor presentación
- Incluye insights accionables y recomendaciones específicas
- Considera el contexto de una clínica especializada en fracturas
- Enfócate en métricas relevantes para el sector salud
"""
            
            self.logger.info("Iniciando análisis con Gemini AI...")
            self.logger.debug(f"Prompt length: {len(full_prompt)} caracteres")
            
            start_time = time.time()
            
            # Generar respuesta
            response = self.model.generate_content(full_prompt)
            
            duration = time.time() - start_time
            self.logger.info(f"Análisis completado en {duration:.2f} segundos")
            
            # Procesar respuesta
            if response.text:
                response_length = len(response.text)
                self.logger.info(f"Respuesta recibida: {response_length} caracteres")
                
                return {
                    "success": True,
                    "analysis": response.text,
                    "model_used": self.model_name,
                    "processing_time": duration,
                    "timestamp": time.time(),
                    "prompt_tokens": len(full_prompt.split()),
                    "response_tokens": len(response.text.split()),
                    "response_length": response_length
                }
            else:
                self.logger.warning("No se recibió respuesta del modelo")
                return {
                    "success": False,
                    "error": "No se recibió respuesta del modelo",
                    "model_used": self.model_name
                }
                
        except Exception as e:
            self.logger.error(f"Error en análisis AI: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "model_used": self.model_name,
                "error_type": type(e).__name__
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información del modelo actual
        
        Returns:
            Información del modelo
        """
        try:
            self.logger.info("Obteniendo información del modelo...")
            models = list(genai.list_models())
            current_model = next((m for m in models if self.model_name in m.name), None)
            
            return {
                "model_name": self.model_name,
                "available": current_model is not None,
                "total_models_available": len(models),
                "details": {
                    "name": current_model.name if current_model else "N/A",
                    "description": current_model.description if current_model else "N/A",
                    "input_token_limit": getattr(current_model, 'input_token_limit', 'N/A'),
                    "output_token_limit": getattr(current_model, 'output_token_limit', 'N/A')
                } if current_model else {}
            }
        except Exception as e:
            self.logger.error(f"Error al obtener info del modelo: {str(e)}")
            return {
                "model_name": self.model_name,
                "available": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión con la API
        
        Returns:
            Resultado de la prueba
        """
        try:
            self.logger.info("Probando conexión con Gemini AI...")
            
            test_prompt = "Responde brevemente: 'Conexión exitosa con Gemini AI. Sistema funcionando correctamente.'"
            start_time = time.time()
            
            response = self.model.generate_content(test_prompt)
            duration = time.time() - start_time
            
            if response.text:
                self.logger.info(f"Test de conexión exitoso en {duration:.2f}s")
                return {
                    "success": True,
                    "message": "Conexión exitosa con Gemini AI",
                    "response": response.text,
                    "model": self.model_name,
                    "response_time": duration,
                    "api_key_preview": self.api_key[:20] + "..."
                }
            else:
                self.logger.warning("Test de conexión falló: sin respuesta")
                return {
                    "success": False,
                    "error": "No se recibió respuesta en el test",
                    "model": self.model_name
                }
        except Exception as e:
            self.logger.error(f"Error en test de conexión: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "model": self.model_name,
                "error_type": type(e).__name__
            }