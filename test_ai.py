#!/usr/bin/env python3
"""
Tests específicos para la funcionalidad de IA
Dashboard IT - Clínica Bonsana
"""

import unittest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
from dotenv import load_dotenv

# Agregar el directorio raíz al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Cargar variables de entorno
load_dotenv()

class TestAIConfiguration(unittest.TestCase):
    """Tests para configuración de IA"""
    
    def setUp(self):
        """Setup para tests de configuración"""
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        """Limpieza después de tests"""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_config_ai_enabled(self):
        """Test configuración con IA habilitada"""
        os.environ['AI_ANALYSIS_ENABLED'] = 'True'
        os.environ['GOOGLE_AI_API_KEY'] = 'test-api-key'
        
        from config import get_config
        config = get_config()
        
        self.assertTrue(config.AI_ANALYSIS_ENABLED)
        self.assertEqual(config.GOOGLE_AI_API_KEY, 'test-api-key')
        self.assertEqual(config.GOOGLE_AI_MODEL, 'gemini-1.5-pro')
    
    def test_config_ai_disabled(self):
        """Test configuración con IA deshabilitada"""
        os.environ['AI_ANALYSIS_ENABLED'] = 'False'
        
        from config import get_config
        config = get_config()
        
        self.assertFalse(config.AI_ANALYSIS_ENABLED)
    
    def test_prompt_template(self):
        """Test del template de prompt"""
        from config import get_config
        config = get_config()
        
        prompt_template = config.AI_CONFIG['prompt_template']
        
        # Verificar que contiene elementos clave
        self.assertIn('Director de Tecnología', prompt_template)
        self.assertIn('Clínica Bonsana', prompt_template)
        self.assertIn('sector salud', prompt_template)
        self.assertIn('{csv_data}', prompt_template)

class TestAIAnalysisService(unittest.TestCase):
    """Tests para el servicio de análisis IA"""
    
    def setUp(self):
        """Setup para tests del servicio IA"""
        self.test_dir = tempfile.mkdtemp()
        self.test_csv = os.path.join(self.test_dir, 'test.csv')
        self.create_test_csv()
        
        # Mock de configuración
        self.config_patch = patch('app.config')
        self.mock_config = self.config_patch.start()
        self.mock_config.AI_ANALYSIS_ENABLED = True
        self.mock_config.GOOGLE_AI_API_KEY = 'test-api-key'
        self.mock_config.GOOGLE_AI_MODEL = 'gemini-1.5-pro'
        self.mock_config.AI_CONFIG = {
            'max_csv_size_mb': 10,
            'prompt_template': 'Test prompt: {csv_data}'
        }
    
    def tearDown(self):
        """Limpieza después de tests"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
        self.config_patch.stop()
    
    def create_test_csv(self):
        """Crea un CSV de prueba"""
        test_data = """ID;Título;Tipo;Estado;Fecha de Apertura
