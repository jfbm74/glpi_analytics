from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
from datetime import datetime
import os
from collections import Counter
import numpy as np
import asyncio
import logging
from dotenv import load_dotenv
from config import get_config

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
config = get_config()
app.config.from_object(config)

# Importar Google AI solo si está habilitado
if config.AI_ANALYSIS_ENABLED:
    try:
        import google.generativeai as genai
        if config.GOOGLE_AI_API_KEY:
            genai.configure(api_key=config.GOOGLE_AI_API_KEY)
            logger.info("Google AI Studio configurado correctamente")
        else:
            logger.warning("Google AI API Key no encontrada")
            config.AI_ANALYSIS_ENABLED = False
    except ImportError:
        logger.error("google-generativeai no instalado. Instala con: pip install google-generativeai")
        config.AI_ANALYSIS_ENABLED = False

class TicketAnalyzer:
    def __init__(self, data_path='data/'):
        """
        Inicializa el analizador de tickets
        
        Args:
            data_path (str): Ruta al directorio de datos
        """
        self.data_path = data_path
        self.df = None
        self.load_data()
    
    def load_data(self):
        """
        Carga los datos del CSV. Diseñado para ser extensible 
        para múltiples archivos CSV en el futuro.
        """
        try:
            # Por ahora carga solo glpi.csv, pero puede extenderse para múltiples archivos
            csv_files = [f for f in os.listdir(self.data_path) if f.endswith('.csv')]
            
            if not csv_files:
                raise FileNotFoundError("No se encontraron archivos CSV en el directorio de datos")
            
            # Por ahora usa el primer archivo CSV encontrado
            csv_path = os.path.join(self.data_path, csv_files[0])
            
            # Cargar con el delimitador correcto
            self.df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')
            
            # Limpiar nombres de columnas (remover espacios extra)
            self.df.columns = self.df.columns.str.strip()
            
            # Convertir fechas
            date_columns = ['Fecha de Apertura', 'Fecha de solución']
            for col in date_columns:
                if col in self.df.columns:
                    self.df[col] = pd.to_datetime(self.df[col], format='%Y-%m-%d %H:%M', errors='coerce')
            
            logger.info(f"Datos cargados exitosamente: {len(self.df)} tickets")
            
        except Exception as e:
            logger.error(f"Error al cargar los datos: {str(e)}")
            raise
    
    def get_csv_path(self):
        """
        Retorna la ruta del archivo CSV principal
        """
        csv_files = [f for f in os.listdir(self.data_path) if f.endswith('.csv')]
        if csv_files:
            return os.path.join(self.data_path, csv_files[0])
        return None
    
    def get_overall_metrics(self):
        """
        Calcula métricas generales de tickets
        """
        if self.df is None:
            return {}
        
        total_tickets = len(self.df)
        
        # Tickets resueltos (considerando 'Resueltas' y 'Cerrado' como resueltos)
        resolved_states = ['Resueltas', 'Cerrado']
        resolved_tickets = len(self.df[self.df['Estado'].isin(resolved_states)])
        resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0
        
        # Tiempo promedio de resolución (solo para tickets resueltos con fechas válidas)
        resolved_df = self.df[
            (self.df['Estado'].isin(resolved_states)) & 
            (self.df['Fecha de Apertura'].notna()) & 
            (self.df['Fecha de solución'].notna())
        ]
        
        if len(resolved_df) > 0:
            resolution_times = (resolved_df['Fecha de solución'] - resolved_df['Fecha de Apertura']).dt.total_seconds() / 3600  # en horas
            avg_resolution_time = resolution_times.mean()
        else:
            avg_resolution_time = 0
        
        # KPI: SLA Compliance para Incidencias
        incidents = self.df[self.df['Tipo'] == 'Incidencia']
        if len(incidents) > 0:
            incidents_within_sla = len(incidents[incidents['Se superó el tiempo de resolución'] == 'No'])
            sla_compliance = (incidents_within_sla / len(incidents)) * 100
        else:
            sla_compliance = 0
        
        # Backlog actual (tickets no resueltos)
        backlog = len(self.df[~self.df['Estado'].isin(resolved_states)])
        
        return {
            'total_tickets': total_tickets,
            'resolved_tickets': resolved_tickets,
            'resolution_rate': round(resolution_rate, 1),
            'avg_resolution_time_hours': round(avg_resolution_time, 2),
            'sla_compliance': round(sla_compliance, 1),
            'backlog': backlog
        }
    
    def get_ticket_distribution(self):
        """
        Obtiene distribuciones de tickets por diferentes categorías
        """
        if self.df is None:
            return {}
        
        # Distribución por tipo
        type_dist = self.df['Tipo'].value_counts().to_dict()
        
        # Distribución por estado
        status_dist = self.df['Estado'].value_counts().to_dict()
        
        # Distribución por prioridad
        priority_dist = self.df['Prioridad'].value_counts().to_dict()
        
        # Distribución por categoría (top 10)
        category_dist = self.df['Categoría'].fillna('Sin Categoría').value_counts().head(10).to_dict()
        
        return {
            'by_type': type_dist,
            'by_status': status_dist,
            'by_priority': priority_dist,
            'by_category': category_dist
        }
    
    def get_technician_workload(self):
        """
        Analiza la carga de trabajo por técnico
        """
        if self.df is None:
            return {}
        
        # Contar tickets por técnico
        technician_col = 'Asignado a: - Técnico'
        
        # Separar tickets asignados y no asignados
        assigned_tickets = self.df[self.df[technician_col].notna() & (self.df[technician_col].str.strip() != '')]
        unassigned_count = len(self.df) - len(assigned_tickets)
        
        technician_counts = assigned_tickets[technician_col].value_counts().to_dict()
        
        # Agregar tickets no asignados
        if unassigned_count > 0:
            technician_counts['Sin Asignar'] = unassigned_count
        
        return technician_counts
    
    def get_top_requesters(self, top_n=5):
        """
        Obtiene los solicitantes más activos
        """
        if self.df is None:
            return {}
        
        requester_col = 'Solicitante - Solicitante'
        top_requesters = self.df[requester_col].fillna('Desconocido').value_counts().head(top_n).to_dict()
        
        return top_requesters
    
    def get_sla_analysis(self):
        """
        Analiza el cumplimiento de SLA
        """
        if self.df is None:
            return {}
        
        # Solo para incidencias
        incidents = self.df[self.df['Tipo'] == 'Incidencia']
        
        if len(incidents) == 0:
            return {
                'total_incidents': 0,
                'sla_exceeded': 0,
                'sla_compliance_by_level': {}
            }
        
        # Tickets que excedieron SLA
        sla_exceeded = len(incidents[incidents['Se superó el tiempo de resolución'] == 'Si'])
        
        # Cumplimiento por nivel de SLA
        sla_col = 'ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución'
        sla_levels = incidents[sla_col].fillna('Sin SLA').value_counts().to_dict()
        
        # Calcular cumplimiento por nivel
        sla_compliance_by_level = {}
        for level in sla_levels.keys():
            if level != 'Sin SLA':
                level_incidents = incidents[incidents[sla_col] == level]
                within_sla = len(level_incidents[level_incidents['Se superó el tiempo de resolución'] == 'No'])
                compliance_rate = (within_sla / len(level_incidents)) * 100 if len(level_incidents) > 0 else 0
                sla_compliance_by_level[level] = {
                    'total': len(level_incidents),
                    'within_sla': within_sla,
                    'compliance_rate': round(compliance_rate, 1)
                }
        
        return {
            'total_incidents': len(incidents),
            'sla_exceeded': sla_exceeded,
            'sla_compliance_by_level': sla_compliance_by_level
        }
    
    def get_csat_score(self):
        """
        Calcula el Customer Satisfaction Score (CSAT)
        """
        if self.df is None:
            return {}
        
        satisfaction_col = 'Encuesta de satisfacción - Satisfacción'
        
        # Filtrar valores numéricos válidos
        satisfaction_scores = pd.to_numeric(self.df[satisfaction_col], errors='coerce')
        valid_scores = satisfaction_scores.dropna()
        
        if len(valid_scores) == 0:
            return {
                'average_csat': 0,
                'total_surveys': 0,
                'distribution': {}
            }
        
        average_csat = valid_scores.mean()
        total_surveys = len(valid_scores)
        
        # Distribución de puntuaciones
        distribution = valid_scores.value_counts().sort_index().to_dict()
        
        return {
            'average_csat': round(average_csat, 2),
            'total_surveys': total_surveys,
            'distribution': distribution
        }
    
    def get_data_validation_insights(self):
        """
        Identifica problemas en los datos y proporciona recomendaciones
        """
        if self.df is None:
            return {}
        
        insights = {}
        
        # Tickets sin técnico asignado
        unassigned = self.df[
            (self.df['Asignado a: - Técnico'].isna()) | 
            (self.df['Asignado a: - Técnico'].str.strip() == '')
        ]
        insights['unassigned_tickets'] = {
            'count': len(unassigned),
            'tickets': unassigned[['ID', 'Título', 'Estado']].to_dict('records') if len(unassigned) > 0 else [],
            'recommendation': 'Asignar un técnico al crear el ticket.'
        }
        
        # Tickets sin categoría
        no_category = self.df[
            (self.df['Categoría'].isna()) | 
            (self.df['Categoría'].str.strip() == '')
        ]
        insights['no_category_tickets'] = {
            'count': len(no_category),
            'tickets': no_category[['ID', 'Título', 'Estado']].to_dict('records') if len(no_category) > 0 else [],
            'recommendation': 'Establecer categoría al inicio del ticket.'
        }
        
        # Tickets de hardware sin elementos asociados
        hardware_keywords = ['Impresora', 'Computador', 'Equipo', 'Hardware', 'PC']
        hardware_tickets = self.df[
            self.df['Categoría'].str.contains('|'.join(hardware_keywords), case=False, na=False) &
            ((self.df['Elementos asociados'].isna()) | (self.df['Elementos asociados'].str.strip() == ''))
        ]
        insights['hardware_no_assets'] = {
            'count': len(hardware_tickets),
            'tickets': hardware_tickets[['ID', 'Título', 'Categoría']].to_dict('records') if len(hardware_tickets) > 0 else [],
            'recommendation': 'Asociar el equipo afectado en tickets de hardware.'
        }
        
        return insights
    
    def get_monthly_trends(self):
        """
        Analiza tendencias mensuales de tickets
        """
        if self.df is None:
            return {}
        
        # Agrupar por mes de apertura
        monthly_data = self.df.groupby(self.df['Fecha de Apertura'].dt.to_period('M')).size()
        
        trends = {}
        for period, count in monthly_data.items():
            month_key = str(period)
            trends[month_key] = count
        
        return trends

