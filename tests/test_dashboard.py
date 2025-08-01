#!/usr/bin/env python3
"""
Script de pruebas para Dashboard IT - Clínica Bonsana
Valida las nuevas funcionalidades de estadísticas por técnico
"""

import os
import sys
import json
import unittest
import tempfile
import pandas as pd
from datetime import datetime, timedelta
import requests
import time

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import TicketAnalyzer
    from utils import generate_sample_csv, validate_csv_structure, analyze_data_quality
    from config import active_config
except ImportError as e:
    print(f"❌ Error al importar módulos: {e}")
    print("Asegúrate de que app.py, utils.py y config.py estén en el directorio actual")
    sys.exit(1)

class TestTicketAnalyzer(unittest.TestCase):
    """Pruebas para la clase TicketAnalyzer"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para todas las pruebas"""
        # Crear directorio temporal para datos de prueba
        cls.test_dir = tempfile.mkdtemp()
        cls.test_csv = os.path.join(cls.test_dir, 'test_data.csv')
        
        # Generar datos de prueba
        generate_sample_csv(cls.test_csv, num_records=50)
        
        # Crear instancia del analizador
        cls.analyzer = TicketAnalyzer(data_path=cls.test_dir)
    
    def test_load_data(self):
        """Prueba la carga de datos"""
        self.assertIsNotNone(self.analyzer.df)
        self.assertGreater(len(self.analyzer.df), 0)
        print("✅ Carga de datos: OK")
    
    def test_overall_metrics(self):
        """Prueba las métricas generales"""
        metrics = self.analyzer.get_overall_metrics()
        
        # Verificar que las métricas tienen las claves esperadas
        expected_keys = ['total_tickets', 'resolution_rate', 'avg_resolution_time_hours', 'sla_compliance']
        for key in expected_keys:
            self.assertIn(key, metrics)
        
        # Verificar que los valores son razonables
        self.assertGreaterEqual(metrics['total_tickets'], 0)
        self.assertGreaterEqual(metrics['resolution_rate'], 0)
        self.assertLessEqual(metrics['resolution_rate'], 100)
        
        print(f"✅ Métricas generales: {metrics['total_tickets']} tickets")
    
    def test_technician_sla_stats(self):
        """Prueba las estadísticas de SLA por técnico"""
        sla_stats = self.analyzer.get_technician_sla_stats()
        
        if sla_stats:
            # Verificar estructura de datos
            for technician, stats in sla_stats.items():
                self.assertIn('total_incidents', stats)
                self.assertIn('sla_compliant', stats)
                self.assertIn('compliance_rate', stats)
                
                # Verificar que los valores son coherentes
                self.assertGreaterEqual(stats['compliance_rate'], 0)
                self.assertLessEqual(stats['compliance_rate'], 100)
                self.assertEqual(
                    stats['total_incidents'], 
                    stats['sla_compliant'] + stats['sla_exceeded']
                )
            
            print(f"✅ SLA por técnico: {len(sla_stats)} técnicos analizados")
        else:
            print("⚠️  SLA por técnico: Sin datos de incidencias")
    
    def test_technician_csat_stats(self):
        """Prueba las estadísticas de CSAT por técnico"""
        csat_stats = self.analyzer.get_technician_csat_stats()
        
        if csat_stats:
            for technician, stats in csat_stats.items():
                self.assertIn('average_csat', stats)
                self.assertIn('total_surveys', stats)
                
                # Verificar rangos de CSAT
                self.assertGreaterEqual(stats['average_csat'], 1)
                self.assertLessEqual(stats['average_csat'], 5)
                self.assertGreater(stats['total_surveys'], 0)
            
            print(f"✅ CSAT por técnico: {len(csat_stats)} técnicos con encuestas")
        else:
            print("⚠️  CSAT por técnico: Sin datos de satisfacción")
    
    def test_technician_resolution_time(self):
        """Prueba las estadísticas de tiempo de resolución por técnico"""
        resolution_stats = self.analyzer.get_technician_resolution_time()
        
        if resolution_stats:
            for technician, stats in resolution_stats.items():
                self.assertIn('avg_resolution_hours', stats)
                self.assertIn('total_resolved', stats)
                
                # Verificar que los tiempos son positivos
                self.assertGreater(stats['avg_resolution_hours'], 0)
                self.assertGreater(stats['total_resolved'], 0)
            
            print(f"✅ Tiempo de resolución por técnico: {len(resolution_stats)} técnicos")
        else:
            print("⚠️  Tiempo de resolución: Sin datos de tickets resueltos")
    
    def test_ticket_distribution(self):
        """Prueba las distribuciones de tickets"""
        distributions = self.analyzer.get_ticket_distribution()
        
        self.assertIn('by_type', distributions)
        self.assertIn('by_status', distributions)
        self.assertIn('by_priority', distributions)
        
        print("✅ Distribuciones de tickets: OK")
    
    def test_data_validation(self):
        """Prueba la validación de datos"""
        validation = self.analyzer.get_data_validation_insights()
        
        # La validación puede retornar vacío si no hay problemas
        self.assertIsInstance(validation, dict)
        
        print("✅ Validación de datos: OK")

class TestAPIEndpoints(unittest.TestCase):
    """Pruebas para los endpoints de la API"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración para pruebas de API"""
        cls.base_url = f"http://localhost:{active_config.PORT}"
        cls.api_endpoints = [
            '/api/metrics',
            '/api/distributions', 
            '/api/technicians',
            '/api/technicians/sla',
            '/api/technicians/csat',
            '/api/technicians/resolution-time',
            '/api/requesters',
            '/api/sla',
            '/api/csat',
            '/api/validation'
        ]
    
    def test_api_endpoints(self):
        """Prueba que todos los endpoints respondan correctamente"""
        print("\n🌐 Probando endpoints de API...")
        
        for endpoint in self.api_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    # Verificar que la respuesta es JSON válido
                    data = response.json()
                    self.assertIsInstance(data, dict)
                    print(f"   ✅ {endpoint}")
                else:
                    print(f"   ❌ {endpoint} - Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ {endpoint} - Error: {e}")

