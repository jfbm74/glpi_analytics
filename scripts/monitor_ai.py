#!/usr/bin/env python3
"""
Script de monitoreo para la funcionalidad IA
Dashboard IT - Clínica Bonsana
"""

import os
import sys
import time
import json
import logging
import argparse
import requests
import smtplib
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from dataclasses import dataclass
from typing import Dict, List, Optional
import subprocess

@dataclass
class HealthStatus:
    """Estado de salud del servicio IA"""
    timestamp: str
    service_available: bool
    api_key_valid: bool
    model_accessible: bool
    response_time_ms: Optional[float]
    error_message: Optional[str]
    last_analysis_time: Optional[str]
    analysis_success_rate: float

class AIMonitor:
    """Monitor para servicios de IA"""
    
    def __init__(self, config_file=None):
        self.project_root = Path(__file__).parent
        self.config = self.load_config(config_file)
        self.setup_logging()
        
        # Estados y métricas
        self.health_history = []
        self.alert_history = []
        self.metrics = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'avg_response_time': 0,
            'uptime_percentage': 0
        }
        
        # URLs del dashboard
        self.base_url = self.config.get('dashboard_url', 'http://localhost:5000')
        self.ai_status_url = f"{self.base_url}/api/ai/status"
        self.health_url = f"{self.base_url}/health"
        
    def load_config(self, config_file):
        """Carga configuración del monitor"""
        default_config = {
            'dashboard_url': 'http://localhost:5000',
            'check_interval': 60,  # segundos
            'alert_threshold': 3,  # fallos consecutivos antes de alertar
            'response_time_threshold': 5000,  # ms
            'email_alerts': False,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email_from': '',
            'email_to': [],
            'log_level': 'INFO',
            'retention_days': 7
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"Error cargando configuración: {e}")
        
        return default_config
    
    def setup_logging(self):
        """Configura el sistema de logging"""
        log_level = getattr(logging, self.config['log_level'].upper())
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ai_monitor.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('AIMonitor')
    
    def check_ai_health(self) -> HealthStatus:
        """Verifica el estado de salud del servicio IA"""
        start_time = time.time()
        
        try:
            # Verificar endpoint de estado IA
            response = requests.get(
                self.ai_status_url,
                timeout=self.config.get('request_timeout', 10)
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # ms
            
            if response.status_code == 200:
                data = response.json()
                
                return HealthStatus(
                    timestamp=datetime.now().isoformat(),
                    service_available=data.get('service_available', False),
                    api_key_valid=data.get('api_key_configured', False),
                    model_accessible=data.get('model', '') != '',
                    response_time_ms=response_time,
                    error_message=None,
                    last_analysis_time=self.get_last_analysis_time(),
                    analysis_success_rate=self.get_analysis_success_rate()
                )
            else:
                return HealthStatus(
                    timestamp=datetime.now().isoformat(),
                    service_available=False,
                    api_key_valid=False,
                    model_accessible=False,
                    response_time_ms=response_time,
                    error_message=f"HTTP {response.status_code}",
                    last_analysis_time=None,
                    analysis_success_rate=0.0
                )
                
        except requests.RequestException as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return HealthStatus(
                timestamp=datetime.now().isoformat(),
                service_available=False,
                api_key_valid=False,
                model_accessible=False,
                response_time_ms=response_time,
                error_message=str(e),
                last_analysis_time=None,
                analysis_success_rate=0.0
            )
    
    def get_last_analysis_time(self) -> Optional[str]:
        """Obtiene el timestamp del último análisis exitoso"""
        try:
            # Buscar en logs o archivos de análisis
            analysis_files = list(self.project_root.glob('test_analysis_*.txt'))
            if analysis_files:
                latest_file = max(analysis_files, key=os.path.getctime)
                return datetime.fromtimestamp(os.path.getctime(latest_file)).isoformat()
        except Exception:
            pass
        return None
    
    def get_analysis_success_rate(self) -> float:
        """Calcula la tasa de éxito de análisis en las últimas 24 horas"""
        try:
            # Esta sería implementada con métricas más detalladas
            # Por ahora retorna un valor estimado basado en checks recientes
            recent_checks = [h for h in self.health_history 
                           if datetime.fromisoformat(h.timestamp) > datetime.now() - timedelta(hours=24)]
            
            if not recent_checks:
                return 0.0
            
            successful = sum(1 for h in recent_checks if h.service_available)
            return (successful / len(recent_checks)) * 100
            
        except Exception:
            return 0.0
    
    def update_metrics(self, health: HealthStatus):
        """Actualiza métricas del monitor"""
        self.metrics['total_checks'] += 1
        
        if health.service_available:
            self.metrics['successful_checks'] += 1
        else:
            self.metrics['failed_checks'] += 1
        
        # Actualizar tiempo de respuesta promedio
        if health.response_time_ms:
            current_avg = self.metrics['avg_response_time']
            total_checks = self.metrics['total_checks']
            
            self.metrics['avg_response_time'] = (
                (current_avg * (total_checks - 1) + health.response_time_ms) / total_checks
            )
        
        # Calcular uptime
        self.metrics['uptime_percentage'] = (
            self.metrics['successful_checks'] / self.metrics['total_checks']
        ) * 100
    
    def should_alert(self, health: HealthStatus) -> bool:
        """Determina si se debe enviar una alerta"""
        # Revisar últimos N checks
        threshold = self.config['alert_threshold']
        recent_checks = self.health_history[-threshold:]
        
        if len(recent_checks) < threshold:
            return False
        
        # Verificar si todos los últimos checks han fallado
        all_failed = all(not h.service_available for h in recent_checks)
        
        # Verificar tiempo de respuesta alto
        slow_response = health.response_time_ms and health.response_time_ms > self.config['response_time_threshold']
        
        # No enviar alerta duplicada en la última hora
        recent_alerts = [a for a in self.alert_history 
                        if datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(hours=1)]
        
        has_recent_alert = any(a['type'] in ['service_down', 'slow_response'] for a in recent_alerts)
        
        return (all_failed or slow_response) and not has_recent_alert
    
    def send_alert(self, health: HealthStatus, alert_type: str):
        """Envía alerta por email"""
        if not self.config['email_alerts'] or not self.config['email_to']:
            self.logger.info(f"Alerta generada ({alert_type}) pero email no configurado")
            return
        
        try:
            # Crear mensaje
            msg = MimeMultipart()
            msg['From'] = self.config['email_from']
            msg['To'] = ', '.join(self.config['email_to'])
            
            if alert_type == 'service_down':
                msg['Subject'] = '🚨 ALERTA: Servicio IA Dashboard IT No Disponible'
                body = self.create_service_down_alert(health)
            elif alert_type == 'slow_response':
                msg['Subject'] = '⚠️ ALERTA: Servicio IA Dashboard IT Respuesta Lenta'
                body = self.create_slow_response_alert(health)
            else:
                msg['Subject'] = f'📊 Dashboard IT: {alert_type}'
                body = f"Estado del servicio IA: {health}"
            
            msg.attach(MimeText(body, 'html'))
            
            # Enviar email
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                if self.config.get('smtp_user') and self.config.get('smtp_password'):
                    server.login(self.config['smtp_user'], self.config['smtp_password'])
                
                server.send_message(msg)
            
            self.logger.info(f"Alerta enviada: {alert_type}")
            
            # Registrar alerta
            self.alert_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': alert_type,
                'recipients': self.config['email_to']
            })
            
        except Exception as e:
            self.logger.error(f"Error enviando alerta: {e}")
    
    def create_service_down_alert(self, health: HealthStatus) -> str:
        """Crea el contenido HTML para alerta de servicio caído"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #dc3545;">
                <h2 style="color: #dc3545; margin-top: 0;">🚨 Servicio IA No Disponible</h2>
                
                <p><strong>Dashboard IT - Clínica Bonsana</strong></p>
                
                <div style="background: white; padding: 15px; border-radius: 4px; margin: 15px 0;">
                    <h3>Detalles del Problema:</h3>
                    <ul>
                        <li><strong>Timestamp:</strong> {health.timestamp}</li>
                        <li><strong>Servicio Disponible:</strong> {'✅ Sí' if health.service_available else '❌ No'}</li>
                        <li><strong>API Key Válida:</strong> {'✅ Sí' if health.api_key_valid else '❌ No'}</li>
                        <li><strong>Tiempo de Respuesta:</strong> {health.response_time_ms:.0f}ms</li>
                        <li><strong>Error:</strong> {health.error_message or 'N/A'}</li>
                    </ul>
                </div>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 4px; border: 1px solid #ffeaa7;">
                    <h3>Acciones Recomendadas:</h3>
                    <ol>
                        <li>Verificar conectividad con Google AI Studio</li>
                        <li>Revisar configuración de API Key</li>
                        <li>Comprobar logs de la aplicación</li>
                        <li>Reiniciar servicios si es necesario</li>
                    </ol>
                </div>
                
                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #dee2e6;">
                    <p><strong>Métricas Actuales:</strong></p>
                    <ul>
                        <li>Uptime: {self.metrics['uptime_percentage']:.1f}%</li>
                        <li>Checks Exitosos: {self.metrics['successful_checks']}/{self.metrics['total_checks']}</li>
                        <li>Tiempo Respuesta Promedio: {self.metrics['avg_response_time']:.0f}ms</li>
                    </ul>
                </div>
                
                <p style="margin-top: 20px; color: #6c757d; font-size: 0.9em;">
                    Este es un mensaje automático del sistema de monitoreo.
                </p>
            </div>
        </body>
        </html>
        """
    
    def create_slow_response_alert(self, health: HealthStatus) -> str:
        """Crea el contenido HTML para alerta de respuesta lenta"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107;">
                <h2 style="color: #e91e63; margin-top: 0;">⚠️ Servicio IA Respuesta Lenta</h2>
                
                <p><strong>Dashboard IT - Clínica Bonsana</strong></p>
                
                <div style="background: white; padding: 15px; border-radius: 4px; margin: 15px 0;">
                    <h3>Detalles del Rendimiento:</h3>
                    <ul>
                        <li><strong>Tiempo de Respuesta Actual:</strong> {health.response_time_ms:.0f}ms</li>
                        <li><strong>Umbral Configurado:</strong> {self.config['response_time_threshold']}ms</li>
                        <li><strong>Tiempo Promedio:</strong> {self.metrics['avg_response_time']:.0f}ms</li>
                        <li><strong>Timestamp:</strong> {health.timestamp}</li>
                    </ul>
                </div>
                
                <p style="margin-top: 20px; color: #6c757d; font-size: 0.9em;">
                    Considera revisar la carga del sistema y la conectividad de red.
                </p>
            </div>
        </body>
        </html>
        """
    
    def generate_report(self) -> Dict:
        """Genera reporte de estado actual"""
        current_health = self.check_ai_health()
        
        # Estadísticas de las últimas 24 horas
        last_24h = [h for h in self.health_history 
                   if datetime.fromisoformat(h.timestamp) > datetime.now() - timedelta(hours=24)]
        
        # Estadísticas de la última semana
        last_week = [h for h in self.health_history 
                    if datetime.fromisoformat(h.timestamp) > datetime.now() - timedelta(days=7)]
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'current_status': {
                'service_available': current_health.service_available,
                'response_time_ms': current_health.response_time_ms,
                'last_analysis': current_health.last_analysis_time,
                'success_rate': current_health.analysis_success_rate
            },
            'metrics_24h': {
                'total_checks': len(last_24h),
                'successful_checks': sum(1 for h in last_24h if h.service_available),
                'avg_response_time': sum(h.response_time_ms or 0 for h in last_24h) / len(last_24h) if last_24h else 0,
                'uptime_percentage': (sum(1 for h in last_24h if h.service_available) / len(last_24h) * 100) if last_24h else 0
            },
            'metrics_7d': {
                'total_checks': len(last_week),
                'successful_checks': sum(1 for h in last_week if h.service_available),
                'avg_response_time': sum(h.response_time_ms or 0 for h in last_week) / len(last_week) if last_week else 0,
                'uptime_percentage': (sum(1 for h in last_week if h.service_available) / len(last_week) * 100) if last_week else 0
            },
            'recent_alerts': self.alert_history[-10:],  # Últimas 10 alertas
            'recommendations': self.get_recommendations(current_health)
        }
        
        return report
    
    def get_recommendations(self, health: HealthStatus) -> List[str]:
        """Genera recomendaciones basadas en el estado actual"""
        recommendations = []
        
        if not health.service_available:
            recommendations.append("Verificar configuración de Google AI Studio API Key")
            recommendations.append("Comprobar conectividad de red")
            recommendations.append("Revisar logs de la aplicación para errores específicos")
        
        if health.response_time_ms and health.response_time_ms > 3000:
            recommendations.append("Considerar optimizar el tamaño de archivos CSV")
            recommendations.append("Revisar carga del servidor")
            recommendations.append("Verificar latencia de red con Google AI Studio")
        
        if health.analysis_success_rate < 90:
            recommendations.append("Revisar formato de datos CSV")
            recommendations.append("Verificar límites de cuota de Google AI Studio")
            recommendations.append("Considerar implementar retry logic")
        
        if not recommendations:
            recommendations.append("Sistema funcionando correctamente")
        
        return recommendations
    
    def cleanup_old_data(self):
        """Limpia datos antiguos según configuración de retención"""
        cutoff_date = datetime.now() - timedelta(days=self.config['retention_days'])
        
        # Limpiar historial de salud
        self.health_history = [
            h for h in self.health_history 
            if datetime.fromisoformat(h.timestamp) > cutoff_date
        ]
        
        # Limpiar historial de alertas
        self.alert_history = [
            a for a in self.alert_history 
            if datetime.fromisoformat(a['timestamp']) > cutoff_date
        ]
        
        self.logger.info(f"Limpieza completada. Datos anteriores a {cutoff_date} eliminados")
    
    def run_continuous_monitoring(self):
        """Ejecuta monitoreo continuo"""
        self.logger.info("Iniciando monitoreo continuo del servicio IA")
        
        try:
            while True:
                # Realizar check de salud
                health = self.check_ai_health()
                self.health_history.append(health)
                self.update_metrics(health)
                
                # Log del estado
                status = "✅ OK" if health.service_available else "❌ FAIL"
                self.logger.info(
                    f"Health Check [{status}] - "
                    f"Response: {health.response_time_ms:.0f}ms - "
                    f"API Valid: {health.api_key_valid}"
                )
                
                # Verificar si debe enviar alerta
                if self.should_alert(health):
                    if not health.service_available:
                        self.send_alert(health, 'service_down')
                    elif health.response_time_ms and health.response_time_ms > self.config['response_time_threshold']:
                        self.send_alert(health, 'slow_response')
                
                # Limpieza periódica (cada 24 horas)
                if len(self.health_history) % (24 * 60 // (self.config['check_interval'] // 60)) == 0:
                    self.cleanup_old_data()
                
                # Esperar hasta el próximo check
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            self.logger.info("Monitoreo detenido por el usuario")
        except Exception as e:
            self.logger.error(f"Error en monitoreo continuo: {e}")
            raise

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Monitor para servicios de IA - Dashboard IT')
    parser.add_argument('--config', help='Archivo de configuración JSON')
    parser.add_argument('--continuous', action='store_true', help='Ejecutar monitoreo continuo')
    parser.add_argument('--report', action='store_true', help='Generar reporte de estado')
    parser.add_argument('--check', action='store_true', help='Realizar un solo check de salud')
    
    args = parser.parse_args()
    
    monitor = AIMonitor(args.config)
    
    if args.continuous:
        monitor.run_continuous_monitoring()
    elif args.report:
        report = monitor.generate_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.check:
        health = monitor.check_ai_health()
        print(f"Estado del servicio: {'✅ Disponible' if health.service_available else '❌ No disponible'}")
        print(f"Tiempo de respuesta: {health.response_time_ms:.0f}ms")
        print(f"API Key válida: {'✅ Sí' if health.api_key_valid else '❌ No'}")
        if health.error_message:
            print(f"Error: {health.error_message}")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()