#!/usr/bin/env python3
"""
Dashboard IT - Clínica Bonsana
Sistema de análisis y visualización de tickets de soporte IT
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

class TicketAnalyzer:
    def __init__(self, data_path='data'):
        self.data_path = data_path
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Carga los datos desde archivos CSV"""
        try:
            # Buscar archivos CSV en el directorio de datos
            csv_files = [f for f in os.listdir(self.data_path) if f.endswith('.csv')]
            
            if not csv_files:
                raise FileNotFoundError("No se encontraron archivos CSV en el directorio data/")
            
            # Por ahora usar el primer archivo CSV encontrado
            csv_file = os.path.join(self.data_path, csv_files[0])
            
            # Leer CSV con punto y coma como delimitador
            self.df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8')
            
            # Limpiar y procesar datos
            self.preprocess_data()
            
            print(f"Datos cargados exitosamente: {len(self.df)} registros")
            
        except Exception as e:
            print(f"Error al cargar los datos: {str(e)}")
            # Crear DataFrame vacío como fallback
            self.df = pd.DataFrame()
    
    def preprocess_data(self):
        """Preprocesa y limpia los datos"""
        if self.df.empty:
            return
        
        # Convertir fechas
        date_columns = ['Fecha de Apertura', 'Fecha de solución']
        for col in date_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], format='%Y-%m-%d %H:%M', errors='coerce')
        
        # Limpiar espacios en blanco
        string_columns = self.df.select_dtypes(include=['object']).columns
        for col in string_columns:
            self.df[col] = self.df[col].astype(str).str.strip()
        
        # Reemplazar valores vacíos con NaN
        self.df = self.df.replace(['', 'nan', 'None'], np.nan)
        
        # Calcular tiempo de resolución en horas
        mask_resolved = self.df['Fecha de solución'].notna()
        if mask_resolved.any():
            resolution_time = (self.df.loc[mask_resolved, 'Fecha de solución'] - 
                             self.df.loc[mask_resolved, 'Fecha de Apertura'])
            self.df.loc[mask_resolved, 'resolution_time_hours'] = resolution_time.dt.total_seconds() / 3600
    
    def get_overall_metrics(self):
        """Calcula métricas generales del dashboard"""
        if self.df.empty:
            return self._empty_metrics()
        
        total_tickets = len(self.df)
        
        # Estados que se consideran resueltos
        resolved_states = ['Resueltas', 'Cerrado']
        resolved_tickets = self.df[self.df['Estado'].isin(resolved_states)]
        resolution_rate = (len(resolved_tickets) / total_tickets * 100) if total_tickets > 0 else 0
        
        # Tiempo promedio de resolución (solo tickets resueltos)
        avg_resolution_time = resolved_tickets['resolution_time_hours'].mean() if not resolved_tickets.empty else 0
        
        # Cumplimiento SLA (solo incidencias)
        incidents = self.df[self.df['Tipo'] == 'Incidencia']
        if not incidents.empty:
            sla_compliant = incidents[incidents['Se superó el tiempo de resolución'] == 'No']
            sla_compliance = (len(sla_compliant) / len(incidents) * 100) if len(incidents) > 0 else 0
        else:
            sla_compliance = 0
        
        return {
            'total_tickets': total_tickets,
            'resolution_rate': round(resolution_rate, 1),
            'avg_resolution_time_hours': round(avg_resolution_time, 1) if pd.notna(avg_resolution_time) else 0,
            'sla_compliance': round(sla_compliance, 1),
            'pending_tickets': total_tickets - len(resolved_tickets)
        }
    
    def get_ticket_distribution(self):
        """Obtiene distribuciones de tickets por diferentes categorías"""
        if self.df.empty:
            return {}
        
        return {
            'by_type': self.df['Tipo'].value_counts().to_dict(),
            'by_status': self.df['Estado'].value_counts().to_dict(),
            'by_priority': self.df['Prioridad'].value_counts().to_dict(),
            'by_category': self.df['Categoría'].value_counts().head(10).to_dict()
        }
    
    def get_technician_workload(self):
        """Obtiene carga de trabajo por técnico incluyendo tickets sin asignar"""
        if self.df.empty:
            return {}
        
        tech_col = 'Asignado a: - Técnico'
        
        # Contar tickets asignados por técnico
        valid_technicians = self.df[self.df[tech_col].notna() & (self.df[tech_col] != '')]
        workload = valid_technicians[tech_col].value_counts().head(10).to_dict()
        
        # Contar tickets sin asignar
        unassigned_tickets = self.df[self.df[tech_col].isnull() | (self.df[tech_col] == '')]
        unassigned_count = len(unassigned_tickets)
        
        # Agregar tickets sin asignar si existen
        if unassigned_count > 0:
            workload['SIN ASIGNAR'] = unassigned_count
        
        return workload
    
    def get_technician_sla_stats(self):
        """Obtiene estadísticas de SLA por técnico asignado"""
        if self.df.empty:
            return {}
        
        tech_col = 'Asignado a: - Técnico'
        
        # Filtrar solo incidencias con técnico asignado
        incidents = self.df[
            (self.df['Tipo'] == 'Incidencia') & 
            (self.df[tech_col].notna()) & 
            (self.df[tech_col] != '')
        ]
        
        if incidents.empty:
            return {}
        
        sla_stats = {}
        
        for technician in incidents[tech_col].unique():
            tech_incidents = incidents[incidents[tech_col] == technician]
            total_incidents = len(tech_incidents)
            
            # Contar incidencias que NO superaron el SLA
            sla_compliant = len(tech_incidents[tech_incidents['Se superó el tiempo de resolución'] == 'No'])
            compliance_rate = (sla_compliant / total_incidents * 100) if total_incidents > 0 else 0
            
            sla_stats[technician] = {
                'total_incidents': total_incidents,
                'sla_compliant': sla_compliant,
                'sla_exceeded': total_incidents - sla_compliant,
                'compliance_rate': round(compliance_rate, 1)
            }
        
        # Ordenar por tasa de cumplimiento descendente
        return dict(sorted(sla_stats.items(), key=lambda x: x[1]['compliance_rate'], reverse=True))
    
    def get_technician_csat_stats(self):
        """Obtiene estadísticas de satisfacción del cliente por técnico"""
        if self.df.empty:
            return {}
        
        tech_col = 'Asignado a: - Técnico'
        csat_col = 'Encuesta de satisfacción - Satisfacción'
        
        # Filtrar tickets con técnico asignado y calificación CSAT
        valid_data = self.df[
            (self.df[tech_col].notna()) & 
            (self.df[tech_col] != '') &
            (self.df[csat_col].notna()) &
            (self.df[csat_col] != '')
        ].copy()
        
        if valid_data.empty:
            return {}
        
        # Convertir CSAT a numérico
        valid_data[csat_col] = pd.to_numeric(valid_data[csat_col], errors='coerce')
        valid_data = valid_data[valid_data[csat_col].between(1, 5)]
        
        if valid_data.empty:
            return {}
        
        csat_stats = {}
        
        for technician in valid_data[tech_col].unique():
            tech_surveys = valid_data[valid_data[tech_col] == technician]
            
            if not tech_surveys.empty:
                csat_scores = tech_surveys[csat_col]
                
                csat_stats[technician] = {
                    'total_surveys': len(csat_scores),
                    'average_csat': round(csat_scores.mean(), 2),
                    'csat_distribution': csat_scores.value_counts().sort_index().to_dict(),
                    'excellent_ratings': len(csat_scores[csat_scores >= 4]),  # 4 y 5 estrellas
                    'poor_ratings': len(csat_scores[csat_scores <= 2])  # 1 y 2 estrellas
                }
        
        # Ordenar por CSAT promedio descendente
        return dict(sorted(csat_stats.items(), key=lambda x: x[1]['average_csat'], reverse=True))
    
    def get_technician_resolution_time(self):
        """Obtiene tiempo de resolución promedio por técnico"""
        if self.df.empty:
            return {}
        
        tech_col = 'Asignado a: - Técnico'
        
        # Filtrar tickets resueltos con técnico asignado
        resolved_states = ['Resueltas', 'Cerrado']
        resolved_tickets = self.df[
            (self.df['Estado'].isin(resolved_states)) &
            (self.df[tech_col].notna()) & 
            (self.df[tech_col] != '') &
            (self.df['resolution_time_hours'].notna())
        ]
        
        if resolved_tickets.empty:
            return {}
        
        resolution_stats = {}
        
        for technician in resolved_tickets[tech_col].unique():
            tech_tickets = resolved_tickets[resolved_tickets[tech_col] == technician]
            resolution_times = tech_tickets['resolution_time_hours']
            
            if not resolution_times.empty:
                resolution_stats[technician] = {
                    'total_resolved': len(resolution_times),
                    'avg_resolution_hours': round(resolution_times.mean(), 2),
                    'min_resolution_hours': round(resolution_times.min(), 2),
                    'max_resolution_hours': round(resolution_times.max(), 2),
                    'median_resolution_hours': round(resolution_times.median(), 2),
                    'fast_resolutions': len(resolution_times[resolution_times <= 24]),  # Menos de 24h
                    'slow_resolutions': len(resolution_times[resolution_times > 72])   # Más de 72h
                }
        
        # Ordenar por tiempo promedio de resolución ascendente (más rápido primero)
        return dict(sorted(resolution_stats.items(), key=lambda x: x[1]['avg_resolution_hours']))
    
    def get_top_requesters(self):
        """Obtiene los principales solicitantes"""
        if self.df.empty:
            return {}
        
        requester_col = 'Solicitante - Solicitante'
        if requester_col in self.df.columns:
            valid_requesters = self.df[self.df[requester_col].notna() & (self.df[requester_col] != '')]
            return valid_requesters[requester_col].value_counts().head(10).to_dict()
        return {}
    
    def get_sla_analysis(self):
        """Análisis detallado de SLA"""
        if self.df.empty:
            return {}
        
        incidents = self.df[self.df['Tipo'] == 'Incidencia']
        
        if incidents.empty:
            return {}
        
        total_incidents = len(incidents)
        sla_exceeded = len(incidents[incidents['Se superó el tiempo de resolución'] == 'Si'])
        
        # Análisis por nivel de SLA
        sla_col = 'ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución'
        sla_compliance_by_level = {}
        
        if sla_col in incidents.columns:
            for sla_level in incidents[sla_col].dropna().unique():
                level_incidents = incidents[incidents[sla_col] == sla_level]
                level_total = len(level_incidents)
                level_within_sla = len(level_incidents[level_incidents['Se superó el tiempo de resolución'] == 'No'])
                
                sla_compliance_by_level[sla_level] = {
                    'total': level_total,
                    'within_sla': level_within_sla,
                    'exceeded': level_total - level_within_sla,
                    'compliance_rate': round((level_within_sla / level_total * 100) if level_total > 0 else 0, 1)
                }
        
        return {
            'total_incidents': total_incidents,
            'sla_exceeded': sla_exceeded,
            'sla_compliance_rate': round(((total_incidents - sla_exceeded) / total_incidents * 100) if total_incidents > 0 else 0, 1),
            'sla_compliance_by_level': sla_compliance_by_level
        }
    
    def get_csat_score(self):
        """Obtiene puntuación de satisfacción del cliente"""
        if self.df.empty:
            return {}
        
        csat_col = 'Encuesta de satisfacción - Satisfacción'
        
        if csat_col not in self.df.columns:
            return {}
        
        # Filtrar y convertir a numérico
        csat_data = pd.to_numeric(self.df[csat_col], errors='coerce')
        valid_csat = csat_data.dropna()
        valid_csat = valid_csat[valid_csat.between(1, 5)]
        
        if valid_csat.empty:
            return {}
        
        return {
            'average_csat': round(valid_csat.mean(), 2),
            'total_surveys': len(valid_csat),
            'distribution': valid_csat.value_counts().sort_index().to_dict()
        }
    
    def get_data_validation_insights(self):
        """Obtiene insights de validación de datos"""
        if self.df.empty:
            return {}
        
        insights = {}
        
        # Tickets sin técnico asignado
        tech_col = 'Asignado a: - Técnico'
        unassigned = self.df[self.df[tech_col].isnull() | (self.df[tech_col] == '')]
        if not unassigned.empty:
            insights['unassigned_tickets'] = {
                'count': len(unassigned),
                'percentage': round(len(unassigned) / len(self.df) * 100, 1),
                'recommendation': 'Asignar técnicos responsables para mejorar el seguimiento'
            }
        
        # Tickets sin categoría
        category_col = 'Categoría'
        no_category = self.df[self.df[category_col].isnull() | (self.df[category_col] == '')]
        if not no_category.empty:
            insights['no_category_tickets'] = {
                'count': len(no_category),
                'percentage': round(len(no_category) / len(self.df) * 100, 1),
                'recommendation': 'Categorizar tickets para mejor análisis y reporting'
            }
        
        # Tickets de hardware sin elementos asociados
        hardware_tickets = self.df[self.df['Categoría'].str.contains('Hardware', na=False, case=False)]
        if not hardware_tickets.empty:
            no_assets = hardware_tickets[hardware_tickets['Elementos asociados'].isnull() | 
                                       (hardware_tickets['Elementos asociados'] == '')]
            if not no_assets.empty:
                insights['hardware_no_assets'] = {
                    'count': len(no_assets),
                    'percentage': round(len(no_assets) / len(hardware_tickets) * 100, 1),
                    'recommendation': 'Asociar elementos de hardware para mejor gestión de activos'
                }
        
        return insights
    
    def _empty_metrics(self):
        """Retorna métricas vacías cuando no hay datos"""
        return {
            'total_tickets': 0,
            'resolution_rate': 0,
            'avg_resolution_time_hours': 0,
            'sla_compliance': 0,
            'pending_tickets': 0
        }

