#!/usr/bin/env python3
"""
Tests unitarios para Dashboard IT - Clínica Bonsana
"""

import unittest
import os
import tempfile
import json
from datetime import datetime
import pandas as pd
import sys
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app import TicketAnalyzer, app
    from config import DevelopmentConfig, validate_config
    from utils import validate_csv_structure, analyze_data_quality
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print("Asegúrate de que todos los archivos están en el directorio correcto")
    sys.exit(1)

class TestTicketAnalyzer(unittest.TestCase):
    """Tests para la clase TicketAnalyzer"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear directorio temporal para datos de prueba
        self.test_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.test_dir, 'test_glpi.csv')
        
        # Crear CSV de prueba
        self.create_test_csv()
        
        # Crear analizador
        self.analyzer = TicketAnalyzer(data_path=self.test_dir)
    
    def tearDown(self):
        """Limpieza después de cada test"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_csv(self):
        """Crea un CSV de prueba con datos válidos"""
        test_data = [
            ['ID', 'Título', 'Tipo', 'Categoría', 'Prioridad', 'Estado', 
             'Fecha de Apertura', 'Fecha de solución', 'Se superó el tiempo de resolución',
             'Asignado a: - Técnico', 'Solicitante - Solicitante', 'Elementos asociados',
             'ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución',
             'Encuesta de satisfacción - Satisfacción'],
            ['1', 'Test Ticket 1', 'Incidencia', 'Hardware > PC', 'Alta', 'Resueltas',
             '2025-05-01 10:00', '2025-05-01 12:00', 'No', 'Juan Pérez', 'María García',
             'PC-001', 'INC_ALTO', '5'],
            ['2', 'Test Ticket 2', 'Requerimiento', 'Software > App', 'Mediana', 'Cerrado',
             '2025-05-02 09:00', '2025-05-02 15:00', 'Si', 'Ana López', 'Carlos Ruiz',
             '', 'INC_MEDIO', '4'],
            ['3', 'Test Ticket 3', 'Incidencia', 'Red > Cable', 'Baja', 'En curso (asignada)',
             '2025-05-03 14:00', '', 'No', '', 'Luis Martín', '', 'INC_BAJO', ''],
            ['4', 'Test Ticket 4', 'Requerimiento', 'Hardware > Impresora', 'Alta', 'Resueltas',
             '2025-05-04 08:00', '2025-05-04 10:30', 'No', 'Juan Pérez', 'Sandra Torres',
             'IMP-002', '', '3'],
            ['5', 'Test Ticket 5', 'Incidencia', 'Software > Sistema', 'Mediana', 'Cerrado',
             '2025-05-05 11:00', '2025-05-05 16:00', 'Si', 'Ana López', 'Roberto Silva',
             '', 'INC_MEDIO', '5']
        ]
        
        with open(self.csv_file, 'w', encoding='utf-8', newline='') as f:
            import csv
            writer = csv.writer(f, delimiter=';')
            writer.writerows(test_data)
    
    def test_load_data(self):
        """Test que los datos se cargan correctamente"""
        self.assertIsNotNone(self.analyzer.df)
        self.assertEqual(len(self.analyzer.df), 5)
        self.assertIn('ID', self.analyzer.df.columns)
        self.assertIn('Título', self.analyzer.df.columns)
    
    def test_overall_metrics(self):
        """Test de métricas generales"""
        metrics = self.analyzer.get_overall_metrics()
        
        self.assertEqual(metrics['total_tickets'], 5)
        self.assertEqual(metrics['resolved_tickets'], 4)  # Resueltas + Cerrado
        self.assertEqual(metrics['resolution_rate'], 80.0)  # 4/5 * 100
        self.assertEqual(metrics['backlog'], 1)  # 1 ticket En curso
        
        # SLA compliance: 2 incidencias, 1 con SLA excedido
        # 2 incidencias totales, 1 dentro de SLA = 50%
        self.assertEqual(metrics['sla_compliance'], 50.0)
    
    def test_ticket_distribution(self):
        """Test de distribuciones de tickets"""
        distributions = self.analyzer.get_ticket_distribution()
        
        # Distribución por tipo
        self.assertEqual(distributions['by_type']['Incidencia'], 3)
        self.assertEqual(distributions['by_type']['Requerimiento'], 2)
        
        # Distribución por estado
        self.assertEqual(distributions['by_status']['Resueltas'], 2)
        self.assertEqual(distributions['by_status']['Cerrado'], 2)
        self.assertEqual(distributions['by_status']['En curso (asignada)'], 1)
        
        # Distribución por prioridad
        self.assertEqual(distributions['by_priority']['Alta'], 2)
        self.assertEqual(distributions['by_priority']['Mediana'], 2)
        self.assertEqual(distributions['by_priority']['Baja'], 1)
    
    def test_technician_workload(self):
        """Test de carga de trabajo por técnico"""
        workload = self.analyzer.get_technician_workload()
        
        self.assertEqual(workload['Juan Pérez'], 2)
        self.assertEqual(workload['Ana López'], 2)
        self.assertEqual(workload['Sin Asignar'], 1)
    
    def test_top_requesters(self):
        """Test de principales solicitantes"""
        requesters = self.analyzer.get_top_requesters(top_n=3)
        
        # Verificar que retorna los top solicitantes
        self.assertIsInstance(requesters, dict)
        self.assertLessEqual(len(requesters), 3)
    
    def test_sla_analysis(self):
        """Test de análisis SLA"""
        sla_data = self.analyzer.get_sla_analysis()
        
        self.assertEqual(sla_data['total_incidents'], 3)  # 3 incidencias
        self.assertEqual(sla_data['sla_exceeded'], 2)  # 2 con SLA excedido
        
        # Verificar niveles SLA
        self.assertIn('sla_compliance_by_level', sla_data)
    
    def test_csat_score(self):
        """Test de puntuación CSAT"""
        csat_data = self.analyzer.get_csat_score()
        
        # Debe haber 4 respuestas válidas (valores 5,4,3,5)
        self.assertEqual(csat_data['total_surveys'], 4)
        
        # CSAT promedio debería ser (5+4+3+5)/4 = 4.25
        self.assertAlmostEqual(csat_data['average_csat'], 4.25, places=2)
    
    def test_data_validation_insights(self):
        """Test de insights de validación de datos"""
        insights = self.analyzer.get_data_validation_insights()
        
        # Verificar estructura
        self.assertIn('unassigned_tickets', insights)
        self.assertIn('no_category_tickets', insights)
        self.assertIn('hardware_no_assets', insights)
        
        # Verificar tickets sin asignar (1 ticket)
        self.assertEqual(insights['unassigned_tickets']['count'], 1)
        
        # Verificar tickets de hardware sin assets
        # Ticket 4 es de impresora y tiene asset, ticket 1 es de PC y tiene asset
        # Así que no debería haber problemas
        hardware_issues = insights['hardware_no_assets']['count']
        self.assertIsInstance(hardware_issues, int)