class AIAnalysisService:
    """Servicio para análisis con Google AI Studio"""
    
    def __init__(self):
        self.model = None
        if config.AI_ANALYSIS_ENABLED and config.GOOGLE_AI_API_KEY:
            try:
                self.model = genai.GenerativeModel(config.GOOGLE_AI_MODEL)
                logger.info(f"Modelo AI inicializado: {config.GOOGLE_AI_MODEL}")
            except Exception as e:
                logger.error(f"Error inicializando modelo AI: {e}")
                config.AI_ANALYSIS_ENABLED = False
    
    def is_available(self):
        """Verifica si el servicio de AI está disponible"""
        return config.AI_ANALYSIS_ENABLED and self.model is not None
    
    def prepare_csv_data(self, csv_path):
        """
        Prepara los datos CSV para envío a la AI
        """
        try:
            # Verificar tamaño del archivo
            file_size_mb = os.path.getsize(csv_path) / (1024 * 1024)
            if file_size_mb > config.AI_CONFIG['max_csv_size_mb']:
                raise ValueError(f"Archivo CSV muy grande: {file_size_mb:.1f}MB. Máximo permitido: {config.AI_CONFIG['max_csv_size_mb']}MB")
            
            # Leer CSV
            df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')
            
            # Limpiar y preparar datos
            # Eliminar columnas completamente vacías
            df = df.dropna(axis=1, how='all')
            
            # Limitar a primeras 1000 filas para análisis si es muy grande
            if len(df) > 1000:
                logger.warning(f"CSV muy grande ({len(df)} filas), limitando a 1000 filas para análisis")
                df = df.head(1000)
            
            # Convertir a string para envío
            csv_string = df.to_csv(sep=';', index=False)
            
            return csv_string
            
        except Exception as e:
            logger.error(f"Error preparando datos CSV: {e}")
            raise
    
    def analyze_tickets(self, csv_path):
        """
        Realiza análisis completo de tickets usando Google AI Studio
        """
        if not self.is_available():
            raise Exception("Servicio de AI no disponible")
        
        try:
            # Preparar datos
            csv_data = self.prepare_csv_data(csv_path)
            
            # Crear prompt con datos
            prompt = config.AI_CONFIG['prompt_template'].format(csv_data=csv_data)
            
            logger.info("Enviando solicitud a Google AI Studio...")
            
            # Generar respuesta
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'max_output_tokens': 8192,
                }
            )
            
            logger.info("Análisis completado exitosamente")
            
            return {
                'success': True,
                'analysis': response.text,
                'timestamp': datetime.now().isoformat(),
                'model_used': config.GOOGLE_AI_MODEL,
                'csv_rows_analyzed': csv_data.count('\n') - 1  # Menos header
            }
            
        except Exception as e:
            logger.error(f"Error en análisis AI: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Instancia global del analizador
analyzer = TicketAnalyzer()
ai_service = AIAnalysisService()

@app.route('/')
def dashboard():
    """
    Página principal del dashboard
    """
    return render_template('index.html', ai_enabled=config.AI_ANALYSIS_ENABLED)

@app.route('/api/metrics')
def api_metrics():
    """
    API endpoint para métricas generales
    """
    try:
        metrics = analyzer.get_overall_metrics()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/distributions')
def api_distributions():
    """
    API endpoint para distribuciones de tickets
    """
    try:
        distributions = analyzer.get_ticket_distribution()
        return jsonify(distributions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/technicians')
def api_technicians():
    """
    API endpoint para carga de trabajo de técnicos
    """
    try:
        workload = analyzer.get_technician_workload()
        return jsonify(workload)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/requesters')
def api_requesters():
    """
    API endpoint para principales solicitantes
    """
    try:
        requesters = analyzer.get_top_requesters()
        return jsonify(requesters)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sla')
def api_sla():
    """
    API endpoint para análisis de SLA
    """
    try:
        sla_data = analyzer.get_sla_analysis()
        return jsonify(sla_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/csat')
def api_csat():
    """
    API endpoint para puntuación CSAT
    """
    try:
        csat_data = analyzer.get_csat_score()
        return jsonify(csat_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validation')
def api_validation():
    """
    API endpoint para insights de validación de datos
    """
    try:
        validation_data = analyzer.get_data_validation_insights()
        return jsonify(validation_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trends')
def api_trends():
    """
    API endpoint para tendencias mensuales
    """
    try:
        trends = analyzer.get_monthly_trends()
        return jsonify(trends)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/analyze', methods=['POST'])
def api_ai_analyze():
    """
    API endpoint para análisis con Google AI Studio
    """
    try:
        if not ai_service.is_available():
            return jsonify({
                'success': False,
                'error': 'Servicio de AI no disponible. Verifica la configuración de Google AI Studio API Key.'
            }), 503
        
        # Obtener ruta del CSV
        csv_path = analyzer.get_csv_path()
        if not csv_path:
            return jsonify({
                'success': False,
                'error': 'No se encontró archivo CSV para analizar'
            }), 404
        
        # Realizar análisis
        result = ai_service.analyze_tickets(csv_path)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error en endpoint AI: {e}")
        return jsonify({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }), 500

@app.route('/api/ai/status')
def api_ai_status():
    """
    API endpoint para verificar estado del servicio AI
    """
    return jsonify({
        'ai_enabled': config.AI_ANALYSIS_ENABLED,
        'api_key_configured': bool(config.GOOGLE_AI_API_KEY),
        'model': config.GOOGLE_AI_MODEL if config.AI_ANALYSIS_ENABLED else None,
        'service_available': ai_service.is_available()
    })

@app.route('/health')
def health_check():
    """
    Endpoint para verificación de salud del servicio
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': config.APP_VERSION,
        'ai_enabled': config.AI_ANALYSIS_ENABLED
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)