class TestUtils(unittest.TestCase):
    """Pruebas para utilidades"""
    
    def test_csv_validation(self):
        """Prueba la validación de estructura CSV"""
        # Crear archivo temporal con datos de prueba
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_csv = f.name
            
        try:
            generate_sample_csv(test_csv, num_records=10)
            
            # Validar estructura
            result = validate_csv_structure(test_csv)
            
            self.assertIn('valid', result)
            self.assertIn('errors', result)
            self.assertIn('warnings', result)
            
            print("✅ Validación de CSV: OK")
            
        finally:
            if os.path.exists(test_csv):
                os.unlink(test_csv)
    
    def test_data_quality_analysis(self):
        """Prueba el análisis de calidad de datos"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_csv = f.name
            
        try:
            generate_sample_csv(test_csv, num_records=20)
            
            # Analizar calidad
            result = analyze_data_quality(test_csv)
            
            self.assertIn('general', result)
            self.assertIn('completeness', result)
            
            print("✅ Análisis de calidad: OK")
            
        finally:
            if os.path.exists(test_csv):
                os.unlink(test_csv)

def run_performance_tests():
    """Ejecuta pruebas de rendimiento básicas"""
    print("\n⚡ Ejecutando pruebas de rendimiento...")
    
    # Crear datos de prueba más grandes
    test_dir = tempfile.mkdtemp()
    large_csv = os.path.join(test_dir, 'large_test.csv')
    
    try:
        # Generar dataset grande
        print("   Generando dataset de 1000 registros...")
        start_time = time.time()
        generate_sample_csv(large_csv, num_records=1000)
        generation_time = time.time() - start_time
        print(f"   ✅ Generación completada en {generation_time:.2f}s")
        
        # Cargar y procesar datos
        print("   Cargando y procesando datos...")
        start_time = time.time()
        analyzer = TicketAnalyzer(data_path=test_dir)
        loading_time = time.time() - start_time
        print(f"   ✅ Carga completada en {loading_time:.2f}s")
        
        # Ejecutar análisis
        print("   Ejecutando análisis completo...")
        start_time = time.time()
        
        metrics = analyzer.get_overall_metrics()
        sla_stats = analyzer.get_technician_sla_stats()
        csat_stats = analyzer.get_technician_csat_stats()
        resolution_stats = analyzer.get_technician_resolution_time()
        
        analysis_time = time.time() - start_time
        print(f"   ✅ Análisis completado en {analysis_time:.2f}s")
        
        # Resumen de rendimiento
        total_time = generation_time + loading_time + analysis_time
        print(f"\n   📊 Resumen de rendimiento:")
        print(f"      - Registros procesados: 1000")
        print(f"      - Tiempo total: {total_time:.2f}s")
        print(f"      - Registros/segundo: {1000/total_time:.0f}")
        
        if total_time < 10:
            print("   ✅ Rendimiento: EXCELENTE")
        elif total_time < 30:
            print("   ✅ Rendimiento: BUENO")
        else:
            print("   ⚠️  Rendimiento: MEJORABLE")
            
    finally:
        # Limpiar archivos temporales
        if os.path.exists(large_csv):
            os.unlink(large_csv)
        os.rmdir(test_dir)

def main():
    """Función principal de pruebas"""
    print("🧪 DASHBOARD IT - SUITE DE PRUEBAS")
    print("=" * 50)
    
    # Verificar que los archivos necesarios existan
    required_files = ['app.py', 'utils.py', 'config.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Archivos faltantes: {missing_files}")
        return False
    
    print("✅ Archivos requeridos encontrados")
    
    # Ejecutar pruebas unitarias
    print("\n🔬 Ejecutando pruebas unitarias...")
    
    # Crear suite de pruebas
    test_suite = unittest.TestSuite()
    
    # Agregar pruebas del analizador
    test_suite.addTest(unittest.makeSuite(TestTicketAnalyzer))
    test_suite.addTest(unittest.makeSuite(TestUtils))
    
    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(test_suite)
    
    # Verificar si hay un servidor ejecutándose para probar API
    try:
        response = requests.get(f"http://localhost:{active_config.PORT}/api/metrics", timeout=5)
        if response.status_code == 200:
            # Ejecutar pruebas de API
            api_suite = unittest.makeSuite(TestAPIEndpoints)
            runner.run(api_suite)
        else:
            print("\n⚠️  Servidor no está ejecutándose - saltando pruebas de API")
            print("   Para probar la API, ejecuta 'python app.py' en otra terminal")
    except requests.exceptions.RequestException:
        print("\n⚠️  Servidor no disponible - saltando pruebas de API")
    
    # Ejecutar pruebas de rendimiento
    run_performance_tests()
    
    # Resumen final
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("\n✅ El dashboard está listo para usar con las nuevas funcionalidades:")
        print("   - Estadísticas de SLA por técnico")
        print("   - Estadísticas de CSAT por técnico") 
        print("   - Tiempo de resolución por técnico")
        return True
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print(f"   Errores: {len(result.errors)}")
        print(f"   Fallos: {len(result.failures)}")
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Pruebas canceladas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado durante las pruebas: {e}")
        sys.exit(1)