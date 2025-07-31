#!/usr/bin/env python3
"""
Script para verificar que la corrección de SLA funciona correctamente
"""

import sys
import logging
from app import TicketAnalyzer

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_sla_correction():
    """Prueba la corrección del cálculo de SLA"""
    
    print("🧪 VERIFICANDO CORRECCIÓN DE SLA")
    print("=" * 50)
    
    try:
        # Inicializar analizador
        analyzer = TicketAnalyzer("data")
        
        # Obtener métricas generales (corregidas)
        print("📊 Obteniendo métricas generales...")
        metrics = analyzer.get_overall_metrics()
        
        print(f"✅ Métricas obtenidas:")
        print(f"   📈 Total tickets: {metrics.get('total_tickets', 0)}")
        print(f"   📈 Tasa de resolución: {metrics.get('resolution_rate', 0)}%")
        print(f"   📈 SLA compliance (CORREGIDO): {metrics.get('sla_compliance', 0)}%")
        
        # Obtener análisis SLA detallado para comparar
        print(f"\n📊 Obteniendo análisis SLA detallado...")
        sla_analysis = analyzer.get_sla_analysis()
        
        print(f"✅ Análisis SLA detallado:")
        print(f"   📈 Total incidencias: {sla_analysis.get('total_incidents', 0)}")
        print(f"   📈 SLA excedido: {sla_analysis.get('sla_exceeded', 0)}")
        print(f"   📈 SLA compliance rate: {sla_analysis.get('sla_compliance_rate', 0)}%")
        
        # Verificar que ahora coinciden
        metrics_sla = metrics.get('sla_compliance', 0)
        analysis_sla = sla_analysis.get('sla_compliance_rate', 0)
        
        print(f"\n🔍 COMPARACIÓN:")
        print(f"   Métricas generales: {metrics_sla}%")
        print(f"   Análisis SLA: {analysis_sla}%")
        
        if abs(metrics_sla - analysis_sla) < 0.1:  # Tolerancia de 0.1%
            print(f"   ✅ ¡CORREGIDO! Los valores ahora coinciden")
        else:
            print(f"   ❌ Los valores aún difieren en {abs(metrics_sla - analysis_sla):.1f} puntos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_sla_correction()
    sys.exit(0 if success else 1)