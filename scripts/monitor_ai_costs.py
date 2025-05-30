#!/usr/bin/env python3
"""
Monitor de costos para Google AI Studio
Dashboard IT - Clínica Bonsana
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

@dataclass
class CostData:
    """Datos de costos de IA"""
    date: str
    requests_count: int
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    model_used: str

@dataclass
class UsageAlert:
    """Alerta de uso"""
    alert_type: str
    threshold: float
    current_value: float
    message: str
    severity: str  # 'info', 'warning', 'critical'

class GoogleAICostMonitor:
    """Monitor de costos para Google AI Studio"""
    
    def __init__(self, config_file=None):
        self.project_root = Path(__file__).parent.parent
        self.config = self.load_config(config_file)
        self.cost_history_file = self.project_root / 'ai_cost_history.json'
        self.usage_log_file = self.project_root / 'logs' / 'ai_usage.log'
        
        # Precios aproximados (verificar precios actuales en Google AI)
        self.pricing = {
            'gemini-1.5-pro': {
                'input_tokens_per_1k': 0.00125,   # $0.00125 por 1K tokens
                'output_tokens_per_1k': 0.005     # $0.005 por 1K tokens
            },
            'gemini-1.0-pro': {
                'input_tokens_per_1k': 0.0005,    # $0.0005 por 1K tokens
                'output_tokens_per_1k': 0.0015    # $0.0015 por 1K tokens
            }
        }
    
    def load_config(self, config_file):
        """Carga configuración del monitor"""
        default_config = {
            'daily_budget': 5.00,           # $5 por día
            'monthly_budget': 100.00,       # $100 por mes
            'weekly_budget': 25.00,         # $25 por semana
            'request_limit_hourly': 10,     # 10 requests por hora
            'request_limit_daily': 50,      # 50 requests por día
            'token_limit_daily': 1000000,   # 1M tokens por día
            'alert_thresholds': {
                'daily_budget': 0.8,        # 80% del presupuesto diario
                'monthly_budget': 0.9,      # 90% del presupuesto mensual
                'request_limit': 0.8        # 80% del límite de requests
            },
            'email_alerts': False,
            'slack_webhook': None,
            'cost_center': 'IT-Dashboard'
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"Error cargando configuración: {e}")
        
        return default_config
    
    def estimate_tokens_from_text(self, text: str) -> int:
        """Estima tokens basado en texto (aproximado)"""
        # Estimación rough: ~4 caracteres por token para inglés/español
        return len(text) // 4
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calcula costo basado en tokens"""
        if model not in self.pricing:
            model = 'gemini-1.5-pro'  # Default
        
        prices = self.pricing[model]
        
        input_cost = (input_tokens / 1000) * prices['input_tokens_per_1k']
        output_cost = (output_tokens / 1000) * prices['output_tokens_per_1k']
        
        return input_cost + output_cost
    
    def log_usage(self, request_data: Dict):
        """Registra uso de IA"""
        try:
            # Crear directorio de logs si no existe
            self.usage_log_file.parent.mkdir(exist_ok=True)
            
            # Preparar entrada de log
            log_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'model': request_data.get('model', 'unknown'),
                'input_tokens': request_data.get('input_tokens', 0),
                'output_tokens': request_data.get('output_tokens', 0),
                'estimated_cost': request_data.get('estimated_cost', 0),
                'success': request_data.get('success', False),
                'csv_rows': request_data.get('csv_rows', 0)
            }
            
            # Escribir a archivo de log
            with open(self.usage_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            # Actualizar historial de costos
            self.update_cost_history(log_entry)
            
        except Exception as e:
            print(f"Error registrando uso: {e}")
    
    def update_cost_history(self, log_entry: Dict):
        """Actualiza historial de costos"""
        try:
            # Cargar historial existente
            if self.cost_history_file.exists():
                with open(self.cost_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = {'daily': {}, 'monthly': {}, 'total_cost': 0.0}
            
            # Obtener fecha actual
            today = datetime.now().strftime('%Y-%m-%d')
            month = datetime.now().strftime('%Y-%m')
            
            # Actualizar datos diarios
            if today not in history['daily']:
                history['daily'][today] = {
                    'requests': 0,
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'cost': 0.0
                }
            
            history['daily'][today]['requests'] += 1
            history['daily'][today]['input_tokens'] += log_entry['input_tokens']
            history['daily'][today]['output_tokens'] += log_entry['output_tokens']
            history['daily'][today]['cost'] += log_entry['estimated_cost']
            
            # Actualizar datos mensuales
            if month not in history['monthly']:
                history['monthly'][month] = {
                    'requests': 0,
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'cost': 0.0
                }
            
            history['monthly'][month]['requests'] += 1
            history['monthly'][month]['input_tokens'] += log_entry['input_tokens']
            history['monthly'][month]['output_tokens'] += log_entry['output_tokens']
            history['monthly'][month]['cost'] += log_entry['estimated_cost']
            
            # Actualizar costo total
            history['total_cost'] += log_entry['estimated_cost']
            
            # Guardar historial actualizado
            with open(self.cost_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            print(f"Error actualizando historial: {e}")
    
    def get_usage_stats(self, period='today') -> Dict:
        """Obtiene estadísticas de uso"""
        try:
            if not self.cost_history_file.exists():
                return {'cost': 0.0, 'requests': 0, 'tokens': 0}
            
            with open(self.cost_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            if period == 'today':
                today = datetime.now().strftime('%Y-%m-%d')
                data = history['daily'].get(today, {})
            elif period == 'month':
                month = datetime.now().strftime('%Y-%m')
                data = history['monthly'].get(month, {})
            elif period == 'week':
                # Sumar últimos 7 días
                data = {'cost': 0.0, 'requests': 0, 'input_tokens': 0, 'output_tokens': 0}
                for i in range(7):
                    date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                    day_data = history['daily'].get(date, {})
                    data['cost'] += day_data.get('cost', 0)
                    data['requests'] += day_data.get('requests', 0)
                    data['input_tokens'] += day_data.get('input_tokens', 0)
                    data['output_tokens'] += day_data.get('output_tokens', 0)
            else:
                data = {'cost': history.get('total_cost', 0.0), 'requests': 0, 'tokens': 0}
            
            return {
                'cost': data.get('cost', 0.0),
                'requests': data.get('requests', 0),
                'input_tokens': data.get('input_tokens', 0),
                'output_tokens': data.get('output_tokens', 0),
                'total_tokens': data.get('input_tokens', 0) + data.get('output_tokens', 0)
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {'cost': 0.0, 'requests': 0, 'tokens': 0}
    
    def check_budget_alerts(self) -> List[UsageAlert]:
        """Verifica si se han excedido presupuestos"""
        alerts = []
        
        # Verificar presupuesto diario
        today_stats = self.get_usage_stats('today')
        daily_threshold = self.config['daily_budget'] * self.config['alert_thresholds']['daily_budget']
        
        if today_stats['cost'] >= daily_threshold:
            severity = 'critical' if today_stats['cost'] >= self.config['daily_budget'] else 'warning'
            alerts.append(UsageAlert(
                alert_type='daily_budget',
                threshold=daily_threshold,
                current_value=today_stats['cost'],
                message=f"Costo diario: ${today_stats['cost']:.3f} / ${self.config['daily_budget']:.2f}",
                severity=severity
            ))
        
        # Verificar presupuesto mensual
        month_stats = self.get_usage_stats('month')
        monthly_threshold = self.config['monthly_budget'] * self.config['alert_thresholds']['monthly_budget']
        
        if month_stats['cost'] >= monthly_threshold:
            severity = 'critical' if month_stats['cost'] >= self.config['monthly_budget'] else 'warning'
            alerts.append(UsageAlert(
                alert_type='monthly_budget',
                threshold=monthly_threshold,
                current_value=month_stats['cost'],
                message=f"Costo mensual: ${month_stats['cost']:.2f} / ${self.config['monthly_budget']:.2f}",
                severity=severity
            ))
        
        # Verificar límites de requests
        request_threshold = self.config['request_limit_daily'] * self.config['alert_thresholds']['request_limit']
        
        if today_stats['requests'] >= request_threshold:
            severity = 'critical' if today_stats['requests'] >= self.config['request_limit_daily'] else 'warning'
            alerts.append(UsageAlert(
                alert_type='request_limit',
                threshold=request_threshold,
                current_value=today_stats['requests'],
                message=f"Requests diarios: {today_stats['requests']} / {self.config['request_limit_daily']}",
                severity=severity
            ))
        
        return alerts
    
    def send_alert_email(self, alerts: List[UsageAlert]):
        """Envía alertas por email"""
        if not self.config.get('email_alerts') or not alerts:
            return
        
        try:
            # Crear mensaje HTML
            html_content = self.create_alert_email_html(alerts)
            
            msg = MimeMultipart('alternative')
            msg['Subject'] = f"⚠️ Alerta de Costos IA - Dashboard IT"
            msg['From'] = self.config.get('email_from', 'dashboard@clinicabonsana.com')
            msg['To'] = ', '.join(self.config.get('email_to', []))
            
            # Agregar contenido HTML
            html_part = MimeText(html_content, 'html')
            msg.attach(html_part)
            
            # Enviar email
            with smtplib.SMTP(self.config.get('smtp_server', 'localhost'), 
                             self.config.get('smtp_port', 587)) as server:
                if self.config.get('smtp_tls', True):
                    server.starttls()
                
                if self.config.get('smtp_user'):
                    server.login(self.config['smtp_user'], self.config['smtp_password'])
                
                server.send_message(msg)
            
            print("✅ Alerta enviada por email")
            
        except Exception as e:
            print(f"❌ Error enviando email: {e}")
    
    def create_alert_email_html(self, alerts: List[UsageAlert]) -> str:
        """Crea contenido HTML para email de alerta"""
        today_stats = self.get_usage_stats('today')
        month_stats = self.get_usage_stats('month')
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #dc3545;">
                <h2 style="color: #dc3545; margin-top: 0;">⚠️ Alerta de Costos IA</h2>
                <p><strong>Dashboard IT - Clínica Bonsana</strong></p>
                <p>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h3>🚨 Alertas Activas:</h3>
                <ul>
        """
        
        for alert in alerts:
            color = {'warning': '#ffc107', 'critical': '#dc3545', 'info': '#17a2b8'}[alert.severity]
            html += f"""
                    <li style="color: {color}; font-weight: bold;">
                        {alert.message}
                    </li>
            """
        
        html += f"""
                </ul>
                
                <h3>📊 Uso Actual:</h3>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <th style="border: 1px solid #ddd; padding: 8px; background: #f2f2f2;">Período</th>
                        <th style="border: 1px solid #ddd; padding: 8px; background: #f2f2f2;">Costo</th>
                        <th style="border: 1px solid #ddd; padding: 8px; background: #f2f2f2;">Requests</th>
                        <th style="border: 1px solid #ddd; padding: 8px; background: #f2f2f2;">Tokens</th>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">Hoy</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">${today_stats['cost']:.3f}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{today_stats['requests']}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{today_stats['total_tokens']:,}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">Este mes</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">${month_stats['cost']:.2f}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{month_stats['requests']}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{month_stats['total_tokens']:,}</td>
                    </tr>
                </table>
                
                <h3>🎯 Presupuestos Configurados:</h3>
                <ul>
                    <li>Diario: ${self.config['daily_budget']:.2f}</li>
                    <li>Mensual: ${self.config['monthly_budget']:.2f}</li>
                    <li>Requests diarios: {self.config['request_limit_daily']}</li>
                </ul>
                
                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #dee2e6;">
                    <p style="color: #6c757d; font-size: 0.9em;">
                        Este es un mensaje automático del sistema de monitoreo de costos IA.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_slack_alert(self, alerts: List[UsageAlert]):
        """Envía alerta a Slack"""
        webhook_url = self.config.get('slack_webhook')
        if not webhook_url or not alerts:
            return
        
        try:
            today_stats = self.get_usage_stats('today')
            
            # Crear mensaje para Slack
            text = "⚠️ *Alerta de Costos IA - Dashboard IT*\n\n"
            
            for alert in alerts:
                emoji = {'warning': '⚠️', 'critical': '🚨', 'info': 'ℹ️'}[alert.severity]
                text += f"{emoji} {alert.message}\n"
            
            text += f"\n📊 *Uso hoy:* ${today_stats['cost']:.3f} | {today_stats['requests']} requests"
            
            payload = {
                'text': text,
                'username': 'Dashboard IT Bot',
                'icon_emoji': ':robot_face:'
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print("✅ Alerta enviada a Slack")
            else:
                print(f"❌ Error enviando a Slack: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error enviando a Slack: {e}")
    
    def generate_cost_report(self, period='month') -> Dict:
        """Genera reporte de costos"""
        stats = self.get_usage_stats(period)
        
        # Calcular proyecciones
        if period == 'today':
            # Proyección mensual basada en uso diario
            monthly_projection = stats['cost'] * 30
            budget_utilization = (stats['cost'] / self.config['daily_budget']) * 100
        elif period == 'month':
            monthly_projection = stats['cost']
            budget_utilization = (stats['cost'] / self.config['monthly_budget']) * 100
        else:
            monthly_projection = 0
            budget_utilization = 0
        
        # Calcular eficiencia
        cost_per_request = stats['cost'] / stats['requests'] if stats['requests'] > 0 else 0
        cost_per_token = stats['cost'] / stats['total_tokens'] if stats['total_tokens'] > 0 else 0
        
        return {
            'period': period,
            'stats': stats,
            'projections': {
                'monthly_cost': monthly_projection,
                'budget_utilization_pct': budget_utilization
            },
            'efficiency': {
                'cost_per_request': cost_per_request,
                'cost_per_token': cost_per_token * 1000,  # Costo por 1K tokens
                'avg_tokens_per_request': stats['total_tokens'] / stats['requests'] if stats['requests'] > 0 else 0
            },
            'alerts': self.check_budget_alerts()
        }
    
    def run_monitoring_check(self):
        """Ejecuta verificación completa de monitoreo"""
        print("💰 MONITOR DE COSTOS IA")
        print("=" * 50)
        
        # Verificar alertas
        alerts = self.check_budget_alerts()
        
        if alerts:
            print(f"🚨 {len(alerts)} alertas encontradas:")
            for alert in alerts:
                emoji = {'warning': '⚠️', 'critical': '🚨', 'info': 'ℹ️'}[alert.severity]
                print(f"   {emoji} {alert.message}")
            
            # Enviar notificaciones
            self.send_alert_email(alerts)
            self.send_slack_alert(alerts)
        else:
            print("✅ No hay alertas de presupuesto")
        
        # Mostrar estadísticas
        today_stats = self.get_usage_stats('today')
        month_stats = self.get_usage_stats('month')
        
        print(f"\n📊 USO HOY:")
        print(f"   Costo: ${today_stats['cost']:.3f} / ${self.config['daily_budget']:.2f}")
        print(f"   Requests: {today_stats['requests']} / {self.config['request_limit_daily']}")
        print(f"   Tokens: {today_stats['total_tokens']:,}")
        
        print(f"\n📊 USO ESTE MES:")
        print(f"   Costo: ${month_stats['cost']:.2f} / ${self.config['monthly_budget']:.2f}")
        print(f"   Requests: {month_stats['requests']}")
        print(f"   Tokens: {month_stats['total_tokens']:,}")
        
        # Proyecciones
        if today_stats['cost'] > 0:
            monthly_projection = today_stats['cost'] * 30
            print(f"\n📈 PROYECCIÓN MENSUAL: ${monthly_projection:.2f}")
            
            if monthly_projection > self.config['monthly_budget']:
                print(f"   ⚠️ Proyección excede presupuesto mensual")
        
        return len(alerts) == 0  # Retorna True si no hay alertas

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Monitor de costos para Google AI Studio')
    parser.add_argument('--config', help='Archivo de configuración JSON')
    parser.add_argument('--threshold', type=float, help='Umbral de alerta de costo diario')
    parser.add_argument('--report', choices=['today', 'week', 'month'], help='Generar reporte')
    parser.add_argument('--log-usage', help='Registrar uso desde JSON')
    
    args = parser.parse_args()
    
    monitor = GoogleAICostMonitor(args.config)
    
    # Aplicar umbral desde línea de comandos
    if args.threshold:
        monitor.config['daily_budget'] = args.threshold
    
    if args.log_usage:
        # Registrar uso desde archivo JSON
        try:
            with open(args.log_usage, 'r') as f:
                usage_data = json.load(f)
            monitor.log_usage(usage_data)
            print("✅ Uso registrado")
        except Exception as e:
            print(f"❌ Error registrando uso: {e}")
            sys.exit(1)
    
    elif args.report:
        # Generar reporte
        report = monitor.generate_cost_report(args.report)
        print(json.dumps(report, indent=2, default=str))
    
    else:
        # Ejecutar verificación de monitoreo
        success = monitor.run_monitoring_check()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()