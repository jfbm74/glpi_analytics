#!/usr/bin/env python3
"""
Script de configuración automática para la integración de Google AI Studio
Dashboard IT - Clínica Bonsana
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path
import time

class AISetupWizard:
    """Asistente de configuración para Google AI Studio"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / '.env'
        self.env_example = self.project_root / '.env.example'
        
    def print_header(self):
        """Imprime el header del asistente"""
        print("=" * 70)
        print("🤖 ASISTENTE DE CONFIGURACIÓN - GOOGLE AI STUDIO")
        print("📍 Dashboard IT - Clínica Bonsana")
        print("=" * 70)
        print()
    
    def check_dependencies(self):
        """Verifica e instala dependencias necesarias"""
        print("🔍 Verificando dependencias...")
        
        required_packages = [
            'google-generativeai',
            'python-dotenv',
            'requests'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"   ✅ {package} - Instalado")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package} - Faltante")
        
        if missing_packages:
            print(f"\n📦 Instalando paquetes faltantes: {', '.join(missing_packages)}")
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install'
                ] + missing_packages)
                print("✅ Dependencias instaladas correctamente")
            except subprocess.CalledProcessError:
                print("❌ Error instalando dependencias")
                return False
        
        return True
    
    def get_api_key_interactive(self):
        """Obtiene la API key de forma interactiva"""
        print("\n🔑 CONFIGURACIÓN DE GOOGLE AI STUDIO")
        print("=" * 50)
        print()
        print("Para obtener tu API Key:")
        print("1. Visita: https://makersuite.google.com/app/apikey")
        print("2. Inicia sesión con tu cuenta de Google")
        print("3. Haz clic en 'Create API Key'")
        print("4. Copia la API Key generada")
        print()
        
        while True:
            api_key = input("🔑 Ingresa tu Google AI Studio API Key: ").strip()
            
            if not api_key:
                print("❌ La API Key no puede estar vacía")
                continue
            
            if len(api_key) < 30:
                print("❌ La API Key parece ser muy corta. Verifica que sea correcta.")
                continue
            
            # Verificar API key
            if self.test_api_key(api_key):
                return api_key
            else:
                print("❌ API Key inválida. Intenta nuevamente.")
                retry = input("¿Deseas intentar con otra API Key? (s/n): ").lower()
                if retry != 's':
                    return None
    
    def test_api_key(self, api_key):
        """Prueba si la API key es válida"""
        print("🧪 Probando API Key...")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Intentar listar modelos disponibles
            models = list(genai.list_models())
            
            if models:
                print("✅ API Key válida")
                print(f"   Modelos disponibles: {len(models)}")
                return True
            else:
                print("❌ No se pudieron obtener modelos")
                return False
                
        except Exception as e:
            print(f"❌ Error probando API Key: {e}")
            return False
    
    def select_model(self, api_key):
        """Permite seleccionar el modelo de IA a usar"""
        print("\n🧠 SELECCIÓN DE MODELO")
        print("=" * 30)
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Obtener modelos disponibles
            models = list(genai.list_models())
            gemini_models = [m for m in models if 'gemini' in m.name.lower()]
            
            if not gemini_models:
                print("⚠️  No se encontraron modelos Gemini. Usando modelo por defecto.")
                return 'gemini-1.5-pro'
            
            print("Modelos Gemini disponibles:")
            for i, model in enumerate(gemini_models[:5], 1):  # Mostrar máximo 5
                model_name = model.name.split('/')[-1]
                print(f"   {i}. {model_name}")
            
            print(f"   {len(gemini_models) + 1}. gemini-1.5-pro (recomendado)")
            
            while True:
                try:
                    choice = input(f"\nSelecciona un modelo (1-{len(gemini_models) + 1}): ").strip()
                    choice_num = int(choice)
                    
                    if choice_num == len(gemini_models) + 1:
                        return 'gemini-1.5-pro'
                    elif 1 <= choice_num <= len(gemini_models):
                        selected_model = gemini_models[choice_num - 1]
                        model_name = selected_model.name.split('/')[-1]
                        return model_name
                    else:
                        print("❌ Selección inválida")
                        
                except ValueError:
                    print("❌ Por favor ingresa un número válido")
                    
        except Exception as e:
            print(f"⚠️  Error obteniendo modelos: {e}")
            print("Usando modelo por defecto: gemini-1.5-pro")
            return 'gemini-1.5-pro'
    
    def create_env_file(self, api_key, model_name):
        """Crea o actualiza el archivo .env"""
        print("\n📝 Creando archivo de configuración...")
        
        # Leer .env.example si existe
        env_content = {}
        if self.env_example.exists():
            with open(self.env_example, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key] = value
        
        # Actualizar valores de IA
        env_content['GOOGLE_AI_API_KEY'] = api_key
        env_content['GOOGLE_AI_MODEL'] = model_name
        env_content['AI_ANALYSIS_ENABLED'] = 'True'
        
        # Valores por defecto si no existen
        defaults = {
            'FLASK_ENV': 'development',
            'SECRET_KEY': 'dev-key-clinica-bonsana-2025',
            'DATA_DIRECTORY': 'data',
            'LOG_LEVEL': 'INFO',
            'MAX_CSV_SIZE_MB': '10',
            'AI_ANALYSIS_TIMEOUT': '300'
        }
        
        for key, value in defaults.items():
            if key not in env_content:
                env_content[key] = value
        
        # Escribir archivo .env
        with open(self.env_file, 'w', encoding='utf-8') as f:
            f.write("# Configuración del Dashboard IT - Clínica Bonsana\n")
            f.write("# Generado automáticamente por setup_ai.py\n\n")
            
            # Sección de IA
            f.write("# Configuración de Google AI Studio\n")
            f.write(f"GOOGLE_AI_API_KEY={env_content['GOOGLE_AI_API_KEY']}\n")
            f.write(f"GOOGLE_AI_MODEL={env_content['GOOGLE_AI_MODEL']}\n")
            f.write(f"AI_ANALYSIS_ENABLED={env_content['AI_ANALYSIS_ENABLED']}\n\n")
            
            # Otras configuraciones
            f.write("# Configuración de Flask\n")
            for key in ['FLASK_ENV', 'SECRET_KEY']:
                if key in env_content:
                    f.write(f"{key}={env_content[key]}\n")
            
            f.write("\n# Configuración de datos\n")
            for key in ['DATA_DIRECTORY', 'LOG_LEVEL']:
                if key in env_content:
                    f.write(f"{key}={env_content[key]}\n")
            
            f.write("\n# Configuración de IA\n")
            for key in ['MAX_CSV_SIZE_MB', 'AI_ANALYSIS_TIMEOUT']:
                if key in env_content:
                    f.write(f"{key}={env_content[key]}\n")
        
        print(f"✅ Archivo .env creado en: {self.env_file}")
    
    def test_integration(self):
        """Prueba la integración completa"""
        print("\n🧪 PROBANDO INTEGRACIÓN")
        print("=" * 30)
        
        try:
            # Cargar variables de entorno
            from dotenv import load_dotenv
            load_dotenv(self.env_file)
            
            # Importar y probar la clase AIAnalysisService
            sys.path.insert(0, str(self.project_root))
            from app import AIAnalysisService
            
            ai_service = AIAnalysisService()
            
            if ai_service.is_available():
                print("✅ Servicio de IA inicializado correctamente")
                
                # Crear CSV de prueba pequeño
                test_csv = self.create_test_csv()
                
                print("🔬 Realizando análisis de prueba...")
                result = ai_service.analyze_tickets(test_csv)
                
                if result['success']:
                    print("✅ Análisis de prueba completado exitosamente")
                    print(f"   Filas analizadas: {result.get('csv_rows_analyzed', 'N/A')}")
                    print(f"   Modelo usado: {result.get('model_used', 'N/A')}")
                    
                    # Mostrar muestra del análisis
                    analysis_preview = result['analysis'][:200] + "..." if len(result['analysis']) > 200 else result['analysis']
                    print(f"   Vista previa: {analysis_preview}")
                    
                    # Limpiar archivo de prueba
                    os.remove(test_csv)
                    
                    return True
                else:
                    print(f"❌ Error en análisis de prueba: {result.get('error', 'Error desconocido')}")
                    return False
            else:
                print("❌ Servicio de IA no está disponible")
                return False
                
        except Exception as e:
            print(f"❌ Error en prueba de integración: {e}")
            return False
    
    def create_test_csv(self):
        """Crea un CSV de prueba pequeño"""
        test_data = """ID;Título;Tipo;Categoría;Prioridad;Estado;Fecha de Apertura;Fecha de solución;Se superó el tiempo de resolución;Asignado a: - Técnico;Solicitante - Solicitante;Elementos asociados;ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución;Encuesta de satisfacción - Satisfacción
1;Test Impresora;Incidencia;Hardware > Impresora;Alta;Resueltas;2025-05-01 10:00;2025-05-01 12:00;No;Juan Pérez;María García;IMP-001;INC_ALTO;5
2;Test Software;Requerimiento;Software > App;Mediana;Cerrado;2025-05-02 09:00;2025-05-02 15:00;Si;Ana López;Carlos Ruiz;;INC_MEDIO;4
3;Test Red;Incidencia;Red > Cable;Baja;En curso (asignada);2025-05-03 14:00;;No;;Luis Martín;;INC_BAJO;"""
        
        test_file = self.project_root / 'test_ai_data.csv'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_data)
        
        return str(test_file)
    
    def show_next_steps(self):
        """Muestra los próximos pasos"""
        print("\n" + "=" * 70)
        print("🎉 ¡CONFIGURACIÓN COMPLETADA!")
        print("=" * 70)
        print("\n📋 PRÓXIMOS PASOS:")
        print()
        print("1. 🚀 Inicia el dashboard:")
        print("   python app.py")
        print()
        print("2. 🌐 Abre tu navegador en:")
        print("   http://localhost:5000")
        print()
        print("3. 🤖 Para usar el análisis IA:")
        print("   • Asegúrate de tener tu archivo glpi.csv en el directorio data/")
        print("   • Haz clic en 'Generar Análisis Inteligente con IA'")
        print("   • Ve a la pestaña 'Análisis IA' para ver los resultados")
        print()
        print("🔧 ARCHIVOS CREADOS:")
        print(f"   • {self.env_file}: Configuración de variables de entorno")
        print()
        print("📊 CARACTERÍSTICAS DISPONIBLES:")
        print("   • Dashboard tradicional con métricas y gráficos")
        print("   • Análisis inteligente con Google AI Studio")
        print("   • Recomendaciones estratégicas para clínicas")
        print("   • Benchmarking específico del sector salud")
        print()
        print("📞 SOPORTE:")
        print("   • Consulta README.md para documentación completa")
        print("   • Verifica el estado de IA en: http://localhost:5000/api/ai/status")
        print("   • Health check en: http://localhost:5000/health")
        print()
        print("⚠️  IMPORTANTE:")
        print("   • Mantén tu API Key privada y no la compartas")
        print("   • El archivo .env está en .gitignore por seguridad")
        print("   • Los análisis con IA tienen un costo por token en Google AI Studio")
        print()
    
    def run_setup(self):
        """Ejecuta el asistente completo"""
        self.print_header()
        
        # Verificar dependencias
        if not self.check_dependencies():
            print("❌ No se pudieron instalar las dependencias requeridas")
            sys.exit(1)
        
        # Obtener API key
        api_key = self.get_api_key_interactive()
        if not api_key:
            print("❌ Configuración cancelada por el usuario")
            sys.exit(1)
        
        # Seleccionar modelo
        model_name = self.select_model(api_key)
        
        # Crear archivo .env
        self.create_env_file(api_key, model_name)
        
        # Probar integración
        if self.test_integration():
            print("✅ Integración verificada correctamente")
        else:
            print("⚠️  Hubo problemas en la verificación, pero la configuración está completa")
        
        # Mostrar próximos pasos
        self.show_next_steps()

def main():
    """Función principal"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Asistente de Configuración - Google AI Studio")
        print("\nUso: python setup_ai.py")
        print("\nEste script te ayuda a configurar la integración con Google AI Studio:")
        print("- Instala dependencias necesarias")
        print("- Configura tu API Key de Google AI Studio")
        print("- Selecciona el modelo de IA a usar")
        print("- Crea el archivo .env con la configuración")
        print("- Prueba la integración completa")
        return
    
    wizard = AISetupWizard()
    wizard.run_setup()

if __name__ == '__main__':
    main()