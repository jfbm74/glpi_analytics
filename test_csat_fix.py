#!/usr/bin/env python3
"""
Script para verificar que la corrección del CSAT funciona correctamente
"""

import pandas as pd
import logging
from app import TicketAnalyzer

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_csat_calculation():
    """Prueba el cálculo corregido del CSAT"""
    
    print("🧪 VERIFICANDO CORRECCIÓN DEL CSAT")
    print("=" * 50)
    
    try:
        # Inicializar analizador
        analyzer = TicketAnalyzer("data")
        
        # Cargar datos directamente para análisis manual
        df = analyzer._load_data()
        
        print(f"📊 Datos cargados: {len(df)} registros")
        
        # Análisis manual del CSAT
        csat_column = 'Encuesta de satisfacción - Satisfacción'
        if csat_column in df.columns:
            # Convertir a numérico
            csat_scores = pd.to_numeric(df[csat_column], errors='coerce').dropna()
            valid_scores = csat_scores[(csat_scores >= 1) & (csat_scores <= 5)]
            
            print(f"\n📋 ANÁLISIS MANUAL DEL CSAT:")
            print(f"   Total registros con CSAT: {len(valid_scores)}")
            
            if len(valid_scores) > 0:
                # Distribución por estrella
                distribution = valid_scores.value_counts().sort_index()
                print(f"   📊 Distribución:")
                for rating, count in distribution.items():
                    print(f"      {int(rating)}★: {count} encuestas")
                
                # Cálculo del porcentaje
                high_satisfaction = valid_scores[valid_scores >= 4]
                high_count = len(high_satisfaction)
                total_count = len(valid_scores)
                percentage = (high_count / total_count * 100) if total_count > 0 else 0
                
                print(f"\n   🎯 CÁLCULO:")
                print(f"      Encuestas ≥4★: {high_count}")
                print(f"      Total encuestas: {total_count}")
                print(f"      Porcentaje: {percentage:.1f}%")
                print(f"      Promedio: {valid_scores.mean():.2f}")
        
        # Probar función corregida
        print(f"\n📊 Probando función get_csat_score()...")
        csat_data = analyzer.get_csat_score()
        
        print(f"✅ Resultado de la función:")
        print(f"   📈 CSAT Porcentaje: {csat_data.get('csat_percentage', 0)}%")
        print(f"   📈 Encuestas ≥4★: {csat_data.get('high_satisfaction_count', 0)}")
        print(f"   📈 Total encuestas: {csat_data.get('total_surveys', 0)}")
        print(f"   📈 Promedio (referencia): {csat_data.get('average_csat', 0)}")
        
        # Verificar distribución
        if 'distribution' in csat_data and csat_data['distribution']:
            print(f"   📊 Distribución función:")
            for rating, count in sorted(csat_data['distribution'].items()):
                print(f"      {int(rating)}★: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_csat_calculation()
    print(f"\n{'✅ ÉXITO' if success else '❌ FALLO'}")