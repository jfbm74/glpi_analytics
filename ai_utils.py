#!/usr/bin/env python3
"""
Utilidades específicas para manejo de IA en el Dashboard IT
Clínica Bonsana
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
import tempfile
import subprocess
from dotenv import load_dotenv

class AIUtils:
    """Utilidades para manejo de la funcionalidad IA"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_AI_API_KEY')
        self.model_name = os.getenv('GOOGLE_AI_MODEL', 'gemini-1.5-pro')
        
    def check_ai_status(self):
        """Verifica el estado completo del sistema de IA"""
        print("🤖 ESTADO DEL SISTEMA DE IA")
        print("=" * 50)
        
        status = {
            'api_key_configured': bool(self.api_key),
            'api_key_valid': False,
            'service_available': False,
            'model_accessible': False,
            'dependencies_installed': False,
            'config_valid': False
        }
        
        # Verificar dependencias
        try:
            import google.generativeai as genai
            status['dependencies_installed'] = True
            print("✅ Dependencias instaladas")
        except ImportError:
            print("❌ google-generativeai no instalado")
            return status
        
        # Verificar API key
        if not self.api_key:
            print("❌ GOOGLE_AI_API_KEY no configurada")
            return status
        
        if self.api_key in ['tu-api-key-aqui', 'your-api-key-here']:
            print("❌ GOOGLE_AI_API_KEY es un placeholder")
            return status
        
        print("✅ API Key configurada")
        
        # Probar conexión
        try:
            genai.configure(api_key=self.api_key)
            models = list(genai.list_models())
            
            if models:
                status['api_key_valid'] = True
                status['service_available'] = True
                print(f"✅ Conexión exitosa ({len(models)} modelos disponibles)")
                
                # Verificar modelo específico
                model_names = [m.name.split('/')[-1] for m in models]
                if self.model_name in model_names:
                    status['model_accessible'] = True
                    print(f"✅ Modelo {self.model_name} accesible")
                else:
                    print(f"⚠️  Modelo {self.model_name} no encontrado")
                    print(f"   Modelos disponibles: {', '.join(model_names[:5])}")
            else:
                print("❌ No se pudieron obtener modelos")
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return status
        
        # Verificar configuración de la aplicación
        try:
            sys.path.insert(0, str(self.project_root))
            from config import get_config
            config = get_config()
            
            if config.AI_ANALYSIS_ENABLED:
                status['config_valid'] = True
                print("✅ Configuración de aplicación válida")
            else:
                print("⚠️  IA deshabilitada en configuración de aplicación")
                
        except Exception as e:
            print(f"❌ Error en configuración: {e}")
        
        return status
    
    def test_analysis(self, sample_size='small'):
        """Prueba el análisis de IA con datos de ejemplo"""
        print(f"\n🧪 PRUEBA DE ANÁLISIS IA ({sample_size.upper()})")
        print("=" * 50)
        
        if not self.api_key:
            print("❌ API Key no configurada")
            return False
        
        # Crear CSV de prueba
        test_csv = self.create_test_csv(sample_size)
        
        try:
            sys.path.insert(0, str(self.project_root))
            from app import AIAnalysisService
            
            service = AIAnalysisService()
            
            if not service.is_available():
                print("❌ Servicio de IA no disponible")
                return False
            
            print("🔄 Iniciando análisis...")
            start_time = time.time()
            
            result = service.analyze_tickets(test_csv)
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result['success']:
                print(f"✅ Análisis completado en {duration:.1f} segundos")
                print(f"📊 Filas analizadas: {result.get('csv_rows_analyzed', 'N/A')}")
                print(f"🧠 Modelo usado: {result.get('model_used', 'N/A')}")
                
                # Mostrar muestra del análisis
                analysis = result['analysis']
                preview_length = 300
                if len(analysis) > preview_length:
                    preview = analysis[:preview_length] + "..."
                else:
                    preview = analysis
                
                print(f"📝 Vista previa del análisis:")
                print("-" * 40)
                print(preview)
                print("-" * 40)
                
                # Guardar análisis completo
                output_file = self.project_root / f'test_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Análisis de prueba - {datetime.now()}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(analysis)
                
                print(f"💾 Análisis completo guardado en: {output_file}")
                return True
                
            else:
                print(f"❌ Error en análisis: {result.get('error', 'Error desconocido')}")
                return False
                
        except Exception as e:
            print(f"❌ Error ejecutando prueba: {e}")
            return False
            
        finally:
            # Limpiar archivo de prueba
            if os.path.exists(test_csv):
                os.remove(test_csv)
    
    def create_test_csv(self, size='small'):
        """Crea CSV de prueba para testing"""
        if size == 'small':
            data_rows = 5
        elif size == 'medium':
            data_rows = 25
        elif size == 'large':
            data_rows = 100
        else:
            data_rows = 5
        
        header = "ID;Título;Tipo;Categoría;Prioridad;Estado;Fecha de Apertura;Fecha de solución;Se superó el tiempo de resolución;Asignado a: - Técnico;Solicitante - Solicitante;Elementos asociados;ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución;Encuesta de satisfacción - Satisfacción"
        
        sample_data = [
            "1;Falla impresora consultorio 1;Incidencia;Hardware > Impresora;Alta;Resueltas;2025-05-01 09:00;2025-05-01 11:30;No;Juan Pérez;Dr. García;IMP-001;INC_ALTO;5",
            "2;Instalación software médico;Requerimiento;Software > Aplicación;Mediana;Cerrado;2025-05-02 14:00;2025-05-03 10:00;Si;Ana López;Enfermera Silva;;REQ_MEDIO;4",
            "3;Red lenta en urgencias;Incidencia;Red > Conectividad;Alta;En curso (asignada);2025-05-03 16:00;;No;Carlos Ruiz;Dr. Martínez;SW-005;INC_ALTO;",
            "4;Actualización sistema HIS;Requerimiento;Software > Sistema;Alta;Resueltas;2025-05-04 08:00;2025-05-04 18:00;No;Juan Pérez;Administración;SRV-MED;REQ_ALTO;5",
            "5;Mantenimiento PCs recepción;Incidencia;Hardware > Computador;Baja;Cerrado;2025-05-05 13:00;2025-05-05 15:00;No;Ana López;Recepción;PC-003;INC_BAJO;3",
            "6;Error en sistema facturación;Incidencia;Software > Sistema;Alta;Resueltas;2025-05-06 10:00;2025-05-06 14:00;No;Carlos Ruiz;Contabilidad;SRV-FACT;INC_ALTO;4",
            "7;Nuevo usuario sistema;Requerimiento;Acceso > Usuario;Baja;Cerrado;2025-05-07 09:00;2025-05-07 09:30;No;Ana López;RRHH;USR-001;REQ_BAJO;5",
            "8;Pantalla no enciende quirófano;Incidencia;Hardware > Monitor;Alta;En curso (asignada);2025-05-08 07:00;;No;Juan Pérez;Dr. Cirujano;MON-QX1;INC_ALTO;",
            "9;Backup automático fallando;Incidencia;Sistema > Backup;Mediana;Resueltas;2025-05-09 02:00;2025-05-09 08:00;Si;Carlos Ruiz;IT Manager;SRV-BCK;INC_MEDIO;3",
            "10;Capacitación nuevo software;Requerimiento;Capacitación > Software;Baja;Cerrado;2025-05-10 15:00;2025-05-12 16:00;No;Ana López;Enfermería;TRAIN-01;REQ_BAJO;4"
        ]
        
        # Repetir datos según el tamaño solicitado
        rows_needed = min(data_rows, len(sample_data))
        selected_rows = sample_data[:rows_needed]
        
        # Si necesitamos más filas, generar datos adicionales
        if data_rows > len(sample_data):
            for i in range(len(sample_data), data_rows):
                # Modificar datos existentes
                base_row = sample_data[i % len(sample_data)]
                parts = base_row.split(';')
                parts[0] = str(i + 1)  # Nuevo ID
                parts[1] = f"Ticket generado {i + 1}"  # Nuevo título
                selected_rows.append(';'.join(parts))
        
        # Crear archivo temporal
        fd, temp_path = tempfile.mkstemp(suffix='.csv', text=True)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(header + '\n')
            for row in selected_rows:
                f.write(row + '\n')
        
        print(f"📝 CSV de prueba creado: {data_rows} filas")
        return temp_path
    
    def benchmark_models(self):
        """Compara el rendimiento de diferentes modelos disponibles"""
        print("\n⚡ BENCHMARK DE MODELOS")
        print("=" * 50)
        
        if not self.api_key:
            print("❌ API Key no configurada")
            return
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            # Obtener modelos Gemini disponibles
            models = list(genai.list_models())
            gemini_models = [m for m in models if 'gemini' in m.name.lower()]
            
            if not gemini_models:
                print("❌ No se encontraron modelos Gemini")
                return
            
            # Crear CSV de prueba pequeño
            test_csv = self.create_test_csv('small')
            
            # Preparar datos
            with open(test_csv, 'r', encoding='utf-8') as f:
                csv_data = f.read()
            
            simple_prompt = f"Analiza brevemente estos datos de tickets de soporte IT: {csv_data[:500]}..."
            
            results = []
            
            for model in gemini_models[:3]:  # Probar máximo 3 modelos
                model_name = model.name.split('/')[-1]
                print(f"\n🧠 Probando modelo: {model_name}")
                
                try:
                    ai_model = genai.GenerativeModel(model_name)
                    
                    start_time = time.time()
                    response = ai_model.generate_content(simple_prompt)
                    end_time = time.time()
                    
                    duration = end_time - start_time
                    response_length = len(response.text) if response.text else 0
                    
                    results.append({
                        'model': model_name,
                        'duration': duration,
                        'response_length': response_length,
                        'success': True
                    })
                    
                    print(f"   ✅ Tiempo: {duration:.2f}s")
                    print(f"   📏 Longitud respuesta: {response_length} caracteres")
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    results.append({
                        'model': model_name,
                        'duration': 0,
                        'response_length': 0,
                        'success': False,
                        'error': str(e)
                    })
            
            # Mostrar resumen
            print(f"\n📊 RESUMEN DEL BENCHMARK")
            print("-" * 40)
            
            successful_results = [r for r in results if r['success']]
            if successful_results:
                fastest = min(successful_results, key=lambda x: x['duration'])
                most_detailed = max(successful_results, key=lambda x: x['response_length'])
                
                print(f"🏃 Más rápido: {fastest['model']} ({fastest['duration']:.2f}s)")
                print(f"📝 Más detallado: {most_detailed['model']} ({most_detailed['response_length']} chars)")
                
                # Recomendación
                if fastest['model'] == most_detailed['model']:
                    print(f"🎯 Recomendado: {fastest['model']} (mejor en ambos aspectos)")
                else:
                    print(f"🎯 Para velocidad: {fastest['model']}")
                    print(f"🎯 Para detalle: {most_detailed['model']}")
            
            # Limpiar
            os.remove(test_csv)
            
        except Exception as e:
            print(f"❌ Error en benchmark: {e}")
    
    def estimate_costs(self, csv_path):
        """Estima costos aproximados del análisis IA"""
        print("\n💰 ESTIMACIÓN DE COSTOS")
        print("=" * 30)
        
        if not os.path.exists(csv_path):
            print(f"❌ Archivo no encontrado: {csv_path}")
            return
        
        try:
            # Leer archivo y calcular tokens aproximados
            with open(csv_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Estimación rough: ~4 caracteres por token
            estimated_input_tokens = len(content) // 4
            
            # Agregar tokens del prompt base
            sys.path.insert(0, str(self.project_root))
            from config import get_config
            config = get_config()
            prompt_template = config.AI_CONFIG['prompt_template']
            prompt_tokens = len(prompt_template) // 4
            
            total_input_tokens = estimated_input_tokens + prompt_tokens
            
            # Estimar tokens de salida (típicamente 1000-3000 para análisis completo)
            estimated_output_tokens = 2000
            
            # Precios aproximados de Gemini (pueden cambiar)
            # Estos son valores de ejemplo - verificar precios actuales
            price_per_1k_input_tokens = 0.00025  # $0.00025 por 1K tokens input
            price_per_1k_output_tokens = 0.0005   # $0.0005 por 1K tokens output
            
            input_cost = (total_input_tokens / 1000) * price_per_1k_input_tokens
            output_cost = (estimated_output_tokens / 1000) * price_per_1k_output_tokens
            total_cost = input_cost + output_cost
            
            print(f"📄 Tamaño del archivo: {len(content):,} caracteres")
            print(f"🔤 Tokens estimados (input): {total_input_tokens:,}")
            print(f"🔤 Tokens estimados (output): {estimated_output_tokens:,}")
            print(f"💵 Costo estimado (input): ${input_cost:.4f}")
            print(f"💵 Costo estimado (output): ${output_cost:.4f}")
            print(f"💰 Costo total estimado: ${total_cost:.4f}")
            
            # Estimaciones mensuales
            print(f"\n📅 ESTIMACIONES MENSUALES:")
            for frequency, multiplier in [('Diario', 30), ('Semanal', 4), ('Mensual', 1)]:
                monthly_cost = total_cost * multiplier
                print(f"   {frequency}: ${monthly_cost:.2f}/mes")
            
            print(f"\n⚠️  Nota: Precios aproximados basados en tarifas de ejemplo")
            print(f"   Verificar precios actuales en: https://ai.google.dev/pricing")
            
        except Exception as e:
            print(f"❌ Error calculando costos: {e}")
    
    def export_analysis_history(self, output_dir=None):
        """Exporta el historial de análisis realizados"""
        if not output_dir:
            output_dir = self.project_root / 'exports'
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        print(f"\n📦 EXPORTANDO HISTORIAL")
        print("=" * 30)
        
        # Buscar archivos de análisis
        analysis_files = list(self.project_root.glob('test_analysis_*.txt'))
        
        if not analysis_files:
            print("ℹ️  No se encontraron archivos de análisis")
            return
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_analyses': len(analysis_files),
            'analyses': []
        }
        
        for file_path in sorted(analysis_files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extraer metadatos del archivo
                file_stats = file_path.stat()
                
                analysis_info = {
                    'filename': file_path.name,
                    'creation_date': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    'size_bytes': file_stats.st_size,
                    'content_preview': content[:500] + "..." if len(content) > 500 else content
                }
                
                export_data['analyses'].append(analysis_info)
                
            except Exception as e:
                print(f"⚠️  Error procesando {file_path.name}: {e}")
        
        # Guardar export
        export_file = output_dir / f'analysis_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Historial exportado: {export_file}")
        print(f"📊 Total de análisis: {len(analysis_files)}")
    
    def cleanup_temp_files(self):
        """Limpia archivos temporales de análisis"""
        print("\n🧹 LIMPIEZA DE ARCHIVOS TEMPORALES")
        print("=" * 40)
        
        # Archivos de análisis de prueba
        analysis_files = list(self.project_root.glob('test_analysis_*.txt'))
        
        # Archivos CSV temporales
        temp_csv_files = list(self.project_root.glob('temp_*.csv'))
        
        all_temp_files = analysis_files + temp_csv_files
        
        if not all_temp_files:
            print("✅ No hay archivos temporales para limpiar")
            return
        
        for file_path in all_temp_files:
            try:
                file_path.unlink()
                print(f"🗑️  Eliminado: {file_path.name}")
            except Exception as e:
                print(f"⚠️  Error eliminando {file_path.name}: {e}")
        
        print(f"✅ Limpieza completada: {len(all_temp_files)} archivos procesados")

def main():
    """Función principal para CLI"""
    parser = argparse.ArgumentParser(description='Utilidades para IA - Dashboard IT Clínica Bonsana')
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando para verificar estado
    status_parser = subparsers.add_parser('status', help='Verificar estado del sistema IA')
    
    # Comando para probar análisis
    test_parser = subparsers.add_parser('test', help='Probar análisis con datos de ejemplo')
    test_parser.add_argument('--size', choices=['small', 'medium', 'large'], 
                           default='small', help='Tamaño del dataset de prueba')
    
    # Comando para benchmark
    benchmark_parser = subparsers.add_parser('benchmark', help='Comparar modelos disponibles')
    
    # Comando para estimar costos
    cost_parser = subparsers.add_parser('cost', help='Estimar costos de análisis')
    cost_parser.add_argument('csv_path', help='Ruta al archivo CSV')
    
    # Comando para exportar historial
    export_parser = subparsers.add_parser('export', help='Exportar historial de análisis')
    export_parser.add_argument('--output', help='Directorio de salida')
    
    # Comando para limpiar
    cleanup_parser = subparsers.add_parser('cleanup', help='Limpiar archivos temporales')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    utils = AIUtils()
    
    if args.command == 'status':
        status = utils.check_ai_status()
        
        # Código de salida basado en el estado
        if all([status['dependencies_installed'], status['api_key_valid'], 
                status['service_available'], status['config_valid']]):
            print("\n✅ Sistema IA completamente funcional")
            sys.exit(0)
        else:
            print("\n⚠️  Sistema IA tiene problemas")
            sys.exit(1)
            
    elif args.command == 'test':
        success = utils.test_analysis(args.size)
        sys.exit(0 if success else 1)
        
    elif args.command == 'benchmark':
        utils.benchmark_models()
        
    elif args.command == 'cost':
        utils.estimate_costs(args.csv_path)
        
    elif args.command == 'export':
        utils.export_analysis_history(args.output)
        
    elif args.command == 'cleanup':
        utils.cleanup_temp_files()

if __name__ == '__main__':
    main()