class TestFlaskApp(unittest.TestCase):
    """Tests para la aplicación Flask"""
    
    def setUp(self):
        """Configuración inicial para tests de Flask"""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Crear datos de prueba
        self.test_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.test_dir, 'glpi.csv')
        self.create_minimal_csv()
        
        # Reemplazar analizador global
        import app as app_module
        app_module.analyzer = TicketAnalyzer(data_path=self.test_dir)
    
    def tearDown(self):
        """Limpieza después de tests"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_minimal_csv(self):
        """Crea un CSV mínimo para tests"""
        minimal_data = [
            ['ID', 'Título', 'Tipo', 'Estado', 'Fecha de Apertura'],
            ['1', 'Test', 'Incidencia', 'Resueltas', '2025-05-01 10:00']
        ]
        
        with open(self.csv_file, 'w', encoding='utf-8', newline='') as f:
            import csv
            writer = csv.writer(f, delimiter=';')
            writer.writerows(minimal_data)
    
    def test_main_page(self):
        """Test de la página principal"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard IT', response.data)
        self.assertIn(b'Cl\xc3\xadnica Bonsana', response.data)  # UTF-8 encoded
    
    def test_api_metrics(self):
        """Test del endpoint de métricas"""
        response = self.client.get('/api/metrics')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('total_tickets', data)
        self.assertIn('resolution_rate', data)
    
    def test_api_distributions(self):
        """Test del endpoint de distribuciones"""
        response = self.client.get('/api/distributions')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('by_type', data)
        self.assertIn('by_status', data)
    
    def test_api_technicians(self):
        """Test del endpoint de técnicos"""
        response = self.client.get('/api/technicians')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
    
    def test_api_sla(self):
        """Test del endpoint de SLA"""
        response = self.client.get('/api/sla')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('total_incidents', data)
    
    def test_api_csat(self):
        """Test del endpoint de CSAT"""
        response = self.client.get('/api/csat')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('average_csat', data)
    
    def test_api_validation(self):
        """Test del endpoint de validación"""
        response = self.client.get('/api/validation')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('unassigned_tickets', data)

