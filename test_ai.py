#!/usr/bin/env python3
"""
Tests básicos para el módulo de IA
Dashboard IT - Clínica Bonsana
"""

import os
import sys
import unittest
import pandas as pd
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar módulos de IA
try:
    from ai.config import AIConfig, AnalysisType
    from ai.gemini_client import GeminiClient
    from ai.analyzer import AIAnalyzer
    from ai.prompts import PromptManager
    from ai.utils import DataValidator, CacheManager, ResponseFormatter, MetricsCalculator
except ImportError as e:
    print(f"Error al importar módulos de IA: {e}")
    print("Asegúrate de que el módulo ai/ esté disponible")
    sys.exit(1)

class TestAIConfig(unittest.TestCase):
    """Tests para configuración de IA"""
    
    def test_config_creation(self):
        """Test creación de configuración"""
        config = AIConfig(
            api_key="test_key",
            model_name="gemini-2.0-flash-exp"
        )
        
        self.assertEqual(config.api_key, "test_key")
        self.assertEqual(config.model_name, "gemini-2.0-flash-exp")
        self.assertEqual(config.max_csv_rows, 1000)
    
    def test_config_validation(self):
        """Test validación de configuración"""
        # Configuración inválida
        config = AIConfig(api_key="", model_name="invalid_model")
        errors = config.validate()
        
        self.assertTrue(len(errors) > 0)
        self.assertIn('api_key', errors)
        self.assertIn('model', errors)
        
        # Configuración válida
        config = AIConfig(
            api_key="AIzaSyTestKey123",
            model_name="gemini-2.0-flash-exp"
        )
        errors = config.validate()
        
        # Puede tener errores de directorio, pero no de api_key o model
        if errors:
            self.assertNotIn('api_key', errors)
            self.assertNotIn('model', errors)

class TestDataValidator(unittest.TestCase):
    """Tests para validador de datos"""
    
    def setUp(self):
        """Configurar datos de test"""
        self.valid_data = {
            'ID': ['001', '002', '003'],
            'Título': ['Test 1', 'Test 2', 'Test 3'],
            'Tipo': ['Incidencia', 'Requerimiento', 'Incidencia'],
            'Estado': ['Resueltas', 'Nuevo', 'En curso (asignada)'],
            'Fecha de Apertura': ['2024-01-01 10:00', '2024-01-02 11:00', '2024-01-03 12:00']
        }
        self.df_valid = pd.DataFrame(self.valid_data)
    
    def test_validate_valid_structure(self):
        """Test validación de estructura válida"""
        result = DataValidator.validate_csv_structure(self.df_valid)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(result['stats']['total_rows'], 3)
    
    def test_validate_missing_columns(self):
        """Test validación con columnas faltantes"""
        df_invalid = pd.DataFrame({
            'ID': ['001', '002'],
            'Título': ['Test 1', 'Test 2']
            # Faltan columnas requeridas
        })
        
        result = DataValidator.validate_csv_structure(df_invalid)
        
        self.assertFalse(result['valid'])
        self.assertTrue(len(result['errors']) > 0)
    
    def test_validate_empty_dataframe(self):
        """Test validación de DataFrame vacío"""
        df_empty = pd.DataFrame()
        
        result = DataValidator.validate_csv_structure(df_empty)
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('vacío' in error for error in result['errors']))
    
    def test_clean_text_data(self):
        """Test limpieza de texto"""
        dirty_text = "Texto con ♠♣♦♥ caracteres    especiales\n\n\t"
        clean_text = DataValidator.clean_text_data(dirty_text)
        
        self.assertNotIn('♠', clean_text)
        self.assertNotIn('\n', clean_text)
        self.assertEqual(clean_text.strip(), clean_text)

class TestCacheManager(unittest.TestCase):
    """Tests para gestor de cache"""
    
    def setUp(self):
        """Configurar cache temporal"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_manager = CacheManager(self.temp_dir)
    
    def tearDown(self):
        """Limpiar cache temporal"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_set_get(self):
        """Test guardar y obtener cache"""
        test_data = {"test": "data", "number": 123}
        
        # Guardar en cache
        success = self.cache_manager.set("test_key", test_data)
        self.assertTrue(success)
        
        # Obtener del cache
        cached_data = self.cache_manager.get("test_key")
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data["test"], "data")
        self.assertEqual(cached_data["number"], 123)
    
    def test_cache_miss(self):
        """Test cache miss"""
        result = self.cache_manager.get("nonexistent_key")
        self.assertIsNone(result)

