#!/usr/bin/env python3
"""
Script para diagnosticar problemas con la API key de Google AI
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Verifica el archivo .env en detalle"""
    print("🔍 DIAGNÓSTICO DETALLADO DEL ARCHIVO .env")
    print("=" * 60)
    
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ No se encontró archivo .env")
        return None
    
    print(f"✅ Archivo .env encontrado en: {env_path.absolute()}")
    
    # Leer archivo completo
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Tamaño del archivo: {len(content)} caracteres")
    
    # Buscar líneas relacionadas con Google AI
    lines = content.split('\n')
    api_key_line = None
    
    print("\n🔍 Buscando configuración de Google AI:")
    for i, line in enumerate(lines, 1):
        if 'GOOGLE_AI' in line:
            print(f"   Línea {i}: {line}")
            if line.startswith('GOOGLE_AI_API_KEY='):
                api_key_line = line
    
    if api_key_line:
        api_key = api_key_line.split('=', 1)[1].strip()
        print(f"\n🔑 API Key extraída del .env:")
        print(f"   Línea completa: {api_key_line}")
        print(f"   API Key: {api_key}")
        print(f"   Longitud: {len(api_key)} caracteres")
        print(f"   Primeros 20 chars: {api_key[:20]}...")
        
        # Verificar caracteres especiales
        if any(char in api_key for char in [' ', '\t', '\n', '\r']):
            print("⚠️  ADVERTENCIA: La API key contiene espacios o caracteres especiales")
        
        return api_key.strip()
    else:
        print("❌ No se encontró GOOGLE_AI_API_KEY en .env")
        return None

def check_environment_variables():
    """Verifica variables de entorno"""
    print("\n🌍 VERIFICANDO VARIABLES DE ENTORNO")
    print("=" * 60)
    
    # Verificar si python-dotenv está cargando las variables
    from dotenv import load_dotenv
    
    print("📋 Variables de entorno ANTES de cargar .env:")
    env_before = os.environ.get('GOOGLE_AI_API_KEY', 'NO_DEFINIDA')
    print(f"   GOOGLE_AI_API_KEY = {env_before}")
    
    # Cargar .env
    result = load_dotenv()
    print(f"\n📥 load_dotenv() resultado: {result}")
    
    print("\n📋 Variables de entorno DESPUÉS de cargar .env:")
    env_after = os.environ.get('GOOGLE_AI_API_KEY', 'NO_DEFINIDA')
    print(f"   GOOGLE_AI_API_KEY = {env_after}")
    
    if env_after != 'NO_DEFINIDA':
        print(f"   Longitud: {len(env_after)} caracteres")
        print(f"   Primeros 20 chars: {env_after[:20]}...")
    
    return env_after

def test_api_key_manually(api_key):
    """Prueba la API key manualmente"""
    print(f"\n🧪 PROBANDO API KEY MANUALMENTE")
    print("=" * 60)
    
    if not api_key or api_key == 'NO_DEFINIDA':
        print("❌ No hay API key para probar")
        return
    
    try:
        import google.generativeai as genai
        
        # Configurar con la API key específica
        genai.configure(api_key=api_key)
        print(f"✅ Configuración exitosa con API key: {api_key[:20]}...")
        
        # Intentar listar modelos
        print("📋 Intentando listar modelos...")
        models = list(genai.list_models())
        
        if models:
            print(f"✅ ¡Éxito! Se encontraron {len(models)} modelos")
            print("   Primeros 3 modelos:")
            for model in models[:3]:
                print(f"     - {model.name}")
        else:
            print("⚠️  No se encontraron modelos")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
        # Análisis del error
        error_str = str(e)
        if 'API key not valid' in error_str:
            print("\n🔍 Análisis del error:")
            print("   - La API key es sintácticamente correcta pero no válida")
            print("   - Posibles causas:")
            print("     * API key expirada")
            print("     * API key deshabilitada")
            print("     * Permisos insuficientes")
            print("     * Restricciones de IP/dominio")

def suggest_solutions():
    """Sugiere soluciones"""
    print(f"\n💡 SOLUCIONES SUGERIDAS")
    print("=" * 60)
    print("1. Ve a Google AI Studio: https://aistudio.google.com/app/apikey")
    print("2. Verifica que tu API key esté activa y sin restricciones")
    print("3. Si es necesario, CREA UNA NUEVA API KEY")
    print("4. Copia la nueva API key COMPLETA (sin espacios)")
    print("5. Actualiza el archivo .env:")
    print("   GOOGLE_AI_API_KEY=tu_nueva_api_key_aqui")
    print("6. NO agregues comillas ni espacios extra")
    print("7. Reinicia tu aplicación después del cambio")

if __name__ == "__main__":
    print("🔧 DIAGNÓSTICO COMPLETO DE API KEY")
    print("=" * 60)
    
    # Verificar archivo .env
    api_key_from_file = check_env_file()
    
    # Verificar variables de entorno
    api_key_from_env = check_environment_variables()
    
    # Comparar
    print(f"\n🔄 COMPARACIÓN")
    print("=" * 60)
    print(f"API key del archivo .env: {api_key_from_file[:20] if api_key_from_file else 'None'}...")
    print(f"API key de variables env: {api_key_from_env[:20] if api_key_from_env != 'NO_DEFINIDA' else 'None'}...")
    
    if api_key_from_file and api_key_from_env != 'NO_DEFINIDA':
        if api_key_from_file == api_key_from_env:
            print("✅ Las API keys coinciden")
        else:
            print("❌ Las API keys NO coinciden - hay un problema de carga")
    
    # Probar la API key
    test_key = api_key_from_env if api_key_from_env != 'NO_DEFINIDA' else api_key_from_file
    if test_key:
        test_api_key_manually(test_key)
    
    # Sugerir soluciones
    suggest_solutions()