class TestConfig(unittest.TestCase):
    """Tests para configuración"""
    
    def test_development_config(self):
        """Test de configuración de desarrollo"""
        config = DevelopmentConfig()
        
        self.assertTrue(config.DEBUG)
        self.assertEqual(config.DATA_DIRECTORY, 'data')
        self.assertEqual(config.CSV_DELIMITER, ';')
        self.assertIn('resolution_states', config.METRICS_CONFIG)
    
    def test_config_validation(self):
        """Test de validación de configuración"""
        config = DevelopmentConfig()
        
        # Crear directorio temporal para prueba
        with tempfile.TemporaryDirectory() as temp_dir:
            config.DATA_DIRECTORY = temp_dir
            errors = validate_config(config)
            # No debería haber errores con directorio válido
            self.assertIsInstance(errors, list)

class TestUtils(unittest.TestCase):
    """Tests para utilidades"""
    
    def setUp(self):
        """Configuración para tests de utilidades"""
        self.test_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.test_dir, 'test.csv')
    
    def tearDown(self):
        """Limpieza después de tests"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_valid_csv(self):
        """Crea un CSV válido para pruebas"""
        headers = ['ID', 'Título', 'Tipo', 'Categoría', 'Prioridad', 'Estado', 
                  'Fecha de Apertura', 'Fecha de solución', 'Se superó el tiempo de resolución',
                  'Asignado a: - Técnico', 'Solicitante - Solicitante', 'Elementos asociados',
                  'ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución',
                  'Encuesta de satisfacción - Satisfacción']
        
        data = [['1', 'Test', 'Incidencia', 'Hardware', 'Alta', 'Resueltas',
                '2025-05-01 10:00', '2025-05-01 12:00', 'No', 'Técnico',
                'Usuario', 'PC-001', 'INC_ALTO', '5']]
        
        with open(self.csv_file, 'w', encoding='utf-8', newline='') as f:
            import csv
            writer = csv.writer(f, delimiter=';')
            writer.writerow(headers)
            writer.writerows(data)
    
    def test_validate_csv_structure_valid(self):
        """Test de validación con CSV válido"""
        self.create_valid_csv()
        result = validate_csv_structure(self.csv_file)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_csv_structure_invalid(self):
        """Test de validación con CSV inválido"""
        # Crear CSV con columnas faltantes
        with open(self.csv_file, 'w', encoding='utf-8') as f:
            f.write('ID;Nombre\n1;Test\n')
        
        result = validate_csv_structure(self.csv_file)
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
    
    def test_analyze_data_quality(self):
        """Test de análisis de calidad de datos"""
        self.create_valid_csv()
        result = analyze_data_quality(self.csv_file)
        
        self.assertIn('general', result)
        self.assertIn('completeness', result)
        self.assertEqual(result['general']['total_records'], 1)

class TestIntegration(unittest.TestCase):
    """Tests de integración completos"""
    
    def setUp(self):
        """Configuración para tests de integración"""
        self.test_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.test_dir, 'glpi.csv')
        self.create_complete_test_data()
    
    def tearDown(self):
        """Limpieza después de tests"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_complete_test_data(self):
        """Crea datos de prueba completos"""
        headers = ['ID', 'Título', 'Tipo', 'Categoría', 'Prioridad', 'Estado', 
                  'Fecha de Apertura', 'Fecha de solución', 'Se superó el tiempo de resolución',
                  'Asignado a: - Técnico', 'Solicitante - Solicitante', 'Elementos asociados',
                  'ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución',
                  'Encuesta de satisfacción - Satisfacción']
        
        # Datos diversos para pruebas completas
        test_data = []
        for i in range(1, 21):  # 20 tickets de prueba
            tipo = 'Incidencia' if i % 2 == 0 else 'Requerimiento'
            estado = ['Resueltas', 'Cerrado', 'En curso (asignada)'][i % 3]
            prioridad = ['Alta', 'Mediana', 'Baja'][i % 3]
            
            row = [
                str(i),
                f'Ticket de prueba {i}',
                tipo,
                f'Categoría {i % 5}',
                prioridad,
                estado,
                f'2025-05-{i:02d} 10:00',
                f'2025-05-{i:02d} 15:00' if estado != 'En curso (asignada)' else '',
                'No' if i % 3 == 0 else 'Si',
                f'Técnico {i % 3}' if i % 4 != 0 else '',
                f'Usuario {i}',
                f'EQ-{i:03d}' if i % 2 == 0 else '',
                'INC_ALTO' if tipo == 'Incidencia' else '',
                str((i % 5) + 1) if i % 2 == 0 else ''
            ]
            test_data.append(row)
        
        with open(self.csv_file, 'w', encoding='utf-8', newline='') as f:
            import csv
            writer = csv.writer(f, delimiter=';')
            writer.writerow(headers)
            writer.writerows(test_data)
    
    def test_complete_workflow(self):
        """Test del flujo completo de la aplicación"""
        # Crear analizador
        analyzer = TicketAnalyzer(data_path=self.test_dir)
        
        # Verificar que todos los métodos funcionan
        metrics = analyzer.get_overall_metrics()
        distributions = analyzer.get_ticket_distribution()
        workload = analyzer.get_technician_workload()
        requesters = analyzer.get_top_requesters()
        sla = analyzer.get_sla_analysis()
        csat = analyzer.get_csat_score()
        validation = analyzer.get_data_validation_insights()
        
        # Verificar que todos los resultados son válidos
        self.assertIsInstance(metrics, dict)
        self.assertIsInstance(distributions, dict)
        self.assertIsInstance(workload, dict)
        self.assertIsInstance(requesters, dict)
        self.assertIsInstance(sla, dict)
        self.assertIsInstance(csat, dict)
        self.assertIsInstance(validation, dict)
        
        # Verificar métricas clave
        self.assertEqual(metrics['total_tickets'], 20)
        self.assertGreater(metrics['resolution_rate'], 0)
        self.assertGreaterEqual(metrics['sla_compliance'], 0)

def run_tests():
    """Ejecuta todos los tests"""
    # Configurar logging para tests
    import logging
    logging.basicConfig(level=logging.ERROR)
    
    # Crear suite de tests
    test_suite = unittest.TestSuite()
    
    # Agregar tests
    test_classes = [
        TestTicketAnalyzer,
        TestFlaskApp,
        TestConfig,
        TestUtils,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Retornar True si todos los tests pasaron
    return result.wasSuccessful()

if __name__ == '__main__':
    print("Dashboard IT - Clínica Bonsana")
    print("Ejecutando Tests Unitarios")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ Todos los tests pasaron exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Algunos tests fallaron")
        sys.exit(1)