class TestResponseFormatter(unittest.TestCase):
    """Tests para formateador de respuestas"""
    
    def test_format_markdown_response(self):
        """Test formateo de markdown"""
        markdown_text = "# Header\nSome text\n## Subheader\nMore text"
        formatted = ResponseFormatter.format_markdown_response(markdown_text)
        
        self.assertIn("# Header", formatted)
        self.assertIn("## Subheader", formatted)
    
    def test_extract_sections(self):
        """Test extracción de secciones"""
        text = """
# Analisis Principal
Contenido del análisis

## Resumen Ejecutivo
Resumen importante

### Detalles
Información detallada
"""
        sections = ResponseFormatter.extract_sections(text)
        
        self.assertIn('analisis_principal', sections)
        self.assertIn('resumen_ejecutivo', sections)
        self.assertIn('detalles', sections)
    
    def test_generate_summary(self):
        """Test generación de resumen"""
        long_text = "Primera oración. Segunda oración. Tercera oración. Cuarta oración."
        summary = ResponseFormatter.generate_summary(long_text, max_sentences=2)
        
        # Debería contener las primeras oraciones
        self.assertIn("Primera", summary)
        self.assertIn("Segunda", summary)

class TestMetricsCalculator(unittest.TestCase):
    """Tests para calculadora de métricas"""
    
    def test_calculate_efficiency_score(self):
        """Test cálculo de score de eficiencia"""
        metrics = {
            'resolution_rate': 95.0,
            'sla_compliance': 98.0,
            'avg_resolution_time_hours': 6.0
        }
        
        score = MetricsCalculator.calculate_efficiency_score(metrics)
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertIsInstance(score, float)
    
    def test_calculate_trend(self):
        """Test cálculo de tendencias"""
        # Tendencia creciente
        values_up = [10, 12, 15, 18, 20]
        trend, change = MetricsCalculator.calculate_trend(values_up)
        
        self.assertEqual(trend, "creciente")
        self.assertGreater(change, 0)
        
        # Tendencia decreciente
        values_down = [20, 18, 15, 12, 10]
        trend, change = MetricsCalculator.calculate_trend(values_down)
        
        self.assertEqual(trend, "decreciente")
        self.assertLess(change, 0)
        
        # Tendencia estable
        values_stable = [10, 10.2, 9.8, 10.1, 10]
        trend, change = MetricsCalculator.calculate_trend(values_stable)
        
        self.assertEqual(trend, "estable")

class TestPromptManager(unittest.TestCase):
    """Tests para gestor de prompts"""
    
    def test_get_comprehensive_analysis_prompt(self):
        """Test obtener prompt de análisis completo"""
        prompt = PromptManager.get_comprehensive_analysis_prompt()
        
        self.assertIsInstance(prompt, str)
        self.assertIn("Clínica Bonsana", prompt)
        self.assertIn("análisis exhaustivo", prompt)
        self.assertGreater(len(prompt), 500)  # Debe ser un prompt sustancial
    
    def test_get_quick_analysis_prompt(self):
        """Test obtener prompt de análisis rápido"""
        prompt = PromptManager.get_quick_analysis_prompt()
        
        self.assertIsInstance(prompt, str)
        self.assertIn("análisis rápido", prompt)
        self.assertIn("500 palabras", prompt)
    
    def test_get_available_prompts(self):
        """Test obtener prompts disponibles"""
        prompts = PromptManager.get_available_prompts()
        
        self.assertIsInstance(prompts, dict)
        self.assertIn("comprehensive", prompts)
        self.assertIn("quick", prompts)
        self.assertIn("sla", prompts)
    
    def test_get_custom_prompt(self):
        """Test obtener prompt personalizado"""
        focus_area = "Análisis de rendimiento"
        questions = ["¿Cuál es la eficiencia?", "¿Qué mejoras recomiendas?"]
        
        prompt = PromptManager.get_custom_prompt(focus_area, questions)
        
        self.assertIn(focus_area, prompt)
        self.assertIn(questions[0], prompt)
        self.assertIn(questions[1], prompt)

