#!/usr/bin/env python3
"""
Script para diagnosticar las diferencias en el cálculo de SLA
"""

import pandas as pd
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def debug_sla_calculations():
    """Analiza las diferencias en el cálculo de SLA"""
    
    csv_path = Path("data/glpi.csv")
    
    if not csv_path.exists():
        print("❌ Archivo data/glpi.csv no encontrado")
        return
    
    print("🔍 ANÁLISIS DE CÁLCULOS DE SLA")
    print("=" * 60)
    
    # Cargar datos con el mismo método que la aplicación
    encodings_to_try = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
    df = None
    
    for encoding in encodings_to_try:
        try:
            df = pd.read_csv(
                csv_path, 
                delimiter=';', 
                encoding=encoding,
                quotechar='"',
                skipinitialspace=True,
                na_values=['', 'NULL', 'null', 'N/A', 'n/a']
            )
            print(f"✅ Archivo cargado con encoding: {encoding}")
            break
        except Exception as e:
            continue
    
    if df is None:
        print("❌ No se pudo cargar el archivo")
        return
    
    print(f"📊 Total de registros: {len(df)}")
    print(f"📋 Columnas: {len(df.columns)}")
    
    # Verificar columnas clave
    print(f"\n📋 COLUMNAS SLA RELEVANTES:")
    sla_columns = [
        'Tipo',
        'Se superó el tiempo de resolución',
        'ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución'
    ]
    
    for col in sla_columns:
        exists = col in df.columns
        print(f"   {'✅' if exists else '❌'} '{col}' - {'ENCONTRADA' if exists else 'FALTANTE'}")
    
    # CÁLCULO 1: Método get_overall_metrics() - TODOS LOS TICKETS
    print(f"\n🧮 CÁLCULO 1: get_overall_metrics() (TODOS LOS TICKETS)")
    print("-" * 50)
    
    total_tickets = len(df)
    sla_exceeded_all = 0
    
    if 'Se superó el tiempo de resolución' in df.columns:
        sla_exceeded_all = len(df[df['Se superó el tiempo de resolución'] == 'Si'])
    
    sla_compliance_all = ((total_tickets - sla_exceeded_all) / total_tickets * 100) if total_tickets > 0 else 0
    
    print(f"   📊 Total tickets: {total_tickets}")
    print(f"   ⚠️  SLA excedido: {sla_exceeded_all}")
    print(f"   ✅ SLA cumplido: {total_tickets - sla_exceeded_all}")
    print(f"   📈 Cumplimiento SLA: {round(sla_compliance_all, 1)}%")
    
    # CÁLCULO 2: Método get_sla_analysis() - SOLO INCIDENCIAS
    print(f"\n🧮 CÁLCULO 2: get_sla_analysis() (SOLO INCIDENCIAS)")
    print("-" * 50)
    
    if 'Tipo' in df.columns:
        incidents = df[df['Tipo'] == 'Incidencia']
        print(f"   📊 Total incidencias: {len(incidents)}")
        
        sla_exceeded_incidents = 0
        if 'Se superó el tiempo de resolución' in incidents.columns:
            sla_exceeded_incidents = len(incidents[incidents['Se superó el tiempo de resolución'] == 'Si'])
        
        sla_compliance_incidents = ((len(incidents) - sla_exceeded_incidents) / len(incidents) * 100) if len(incidents) > 0 else 0
        
        print(f"   ⚠️  SLA excedido: {sla_exceeded_incidents}")
        print(f"   ✅ SLA cumplido: {len(incidents) - sla_exceeded_incidents}")
        print(f"   📈 Cumplimiento SLA: {round(sla_compliance_incidents, 1)}%")
        
        # Análisis por nivel de SLA
        sla_column = 'ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución'
        if sla_column in incidents.columns:
            print(f"\n   📋 ANÁLISIS POR NIVEL DE SLA:")
            
            total_with_sla = 0
            total_exceeded_with_sla = 0
            
            for sla_level in incidents[sla_column].dropna().unique():
                level_incidents = incidents[incidents[sla_column] == sla_level]
                level_total = len(level_incidents)
                level_exceeded = len(level_incidents[level_incidents['Se superó el tiempo de resolución'] == 'Si'])
                level_within_sla = level_total - level_exceeded
                level_compliance = (level_within_sla / level_total * 100) if level_total > 0 else 0
                
                print(f"      📌 {sla_level}:")
                print(f"         Total: {level_total}")
                print(f"         Excedido: {level_exceeded}")
                print(f"         Cumplido: {level_within_sla}")
                print(f"         Compliance: {round(level_compliance, 1)}%")
                
                total_with_sla += level_total
                total_exceeded_with_sla += level_exceeded
            
            # Cálculo consolidado por niveles
            if total_with_sla > 0:
                consolidated_compliance = ((total_with_sla - total_exceeded_with_sla) / total_with_sla * 100)
                print(f"\n   🎯 CONSOLIDADO POR NIVELES:")
                print(f"      Total incidencias con SLA: {total_with_sla}")
                print(f"      Total excedidas: {total_exceeded_with_sla}")
                print(f"      Compliance consolidado: {round(consolidated_compliance, 1)}%")
    
    # COMPARACIÓN
    print(f"\n🔍 COMPARACIÓN DE RESULTADOS:")
    print("=" * 60)
    print(f"📊 Método 1 (Todos los tickets): {round(sla_compliance_all, 1)}%")
    print(f"📊 Método 2 (Solo incidencias): {round(sla_compliance_incidents, 1)}%")
    print(f"🔄 Diferencia: {round(abs(sla_compliance_all - sla_compliance_incidents), 1)} puntos porcentuales")
    
    # ANÁLISIS DE TIPOS
    print(f"\n📈 DISTRIBUCIÓN POR TIPO:")
    if 'Tipo' in df.columns:
        tipo_counts = df['Tipo'].value_counts()
        for tipo, count in tipo_counts.items():
            percentage = (count / len(df) * 100)
            print(f"   {tipo}: {count} ({percentage:.1f}%)")
    
    # ANÁLISIS SLA POR TIPO
    print(f"\n⚖️  ANÁLISIS SLA POR TIPO:")
    if 'Tipo' in df.columns and 'Se superó el tiempo de resolución' in df.columns:
        for tipo in df['Tipo'].unique():
            tipo_df = df[df['Tipo'] == tipo]
            tipo_total = len(tipo_df)
            tipo_exceeded = len(tipo_df[tipo_df['Se superó el tiempo de resolución'] == 'Si'])
            tipo_compliance = ((tipo_total - tipo_exceeded) / tipo_total * 100) if tipo_total > 0 else 0
            
            print(f"   {tipo}:")
            print(f"      Total: {tipo_total}")
            print(f"      Excedido: {tipo_exceeded}")
            print(f"      Compliance: {round(tipo_compliance, 1)}%")

if __name__ == '__main__':
    debug_sla_calculations()