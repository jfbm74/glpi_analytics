#!/usr/bin/env python3
"""
Script de inicio para Dashboard IT con IA
"""

import os
import sys
from app import create_app

if __name__ == '__main__':
    # Verificar que el módulo de IA esté disponible
    try:
        from ai.analyzer import AIAnalyzer
        print("✅ Módulo de IA cargado correctamente")
    except ImportError as e:
        print(f"⚠️  Advertencia: Módulo de IA no disponible: {e}")
    
    # Crear y ejecutar aplicación
    app = create_app()
    
    print("🏥 Iniciando Dashboard IT - Clínica Bonsana")
    print("🌐 Accede a: http://localhost:5000")
    print("🤖 Análisis de IA: http://localhost:5000/ai-analysis")
    print("⏹️  Presiona Ctrl+C para detener")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
