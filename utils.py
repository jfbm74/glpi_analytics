#!/usr/bin/env python3
"""
Utilidades y scripts de apoyo para el Dashboard IT de Clínica Bonsana
"""

import pandas as pd
import os
import json
from datetime import datetime, timedelta
import argparse

def validate_csv_structure(csv_path):
    """
    Valida la estructura del archivo CSV para asegurar compatibilidad
    
    Args:
        csv_path (str): Ruta al archivo CSV
        
    Returns:
        dict: Resultado de la validación
    """
    required_columns = [
        'ID',
        'Título',
        'Tipo',
        'Categoría',
        'Prioridad',
        'Estado',
        'Fecha de Apertura',
        'Fecha de solución',
        'Se superó el tiempo de resolución',
        'Asignado a: - Técnico',
        'Solicitante - Solicitante',
        'Elementos asociados',
        'ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución',
        'Encuesta de satisfacción - Satisfacción'
    ]
    
    try:
        # Leer el CSV
        df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8', nrows=5)
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': {
                'total_columns': len(df.columns),
                'sample_rows': len(df),
                'detected_delimiter': ';'
            }
        }
        
        # Verificar columnas requeridas
        missing_columns = []
        for col in required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Columnas faltantes: {missing_columns}")
        
        # Verificar tipos de datos esperados
        if 'Fecha de Apertura' in df.columns:
            try:
                pd.to_datetime(df['Fecha de Apertura'].dropna().iloc[0], format='%Y-%m-%d %H:%M')
            except:
                validation_result['warnings'].append("Formato de fecha de apertura no reconocido. Esperado: YYYY-MM-DD HH:MM")
        
        # Verificar valores en campos críticos
        if 'Tipo' in df.columns:
            unique_types = df['Tipo'].dropna().unique()
            expected_types = ['Incidencia', 'Requerimiento']
            unexpected_types = [t for t in unique_types if t not in expected_types]
            if unexpected_types:
                validation_result['warnings'].append(f"Tipos de ticket inesperados: {unexpected_types}")
        
        if 'Estado' in df.columns:
            unique_states = df['Estado'].dropna().unique()
            expected_states = ['Resueltas', 'Cerrado', 'En curso (asignada)', 'Nuevo', 'Pendiente']
            validation_result['info']['detected_states'] = list(unique_states)
        
        return validation_result
        
    except Exception as e:
        return {
            'valid': False,
            'errors': [f"Error al leer el archivo: {str(e)}"],
            'warnings': [],
            'info': {}
        }

