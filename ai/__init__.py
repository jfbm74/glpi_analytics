"""
Módulo de Análisis de IA para Dashboard IT - Clínica Bonsana
"""

from .gemini_client import GeminiClient
from .analyzer import AIAnalyzer
from .prompts import PromptManager

__version__ = "1.0.0"
__all__ = ["GeminiClient", "AIAnalyzer", "PromptManager"]