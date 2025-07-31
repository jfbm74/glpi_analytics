#!/usr/bin/env python3
"""
Test script para verificar la funcionalidad de upload de archivos CSV
"""

import requests
import os
import tempfile
import csv
from datetime import datetime

def create_test_csv():
    """Crea un archivo CSV de prueba con datos de ejemplo"""
    
    # Datos de ejemplo con estructura similar a GLPI
    sample_data = [
        {
            'ID': '1001',
            'Tipo': 'Incidencia',
            'Estado': 'Resueltas',
            'Prioridad': 'Alta',
            'Categoría': 'Hardware > Impresoras',
            'Asignado a: - Técnico': 'Juan Pérez',
            'Solicitante - Solicitante': 'María García',
            'Fecha de Apertura': '2024-01-15 09:30:00',
            'Fecha de solución': '2024-01-15 14:20:00',
            'Se superó el tiempo de resolución': 'No',
            'Encuesta de satisfacción - Satisfacción': '4'
        },
        {
            'ID': '1002',
            'Tipo': 'Petición',
            'Estado': 'Abierto',
            'Prioridad': 'Mediana',
            'Categoría': 'Software > Office',
            'Asignado a: - Técnico': 'Ana Rodríguez',
            'Solicitante - Solicitante': 'Carlos López',
            'Fecha de Apertura': '2024-01-16 10:15:00',
            'Fecha de solución': '',
            'Se superó el tiempo de resolución': 'No',
            'Encuesta de satisfacción - Satisfacción': ''
        },
        {
            'ID': '1003',
            'Tipo': 'Incidencia',
            'Estado': 'Cerrado',
            'Prioridad': 'Baja',
            'Categoría': 'Red > Conectividad',
            'Asignado a: - Técnico': '',  # Sin asignar
            'Solicitante - Solicitante': 'Luis Martín',
            'Fecha de Apertura': '2024-01-17 11:45:00',
            'Fecha de solución': '2024-01-18 16:30:00',
            'Se superó el tiempo de resolución': 'Si',
            'Encuesta de satisfacción - Satisfacción': '2'
        }
    ]
    
    # Crear archivo temporal
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
    
    # Escribir datos con delimitador de punto y coma (como GLPI)
    writer = csv.DictWriter(temp_file, fieldnames=sample_data[0].keys(), delimiter=';')
    writer.writeheader()
    writer.writerows(sample_data)
    
    temp_file.close()
    return temp_file.name

def test_upload_endpoint():
    """Prueba el endpoint de upload"""
    
    print("🧪 Iniciando prueba de funcionalidad de upload...")
    
    # Crear archivo CSV de prueba
    csv_file_path = create_test_csv()
    print(f"✅ Archivo CSV de prueba creado: {csv_file_path}")
    
    try:
        # URL del endpoint (asumiendo que el servidor está en localhost:5000)
        upload_url = 'http://localhost:5000/upload-csv' 
        
        # Preparar archivo para upload
        with open(csv_file_path, 'rb') as file:
            files = {'csv_file': ('test_glpi.csv', file, 'text/csv')}
            
            print("📤 Enviando archivo al servidor...")
            
            # Hacer request
            response = requests.post(upload_url, files=files, timeout=30)
            
            print(f"📊 Código de respuesta: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Upload exitoso!")
                    print(f"   Mensaje: {result.get('message')}")
                    
                    if 'file_info' in result:
                        info = result['file_info']
                        print(f"   Archivo: {info.get('filename')}")
                        print(f"   Tamaño: {info.get('size_mb')} MB")
                        print(f"   Columnas: {info.get('columns')}")
                else:
                    print(f"❌ Error en upload: {result.get('error')}")
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Error desconocido')}")
                except:
                    print(f"   Respuesta: {response.text}")
                    
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor.")
        print("   Asegúrate de que el dashboard esté ejecutándose en http://localhost:5000")
    except requests.exceptions.Timeout:
        print("❌ Error: Timeout en la conexión")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        # Limpiar archivo temporal
        if os.path.exists(csv_file_path):
            os.unlink(csv_file_path)
            print("🧹 Archivo temporal eliminado")

def test_file_validation():
    """Prueba validaciones de archivo"""
    
    print("\n🔍 Probando validaciones de archivo...")
    
    # Crear archivo con extensión incorrecta
    temp_txt = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_txt.write("Esto no es un CSV")
    temp_txt.close()
    
    try:
        upload_url = 'http://localhost:5000/upload-csv'
        
        with open(temp_txt.name, 'rb') as file:
            files = {'csv_file': ('test.txt', file, 'text/plain')}
            response = requests.post(upload_url, files=files, timeout=10)
            
            if response.status_code == 400:
                result = response.json()
                if 'Solo se permiten archivos CSV' in result.get('error', ''):
                    print("✅ Validación de extensión funcionando correctamente")
                else:
                    print(f"⚠️  Validación inesperada: {result.get('error')}")
            else:
                print("❌ La validación de extensión no funcionó como esperado")
                
    except Exception as e:
        print(f"❌ Error en prueba de validación: {e}")
    finally:
        os.unlink(temp_txt.name)

if __name__ == '__main__':
    print("=" * 60)
    print("🏥 TEST DE FUNCIONALIDAD DE UPLOAD - DASHBOARD IT")
    print("=" * 60)
    
    test_upload_endpoint()
    test_file_validation()
    
    print("\n" + "=" * 60)
    print("📝 INSTRUCCIONES PARA PRUEBA MANUAL:")
    print("1. Inicia el dashboard con: python run_dashboard.py")
    print("2. Abre http://localhost:5000 en tu navegador")
    print("3. Busca la sección 'Subir Archivo GLPI CSV' en la parte superior")
    print("4. Selecciona un archivo CSV y haz clic en 'Subir Archivo'")
    print("5. Verifica que se muestre el progreso y mensaje de éxito")
    print("6. Confirma que los datos del dashboard se actualicen")
    print("=" * 60)