class TestGeminiClientMocked(unittest.TestCase):
    """Tests para cliente Gemini (mocked)"""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_gemini_client_init(self, mock_model, mock_configure):
        """Test inicialización del cliente"""
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance
        
        client = GeminiClient(api_key="test_key")
        
        mock_configure.assert_called_once_with(api_key="test_key")
        mock_model.assert_called_once()
        self.assertEqual(client.api_key, "test_key")
    
    def test_prepare_csv_data(self):
        """Test preparación de datos CSV"""
        # Crear archivo CSV temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("ID;Tipo;Estado\n001;Incidencia;Resueltas\n002;Requerimiento;Nuevo\n")
            temp_csv = f.name
        
        try:
            client = GeminiClient(api_key="test_key")
            formatted_data = client.prepare_csv_data(temp_csv)
            
            self.assertIsInstance(formatted_data, str)
            self.assertIn("INFORMACIÓN DEL DATASET", formatted_data)
            self.assertIn("ID", formatted_data)
            self.assertIn("Tipo", formatted_data)
            
        finally:
            os.unlink(temp_csv)

def run_integration_tests():
    """Ejecuta tests de integración básicos"""
    print("\n🧪 Ejecutando tests de integración...")
    
    # Test 1: Verificar estructura de directorios
    print("   📁 Verificando estructura de directorios...")
    required_dirs = ['ai', 'data', 'templates']
    missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
    
    if missing_dirs:
        print(f"   ❌ Directorios faltantes: {missing_dirs}")
        return False
    else:
        print("   ✅ Estructura de directorios correcta")
    
    # Test 2: Verificar archivos del módulo de IA
    print("   📄 Verificando archivos del módulo de IA...")
    required_files = [
        'ai/__init__.py',
        'ai/config.py',
        'ai/gemini_client.py',
        'ai/analyzer.py',
        'ai/prompts.py',
        'ai/utils.py'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"   ❌ Archivos faltantes: {missing_files}")
        return False
    else:
        print("   ✅ Archivos del módulo de IA presentes")
    
    # Test 3: Verificar importaciones
    print("   📦 Verificando importaciones...")
    try:
        from ai.config import AIConfig
        from ai.analyzer import AIAnalyzer
        from ai.prompts import PromptManager
        print("   ✅ Importaciones exitosas")
    except ImportError as e:
        print(f"   ❌ Error de importación: {e}")
        return False
    
    # Test 4: Verificar configuración
    print("   ⚙️ Verificando configuración...")
    try:
        config = AIConfig.from_env()
        if not config.api_key:
            print("   ⚠️  API key no configurada")
        else:
            print("   ✅ Configuración cargada")
    except Exception as e:
        print(f"   ❌ Error en configuración: {e}")
        return False
    
    print("   ✅ Tests de integración completados")
    return True

def main():
    """Función principal de tests"""
    print("="*60)
    print("    TESTS DEL MÓDULO DE IA")
    print("    Dashboard IT - Clínica Bonsana")
    print("="*60)
    
    # Tests unitarios
    print("\n🔬 Ejecutando tests unitarios...")
    
    # Crear suite de tests
    test_suite = unittest.TestSuite()
    
    # Agregar clases de test
    test_classes = [
        TestAIConfig,
        TestDataValidator,
        TestCacheManager,
        TestResponseFormatter,
        TestMetricsCalculator,
        TestPromptManager,
        TestGeminiClientMocked
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Tests de integración
    integration_success = run_integration_tests()
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE TESTS")
    print("="*60)
    
    unit_tests_passed = result.wasSuccessful()
    
    print(f"Tests unitarios: {'✅ PASARON' if unit_tests_passed else '❌ FALLARON'}")
    print(f"Tests de integración: {'✅ PASARON' if integration_success else '❌ FALLARON'}")
    
    if result.failures:
        print(f"\nFallas: {len(result.failures)}")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nErrores: {len(result.errors)}")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    overall_success = unit_tests_passed and integration_success
    
    print(f"\n{'🎉 TODOS LOS TESTS PASARON' if overall_success else '⚠️ ALGUNOS TESTS FALLARON'}")
    
    return 0 if overall_success else 1

if __name__ == '__main__':
    sys.exit(main())