1;Test Ticket 1;Incidencia;Resueltas;2025-05-01 10:00
2;Test Ticket 2;Requerimiento;Cerrado;2025-05-02 09:00"""
        
        with open(self.test_csv, 'w', encoding='utf-8') as f:
            f.write(test_data)
    
    @patch('app.genai')
    def test_ai_service_initialization(self, mock_genai):
        """Test inicialización del servicio IA"""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        from app import AIAnalysisService
        service = AIAnalysisService()
        
        self.assertIsNotNone(service.model)
        mock_genai.configure.assert_called_with(api_key='test-api-key')
        mock_genai.GenerativeModel.assert_called_with('gemini-1.5-pro')
    
    @patch('app.genai')
    def test_ai_service_not_available(self, mock_genai):
        """Test servicio IA no disponible"""
        mock_genai.GenerativeModel.side_effect = Exception("API Error")
        
        from app import AIAnalysisService
        service = AIAnalysisService()
        
        self.assertFalse(service.is_available())
    
    @patch('app.genai')
    def test_prepare_csv_data(self, mock_genai):
        """Test preparación de datos CSV"""
        mock_genai.GenerativeModel.return_value = MagicMock()
        
        from app import AIAnalysisService
        service = AIAnalysisService()
        
        csv_string = service.prepare_csv_data(self.test_csv)
        
        self.assertIn('ID;Título;Tipo;Estado;Fecha de Apertura', csv_string)
        self.assertIn('Test Ticket 1', csv_string)
    
    @patch('app.genai')
    def test_csv_too_large(self, mock_genai):
        """Test archivo CSV muy grande"""
        mock_genai.GenerativeModel.return_value = MagicMock()
        
        # Crear archivo grande
        large_csv = os.path.join(self.test_dir, 'large.csv')
        with open(large_csv, 'w') as f:
            # Simular archivo de más de 10MB
            f.write('x' * (11 * 1024 * 1024))  # 11MB
        
        from app import AIAnalysisService
        service = AIAnalysisService()
        
        with self.assertRaises(ValueError):
            service.prepare_csv_data(large_csv)
    
    @patch('app.genai')
    def test_analyze_tickets_success(self, mock_genai):
        """Test análisis exitoso de tickets"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Análisis de prueba completado"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        from app import AIAnalysisService
        service = AIAnalysisService()
        
        result = service.analyze_tickets(self.test_csv)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['analysis'], "Análisis de prueba completado")
        self.assertIn('timestamp', result)
        self.assertIn('model_used', result)
    
    @patch('app.genai')
    def test_analyze_tickets_error(self, mock_genai):
        """Test error en análisis de tickets"""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_model
        
        from app import AIAnalysisService
        service = AIAnalysisService()
        
        result = service.analyze_tickets(self.test_csv)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('timestamp', result)

class TestAIEndpoints(unittest.TestCase):
    """Tests para endpoints de IA"""
    
    def setUp(self):
        """Setup para tests de endpoints"""
        # Crear datos de prueba
        self.test_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.test_dir, 'glpi.csv')
        self.create_test_csv()
        
        # Configurar app para testing
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['AI_ANALYSIS_ENABLED'] = 'True'
        os.environ['GOOGLE_AI_API_KEY'] = 'test-api-key'
        
        from app import app
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def tearDown(self):
        """Limpieza después de tests"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_csv(self):
        """Crea CSV de prueba para endpoints"""
        test_data = """ID;Título;Tipo;Estado;Fecha de Apertura