def generate_sample_csv(output_path, num_records=50):
    """
    Genera un archivo CSV de muestra para pruebas
    
    Args:
        output_path (str): Ruta donde guardar el archivo
        num_records (int): Número de registros a generar
    """
    import random
    from faker import Faker
    
    fake = Faker('es_ES')
    
    # Datos de ejemplo
    tipos = ['Incidencia', 'Requerimiento']
    categorias = [
        'Red > cable de red',
        'Hardware > Impresora',
        'Software > Sistema operativo',
        'Hardware > Computador',
        'Red > Conectividad',
        'Software > Aplicación',
        'Telecomunicaciones > Teléfono',
        'Hardware > Monitor',
        'Software > Base de datos',
        'Red > Wi-Fi'
    ]
    prioridades = ['Alta', 'Mediana', 'Baja']
    estados = ['Resueltas', 'Cerrado', 'En curso (asignada)']
    tecnicos = [
        'JORGE AURELIO BETANCOURT CASTILLO',
        'SANTIAGO HURTADO MORENO',
        'SQL SQL',
        'CARLOS MARTINEZ LOPEZ',
        ''  # Sin asignar
    ]
    sla_levels = ['INC_ALTO', 'INC_MEDIO', 'INC_BAJO']
    
    data = []
    
    for i in range(num_records):
        fecha_apertura = fake.date_time_between(start_date='-30d', end_date='now')
        
        # Calcular fecha de solución (si está resuelto)
        estado = random.choice(estados)
        if estado in ['Resueltas', 'Cerrado']:
            fecha_solucion = fecha_apertura + timedelta(
                hours=random.randint(1, 72),
                minutes=random.randint(0, 59)
            )
            tiempo_solucion = f"{random.randint(1, 72)} hours"
        else:
            fecha_solucion = ''
            tiempo_solucion = ''
        
        # SLA
        sla_excedido = random.choice(['Si', 'No'])
        
        # Satisfacción (solo para algunos tickets)
        satisfaccion = random.choice([str(random.randint(1, 5)), '']) if random.random() > 0.3 else ''
        
        record = {
            'ID': str(100 + i),
            'Título': fake.sentence(nb_words=6),
            'Tipo': random.choice(tipos),
            'Categoría': random.choice(categorias),
            'Prioridad': random.choice(prioridades),
            'Estado': estado,
            'Fecha de Apertura': fecha_apertura.strftime('%Y-%m-%d %H:%M'),
            'Fecha de solución': fecha_solucion.strftime('%Y-%m-%d %H:%M') if fecha_solucion else '',
            'Tiempo de solución': tiempo_solucion,
            'Duración total': '0 seconds',
            'Última actualización': fecha_apertura.strftime('%Y-%m-%d %H:%M'),
            'Asignado a: - Técnico': random.choice(tecnicos),
            'Solicitante - Solicitante': fake.name().upper(),
            'Elementos asociados': fake.random_element(elements=('', 'PC-001', 'IMP-002', 'MON-003')),
            'ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución': random.choice(sla_levels) if record['Tipo'] == 'Incidencia' else '',
            'Se superó el tiempo de resolución': sla_excedido,
            'Estadísticas - Tiempo de solución': tiempo_solucion,
            'Costo - Costo de material': '',
            'Costo - Costo total': '',
            'Encuesta de satisfacción - Satisfacción': satisfaccion,
            '': ''  # Columna extra vacía
        }
        
        data.append(record)
    
    # Crear DataFrame y guardar
    df = pd.DataFrame(data)
    df.to_csv(output_path, sep=';', index=False, encoding='utf-8')
    print(f"Archivo CSV de muestra generado: {output_path}")
    print(f"Registros creados: {num_records}")

def analyze_data_quality(csv_path):
    """
    Analiza la calidad de los datos en el CSV
    
    Args:
        csv_path (str): Ruta al archivo CSV
        
    Returns:
        dict: Reporte de calidad de datos
    """
    try:
        df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')
        
        report = {
            'general': {
                'total_records': len(df),
                'total_columns': len(df.columns),
                'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
            },
            'completeness': {},
            'consistency': {},
            'validity': {}
        }
        
        # Análisis de completitud
        for col in df.columns:
            if col.strip():  # Ignorar columnas vacías
                null_count = df[col].isnull().sum()
                empty_count = (df[col] == '').sum()
                total_missing = null_count + empty_count
                completeness_rate = ((len(df) - total_missing) / len(df)) * 100
                
                report['completeness'][col] = {
                    'missing_count': int(total_missing),
                    'completeness_rate': round(completeness_rate, 2)
                }
        
        # Análisis de consistencia
        if 'Tipo' in df.columns:
            type_values = df['Tipo'].dropna().unique()
            report['consistency']['ticket_types'] = list(type_values)
        
        if 'Estado' in df.columns:
            status_values = df['Estado'].dropna().unique()
            report['consistency']['status_values'] = list(status_values)
        
        if 'Prioridad' in df.columns:
            priority_values = df['Prioridad'].dropna().unique()
            report['consistency']['priority_values'] = list(priority_values)
        
        # Análisis de validez
        if 'Fecha de Apertura' in df.columns:
            try:
                date_col = pd.to_datetime(df['Fecha de Apertura'], format='%Y-%m-%d %H:%M', errors='coerce')
                invalid_dates = date_col.isnull().sum()
                report['validity']['invalid_opening_dates'] = int(invalid_dates)
            except:
                report['validity']['invalid_opening_dates'] = 'Error al procesar fechas'
        
        if 'Encuesta de satisfacción - Satisfacción' in df.columns:
            satisfaction_col = pd.to_numeric(df['Encuesta de satisfacción - Satisfacción'], errors='coerce')
            valid_scores = satisfaction_col.dropna()
            invalid_scores = satisfaction_col.isnull().sum() - df['Encuesta de satisfacción - Satisfacción'].isnull().sum()
            out_of_range = ((valid_scores < 1) | (valid_scores > 5)).sum()
            
            report['validity']['satisfaction_scores'] = {
                'invalid_format': int(invalid_scores),
                'out_of_range': int(out_of_range),
                'valid_responses': int(len(valid_scores) - out_of_range)
            }
        
        return report
        
    except Exception as e:
        return {'error': f"Error al analizar los datos: {str(e)}"}

