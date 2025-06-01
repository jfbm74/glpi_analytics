"""
Cliente para Google AI Gemini API
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
            raise ValueError("API key de Google AI es requerida")
        
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
            self.logger.info(f"Cliente Gemini inicializado con modelo {self.model_name}")
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
            # Leer CSV
            df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')
            
            # Limitar filas si es necesario
            if len(df) > max_rows:
                df = df.head(max_rows)
                self.logger.warning(f"CSV limitado a {max_rows} filas para el análisis")
            
            # Información básica del dataset
            data_info = {
                "total_rows": len(df),
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
                    if df[col].dtype == 'object':
                        data_info["summary_stats"][col] = df[col].value_counts().to_dict()
                    else:
                        data_info["summary_stats"][col] = {
                            "mean": df[col].mean(),
                            "median": df[col].median(),
                            "std": df[col].std()
                        }
            
            # Convertir a formato de texto estructurado
            formatted_data = f"""
INFORMACIÓN DEL DATASET:
- Total de registros: {data_info['total_rows']}
- Columnas disponibles: {', '.join(data_info['columns'])}

ESTADÍSTICAS RESUMIDAS:
{json.dumps(data_info['summary_stats'], indent=2, ensure_ascii=False, default=str)}

MUESTRA DE DATOS (primeras 20 filas):
{df.head(20).to_string(index=False)}

DATOS COMPLETOS DEL CSV:
{df.to_string(index=False)}
"""
            
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

DATOS DEL DASHBOARD:
{json.dumps(context, indent=2, ensure_ascii=False, default=str) if context else 'No disponible'}

DATOS DETALLADOS DEL CSV:
{csv_data}

Por favor, proporciona un análisis exhaustivo y estructurado siguiendo exactamente las secciones solicitadas.
Usa formato Markdown para una mejor presentación.
"""
            
            self.logger.info("Iniciando análisis con Gemini AI...")
            start_time = time.time()
            
            # Generar respuesta
            response = self.model.generate_content(full_prompt)
            
            duration = time.time() - start_time
            self.logger.info(f"Análisis completado en {duration:.2f} segundos")
            
            # Procesar respuesta
            if response.text:
                return {
                    "success": True,
                    "analysis": response.text,
                    "model_used": self.model_name,
                    "processing_time": duration,
                    "timestamp": time.time(),
                    "prompt_tokens": len(full_prompt.split()),
                    "response_tokens": len(response.text.split())
                }
            else:
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
                "model_used": self.model_name
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información del modelo actual
        
        Returns:
            Información del modelo
        """
        try:
            models = list(genai.list_models())
            current_model = next((m for m in models if self.model_name in m.name), None)
            
            return {
                "model_name": self.model_name,
                "available": current_model is not None,
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
                "error": str(e)
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión con la API
        
        Returns:
            Resultado de la prueba
        """
        try:
            test_prompt = "Responde brevemente: '¿Estás funcionando correctamente?'"
            response = self.model.generate_content(test_prompt)
            
            return {
                "success": True,
                "message": "Conexión exitosa con Gemini AI",
                "response": response.text,
                "model": self.model_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.model_name
            }