1;Test;Incidencia;Resueltas;2025-05-01 10:00"""
        
        with open(self.csv_file, 'w', encoding='utf-8') as f:
            f.write(test_data)
    
    def test_ai_status_endpoint(self):
        """Test endpoint de estado IA"""
        response = self.client.get('/api/ai/status')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('ai_enabled', data)
        self.assertIn('api_key_configured', data)
        self.assertIn('model', data)
        self.assertIn('service_available', data)
    
    @patch('app.ai_service')
    def test_ai_analyze_endpoint_success(self, mock_ai_service):
        """Test endpoint de análisis exitoso"""
        # Mock del servicio IA
        mock_ai_service.is_available.return_value = True
        mock_ai_service.analyze_tickets.return_value = {
            'success': True,
            'analysis': 'Test analysis',
            'timestamp': '2025-05-29T10:00:00',
            'model_used': 'gemini-1.5-pro',
            'csv_rows_analyzed': 1
        }
        
        # Mock del analizador para que encuentre el CSV
        with patch('app.analyzer') as mock_analyzer:
            mock_analyzer.get_csv_path.return_value = self.csv_file
            
            response = self.client.post('/api/ai/analyze')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['analysis'], 'Test analysis')
    
    @patch('app.ai_service')
    def test_ai_analyze_endpoint_service_unavailable(self, mock_ai_service):
        """Test endpoint cuando servicio IA no está disponible"""
        mock_ai_service.is_available.return_value = False
        
        response = self.client.post('/api/ai/analyze')
        self.assertEqual(response.status_code, 503)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('no disponible', data['error'])
    
    @patch('app.ai_service')
    def test_ai_analyze_endpoint_no_csv(self, mock_ai_service):
        """Test endpoint sin archivo CSV"""
        mock_ai_service.is_available.return_value = True
        
        with patch('app.analyzer') as mock_analyzer:
            mock_analyzer.get_csv_path.return_value = None
            
            response = self.client.post('/api/ai/analyze')
            self.assertEqual(response.status_code, 404)
            
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('No se encontró archivo CSV', data['error'])

class TestAIIntegration(unittest.TestCase):
    """Tests de integración para funcionalidad IA"""
    
    @unittest.skipIf(not os.getenv('GOOGLE_AI_API_KEY'), "API Key no disponible")
    def test_real_ai_analysis(self):
        """Test con Google AI Studio real (requiere API key)"""
        from app import AIAnalysisService
        
        # Crear CSV de prueba pequeño
        test_csv = self.create_minimal_csv()
        
        try:
            service = AIAnalysisService()
            
            if service.is_available():
                result = service.analyze_tickets(test_csv)
                
                self.assertTrue(result['success'])
                self.assertIn('analysis', result)
                self.assertIn('timestamp', result)
                self.assertGreater(len(result['analysis']), 100)  # Debe ser un análisis sustancial
            else:
                self.skipTest("Servicio AI no disponible")
                
        finally:
            # Limpiar archivo de prueba
            if os.path.exists(test_csv):
                os.remove(test_csv)
    
    def create_minimal_csv(self):
        """Crea CSV mínimo para prueba real"""
        import tempfile
        
        test_data = """ID;Título;Tipo;Categoría;Prioridad;Estado;Fecha de Apertura;Fecha de solución;Se superó el tiempo de resolución;Asignado a: - Técnico;Solicitante - Solicitante;Elementos asociados;ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución;Encuesta de satisfacción - Satisfacción