# Instancia global del analizador
analyzer = TicketAnalyzer()

@app.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('index.html')

@app.route('/api/metrics')
def api_metrics():
    """API endpoint para métricas generales"""
    return jsonify(analyzer.get_overall_metrics())

@app.route('/api/distributions')
def api_distributions():
    """API endpoint para distribuciones de tickets"""
    return jsonify(analyzer.get_ticket_distribution())

@app.route('/api/technicians')
def api_technicians():
    """API endpoint para carga de trabajo por técnico"""
    return jsonify(analyzer.get_technician_workload())

@app.route('/api/technicians/sla')
def api_technicians_sla():
    """API endpoint para estadísticas de SLA por técnico"""
    return jsonify(analyzer.get_technician_sla_stats())

@app.route('/api/technicians/csat')
def api_technicians_csat():
    """API endpoint para estadísticas de CSAT por técnico"""
    return jsonify(analyzer.get_technician_csat_stats())

@app.route('/api/technicians/resolution-time')
def api_technicians_resolution_time():
    """API endpoint para tiempo de resolución por técnico"""
    return jsonify(analyzer.get_technician_resolution_time())

@app.route('/api/requesters')
def api_requesters():
    """API endpoint para principales solicitantes"""
    return jsonify(analyzer.get_top_requesters())

@app.route('/api/sla')
def api_sla():
    """API endpoint para análisis de SLA"""
    return jsonify(analyzer.get_sla_analysis())

@app.route('/api/csat')
def api_csat():
    """API endpoint para puntuación CSAT"""
    return jsonify(analyzer.get_csat_score())

@app.route('/api/validation')
def api_validation():
    """API endpoint para insights de validación"""
    return jsonify(analyzer.get_data_validation_insights())

@app.route('/api/trends')
def api_trends():
    """API endpoint para tendencias mensuales"""
    # Implementación básica - se puede expandir
    return jsonify({'monthly_trends': {}})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)