def export_summary_report(csv_path, output_path):
    """
    Exporta un reporte resumen en formato JSON
    
    Args:
        csv_path (str): Ruta al archivo CSV
        output_path (str): Ruta donde guardar el reporte
    """
    from app import TicketAnalyzer
    
    try:
        # Crear instancia del analizador
        analyzer = TicketAnalyzer(data_path=os.path.dirname(csv_path))
        
        # Recopilar todas las métricas
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'source_file': os.path.basename(csv_path),
                'generator': 'Clínica Bonsana Dashboard IT'
            },
            'metrics': analyzer.get_overall_metrics(),
            'distributions': analyzer.get_ticket_distribution(),
            'technician_workload': analyzer.get_technician_workload(),
            'top_requesters': analyzer.get_top_requesters(),
            'sla_analysis': analyzer.get_sla_analysis(),
            'csat': analyzer.get_csat_score(),
            'data_validation': analyzer.get_data_validation_insights(),
            'data_quality': analyze_data_quality(csv_path)
        }
        
        # Guardar reporte
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Reporte exportado: {output_path}")
        return report
        
    except Exception as e:
        print(f"Error al generar reporte: {str(e)}")
        return None

def main():
    """Función principal para ejecutar utilidades desde línea de comandos"""
    parser = argparse.ArgumentParser(description='Utilidades para Dashboard IT - Clínica Bonsana')
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando para validar CSV
    validate_parser = subparsers.add_parser('validate', help='Validar estructura del CSV')
    validate_parser.add_argument('csv_path', help='Ruta al archivo CSV')
    
    # Comando para generar CSV de muestra
    sample_parser = subparsers.add_parser('generate-sample', help='Generar CSV de muestra')
    sample_parser.add_argument('output_path', help='Ruta donde guardar el archivo')
    sample_parser.add_argument('--records', type=int, default=50, help='Número de registros a generar')
    
    # Comando para analizar calidad de datos
    quality_parser = subparsers.add_parser('analyze-quality', help='Analizar calidad de datos')
    quality_parser.add_argument('csv_path', help='Ruta al archivo CSV')
    
    # Comando para exportar reporte
    report_parser = subparsers.add_parser('export-report', help='Exportar reporte completo')
    report_parser.add_argument('csv_path', help='Ruta al archivo CSV')
    report_parser.add_argument('output_path', help='Ruta donde guardar el reporte JSON')
    
    args = parser.parse_args()
    
    if args.command == 'validate':
        result = validate_csv_structure(args.csv_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif args.command == 'generate-sample':
        generate_sample_csv(args.output_path, args.records)
        
    elif args.command == 'analyze-quality':
        result = analyze_data_quality(args.csv_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif args.command == 'export-report':
        export_summary_report(args.csv_path, args.output_path)
        
    else:
        parser.print_help()

if __name__ == '__main__':
    main()