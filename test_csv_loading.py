#!/usr/bin/env python3
"""
Script para probar la carga del archivo CSV real y diagnosticar problemas
"""

import pandas as pd
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_csv_loading():
    """Prueba cargar el archivo CSV con diferentes configuraciones"""
    
    csv_file = "glpi (1).csv"
    
    if not Path(csv_file).exists():
        print(f"❌ Archivo {csv_file} no encontrado")
        return
        
    print(f"🧪 Probando carga del archivo: {csv_file}")
    print("=" * 60)
    
    # Configuraciones a probar
    configs = [
        {'encoding': 'utf-8-sig', 'delimiter': ';', 'quotechar': '"'},
        {'encoding': 'utf-8', 'delimiter': ';', 'quotechar': '"'},
        {'encoding': 'latin-1', 'delimiter': ';', 'quotechar': '"'},
        {'encoding': 'cp1252', 'delimiter': ';', 'quotechar': '"'},
    ]
    
    successful_config = None
    df = None
    
    for i, config in enumerate(configs, 1):
        print(f"\n🔍 Configuración {i}: {config}")
        
        try:
            df = pd.read_csv(
                csv_file,
                delimiter=config['delimiter'],
                encoding=config['encoding'],
                quotechar=config['quotechar'],
                skipinitialspace=True,
                na_values=['', 'NULL', 'null', 'N/A', 'n/a']
            )
            
            print(f"✅ ¡Éxito! Archivo cargado correctamente")
            print(f"   📊 Filas: {len(df)}")
            print(f"   📋 Columnas: {len(df.columns)}")
            print(f"   🏷️  Primeras columnas: {list(df.columns[:5])}")
            
            successful_config = config
            break
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    if df is not None:
        print("\n" + "=" * 60)
        print("📋 ANÁLISIS DEL ARCHIVO CARGADO")
        print("=" * 60)
        
        # Mostrar información detallada
        print(f"Dimensiones: {df.shape}")
        print(f"Columnas encontradas ({len(df.columns)}):")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. '{col}'")
        
        print(f"\nPrimeros 3 registros:")
        print(df.head(3).to_string(max_cols=5))
        
        # Verificar columnas clave que busca el sistema
        key_columns = [
            'ID', 'Tipo', 'Estado', 'Prioridad', 'Categoría',
            'Asignado a: - Técnico', 'Solicitante - Solicitante',
            'Se superó el tiempo de resolución', 'Encuesta de satisfacción - Satisfacción'
        ]
        
        print(f"\n🔍 VERIFICACIÓN DE COLUMNAS CLAVE:")
        missing_columns = []
        found_columns = []
        
        for col in key_columns:
            if col in df.columns:
                found_columns.append(col)
                print(f"   ✅ '{col}' - ENCONTRADA")
            else:
                missing_columns.append(col)
                print(f"   ❌ '{col}' - FALTANTE")
        
        if missing_columns:
            print(f"\n⚠️  ADVERTENCIA: {len(missing_columns)} columnas clave faltantes")
            print("   El dashboard podría no funcionar correctamente")
        else:
            print(f"\n🎉 PERFECTO: Todas las columnas clave están presentes")
        
        # Probar algunas operaciones básicas
        print(f"\n🧮 PRUEBAS BÁSICAS:")
        
        # Contar tipos
        if 'Tipo' in df.columns:
            tipos = df['Tipo'].value_counts()
            print(f"   📊 Distribución por Tipo:")
            for tipo, count in tipos.items():
                print(f"      {tipo}: {count}")
        
        # Contar estados
        if 'Estado' in df.columns:
            estados = df['Estado'].value_counts()
            print(f"   📊 Distribución por Estado:")
            for estado, count in estados.items():
                print(f"      {estado}: {count}")
        
        # Verificar técnicos
        if 'Asignado a: - Técnico' in df.columns:
            tecnicos = df['Asignado a: - Técnico'].value_counts()
            print(f"   👥 Técnicos encontrados: {len(tecnicos)}")
            print(f"   🎯 Tickets sin asignar: {df['Asignado a: - Técnico'].isna().sum()}")
        
        return True, successful_config, df
    else:
        print("\n❌ NO SE PUDO CARGAR EL ARCHIVO CON NINGUNA CONFIGURACIÓN")
        return False, None, None

def test_with_ticketanalyzer():
    """Prueba usando la clase TicketAnalyzer mejorada"""
    print("\n" + "=" * 60)
    print("🧪 PROBANDO CON TICKETANALYZER")
    print("=" * 60)
    
    # Copiar el archivo a la ubicación esperada
    import shutil
    source = "glpi (1).csv"
    dest = "data/glpi.csv"
    
    if Path(source).exists():
        # Crear directorio si no existe
        Path("data").mkdir(exist_ok=True)
        shutil.copy(source, dest)
        print(f"📁 Archivo copiado a {dest}")
        
        # Importar y probar
        try:
            from app import TicketAnalyzer
            
            analyzer = TicketAnalyzer("data")
            df = analyzer._load_data()
            
            print(f"✅ TicketAnalyzer cargó el archivo exitosamente")
            print(f"   📊 Dimensiones: {df.shape}")
            
            # Probar algunas funciones
            metrics = analyzer.get_overall_metrics()
            print(f"   📈 Métricas generales: {metrics}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error con TicketAnalyzer: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print(f"❌ Archivo fuente {source} no encontrado")
        return False

if __name__ == '__main__':
    print("🏥 DIAGNÓSTICO DE CARGA DE ARCHIVO CSV - GLPI ANALYTICS")
    print("=" * 60)
    
    # Prueba 1: Carga directa con pandas
    success, config, df = test_csv_loading()
    
    if success:
        # Prueba 2: Con TicketAnalyzer
        test_with_ticketanalyzer()
    
    print("\n" + "=" * 60)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("=" * 60)