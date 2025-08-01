#!/usr/bin/env python3
"""
Script para probar las rutas de la API mientras la aplicación está corriendo
"""

import requests
import json

def test_api_routes():
    """Prueba las rutas de la API"""
    
    base_url = "http://localhost:5000"
    
    # Rutas a probar
    routes_to_test = [
        "/api/ai/test-connection",
        "/api/ai/model-info", 
        "/api/ai/history",
        "/api/ai/available-types",
        "/health",
        "/api/config"
    ]
    
    print("🧪 PROBANDO RUTAS DE LA API")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print()
    
    for route in routes_to_test:
        url = f"{base_url}{route}"
        print(f"🔗 Probando: {route}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ JSON válido")
                    if 'success' in data:
                        print(f"   Success: {data['success']}")
                    if 'error' in data:
                        print(f"   Error: {data['error']}")
                except:
                    print(f"   ❌ Respuesta no es JSON válido")
                    print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                    print(f"   Primeros 200 chars: {response.text[:200]}")
            else:
                print(f"   ❌ Error HTTP {response.status_code}")
                print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                print(f"   Primeros 200 chars: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ No se puede conectar - ¿Está corriendo la aplicación?")
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()

def test_post_analyze():
    """Prueba la ruta POST de análisis"""
    
    url = "http://localhost:5000/api/ai/analyze"
    
    print("🧪 PROBANDO RUTA DE ANÁLISIS (POST)")
    print("=" * 60)
    
    # Datos de prueba
    test_data = {
        "analysis_type": "quick"
    }
    
    try:
        response = requests.post(
            url, 
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON válido")
                print(f"Success: {data.get('success', 'unknown')}")
                if not data.get('success'):
                    print(f"Error: {data.get('error', 'unknown')}")
            except:
                print(f"❌ Respuesta no es JSON")
                print(f"Primeros 200 chars: {response.text[:200]}")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🔧 DIAGNÓSTICO DE RUTAS DE LA API")
    print("=" * 60)
    print("Asegúrate de que la aplicación esté corriendo en http://localhost:5000")
    print()
    
    test_api_routes()
    test_post_analyze()