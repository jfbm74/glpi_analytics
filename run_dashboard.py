#!/usr/bin/env python3
"""
Script de inicio para Dashboard IT con IA
"""

import os
import sys

def main():
    print("🏥 Dashboard IT - Clínica Bonsana")
    print("🤖 Módulo de IA activado")
    print("="*50)
    
    # Verificar módulo de IA
    try:
        from ai.analyzer import AIAnalyzer
        print("✅ Módulo de IA cargado correctamente")
    except ImportError as e:
        print(f"⚠️  Advertencia: {e}")
    
    # Importar y ejecutar aplicación
    try:
        # Aquí deberías importar tu app principal
        # from app import create_app
        # app = create_app()
        
        print("\n🌐 Para iniciar el dashboard:")
        print("   1. Implementa tu app.py principal")
        print("   2. Configura las rutas de IA")
        print("   3. Ejecuta: python app.py")
        print("\n🔗 URLs disponibles:")
        print("   - Dashboard: http://localhost:5000")
        print("   - Análisis IA: http://localhost:5000/ai-analysis")
        
    except ImportError:
        print("\n📝 Próximos pasos:")
        print("   1. Crea tu archivo app.py principal")
        print("   2. Integra las rutas de IA")
        print("   3. Configura tus templates")

if __name__ == '__main__':
    main()