1;Problema impresora oficina;Incidencia;Hardware > Impresora;Alta;Resueltas;2025-05-01 09:00;2025-05-01 11:30;No;Juan Pérez;Dr. García;IMP-001;INC_ALTO;5
2;Instalación nuevo software;Requerimiento;Software > Aplicación;Mediana;Cerrado;2025-05-02 14:00;2025-05-03 10:00;Si;Ana López;Enfermera Silva;;REQ_MEDIO;4
3;Falla de red en consultorios;Incidencia;Red > Conectividad;Alta;En curso (asignada);2025-05-03 16:00;;No;Carlos Ruiz;Dr. Martínez;SW-005;INC_ALTO;
4;Actualización sistema médico;Requerimiento;Software > Sistema;Alta;Resueltas;2025-05-04 08:00;2025-05-04 18:00;No;Juan Pérez;Administración;SRV-MED;REQ_ALTO;5
5;Mantenimiento computadores;Incidencia;Hardware > Computador;Baja;Cerrado;2025-05-05 13:00;2025-05-05 15:00;No;Ana López;Recepción;PC-003;INC_BAJO;3"""
        
        fd, temp_path = tempfile.mkstemp(suffix='.csv', text=True)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(test_data)
        
        return temp_path

class TestAIValidation(unittest.TestCase):
    """Tests de validación para funcionalidad IA"""
    
    def test_prompt_template_validation(self):
        """Test validación del template de prompt"""
        from config import get_config
        config = get_config()
        
        prompt_template = config.AI_CONFIG['prompt_template']
        
        # Verificar elementos requeridos
        required_elements = [
            'Director de Tecnología',
            'Clínica Bonsana',
            'sector salud',
            'healthcare',
            'ANÁLISIS DE RENDIMIENTO',
            'BENCHMARKING',
            'PLAN DE ACCIÓN',
            '{csv_data}'
        ]
        
        for element in required_elements:
            self.assertIn(element, prompt_template, f"Elemento faltante: {element}")
    
    def test_csv_size_validation(self):
        """Test validación de tamaño de CSV"""
        from config import get_config
        config = get_config()
        
        max_size = config.AI_CONFIG['max_csv_size_mb']
        self.assertIsInstance(max_size, int)
        self.assertGreater(max_size, 0)
        self.assertLessEqual(max_size, 50)  # Máximo razonable
    
    def test_model_name_validation(self):
        """Test validación del nombre del modelo"""
        from config import get_config
        config = get_config()
        
        model_name = config.GOOGLE_AI_MODEL
        self.assertIsInstance(model_name, str)
        self.assertGreater(len(model_name), 0)
        
        # Debe ser un modelo Gemini válido
        valid_models = ['gemini-pro', 'gemini-1.5-pro', 'gemini-1.0-pro']
        self.assertTrue(any(valid_model in model_name for valid_model in valid_models))

def run_ai_tests():
    """Ejecuta todos los tests de IA"""
    print("🤖 Ejecutando Tests de Funcionalidad IA")
    print("=" * 50)
    
    # Crear suite de tests
    test_suite = unittest.TestSuite()
    
    test_classes = [
        TestAIConfiguration,
        TestAIAnalysisService,
        TestAIEndpoints,
        TestAIValidation,
        TestAIIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

def check_ai_prerequisites():
    """Verifica que los prerrequisitos para IA estén disponibles"""
    print("\n🔍 Verificando Prerrequisitos para IA")
    print("-" * 40)
    
    issues = []
    
    # Verificar instalación de google-generativeai
    try:
        import google.generativeai as genai
        print("✅ google-generativeai - Instalado")
    except ImportError:
        issues.append("❌ google-generativeai no instalado")
        print("❌ google-generativeai - No instalado")
    
    # Verificar API key
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if api_key:
        print("✅ GOOGLE_AI_API_KEY - Configurada")
    else:
        issues.append("❌ GOOGLE_AI_API_KEY no configurada")
        print("❌ GOOGLE_AI_API_KEY - No configurada")
    
    # Verificar archivo .env
    env_file = Path('.env')
    if env_file.exists():
        print("✅ Archivo .env - Existe")
    else:
        issues.append("⚠️  Archivo .env no existe")
        print("⚠️  Archivo .env - No existe")
    
    # Verificar configuración
    try:
        from config import get_config
        config = get_config()
        if config.AI_ANALYSIS_ENABLED:
            print("✅ AI_ANALYSIS_ENABLED - Habilitado")
        else:
            issues.append("⚠️  AI_ANALYSIS_ENABLED deshabilitado")
            print("⚠️  AI_ANALYSIS_ENABLED - Deshabilitado")
    except Exception as e:
        issues.append(f"❌ Error cargando configuración: {e}")
        print(f"❌ Error cargando configuración: {e}")
    
    if issues:
        print(f"\n⚠️  Se encontraron {len(issues)} problemas:")
        for issue in issues:
            print(f"   {issue}")
        print("\n💡 Ejecuta 'python setup_ai.py' para configurar automáticamente")
        return False
    else:
        print("\n✅ Todos los prerrequisitos están disponibles")
        return True

if __name__ == '__main__':
    print("Dashboard IT - Clínica Bonsana")
    print("Tests de Funcionalidad IA")
    print("=" * 50)
    
    # Verificar prerrequisitos
    if not check_ai_prerequisites():
        print("\n❌ No se pueden ejecutar los tests sin los prerrequisitos")
        print("Ejecuta 'python setup_ai.py' primero")
        sys.exit(1)
    
    # Ejecutar tests
    success = run_ai_tests()
    
    if success:
        print("\n✅ Todos los tests de IA pasaron exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Algunos tests de IA fallaron")
        sys.exit(1)