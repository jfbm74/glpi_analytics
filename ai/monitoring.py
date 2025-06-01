"""
Sistema de monitoreo y métricas para el módulo de IA
"""

import os
import json
import time
import logging
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import threading

logger = logging.getLogger(__name__)

@dataclass
class AnalysisMetrics:
    """Métricas de un análisis individual"""
    analysis_id: str
    analysis_type: str
    start_time: float
    end_time: float
    processing_time: float
    success: bool
    model_used: str
    prompt_tokens: int
    response_tokens: int
    total_tokens: int
    cost_estimate: float
    error_message: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        """Duración en segundos"""
        return self.end_time - self.start_time
    
    @property
    def tokens_per_second(self) -> float:
        """Tokens por segundo"""
        return self.total_tokens / self.processing_time if self.processing_time > 0 else 0

@dataclass
class SystemMetrics:
    """Métricas del sistema"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    active_analyses: int
    cache_size_mb: float
    log_size_mb: float

class AIMonitor:
    """Monitor del sistema de IA"""
    
    def __init__(self, metrics_dir: str = "data/metrics"):
        """
        Inicializa el monitor
        
        Args:
            metrics_dir: Directorio para almacenar métricas
        """
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Almacenamiento en memoria de métricas recientes
        self.analysis_history = deque(maxlen=1000)  # Últimos 1000 análisis
        self.system_metrics = deque(maxlen=2880)    # 24 horas de métricas (cada 30 seg)
        self.error_counts = defaultdict(int)
        
        # Estado actual
        self.active_analyses = {}
        self.daily_stats = {}
        
        # Thread para monitoreo de sistema
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Configuración de costos (estimados por modelo)
        self.cost_per_token = {
            'gemini-2.0-flash-exp': 0.00001,  # $0.01 per 1K tokens (estimado)
            'gemini-1.5-pro': 0.000015,
            'gemini-1.5-flash': 0.000005
        }
        
        self.load_historical_metrics()
    
    def start_monitoring(self, interval: int = 30):
        """
        Inicia monitoreo automático del sistema
        
        Args:
            interval: Intervalo en segundos entre mediciones
        """
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info("Sistema de monitoreo iniciado")
    
    def stop_monitoring(self):
        """Detiene el monitoreo automático"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Sistema de monitoreo detenido")
    
    def start_analysis(self, analysis_id: str, analysis_type: str, model: str) -> float:
        """
        Registra inicio de análisis
        
        Args:
            analysis_id: ID único del análisis
            analysis_type: Tipo de análisis
            model: Modelo utilizado
            
        Returns:
            Timestamp de inicio
        """
        start_time = time.time()
        
        self.active_analyses[analysis_id] = {
            'analysis_type': analysis_type,
            'model': model,
            'start_time': start_time
        }
        
        logger.debug(f"Análisis iniciado: {analysis_id} ({analysis_type})")
        return start_time
    
    def end_analysis(self, analysis_id: str, success: bool, prompt_tokens: int = 0, 
                    response_tokens: int = 0, error_message: str = None):
        """
        Registra finalización de análisis
        
        Args:
            analysis_id: ID del análisis
            success: Si fue exitoso
            prompt_tokens: Tokens del prompt
            response_tokens: Tokens de respuesta
            error_message: Mensaje de error si aplica
        """
        end_time = time.time()
        
        if analysis_id not in self.active_analyses:
            logger.warning(f"Análisis no encontrado: {analysis_id}")
            return
        
        analysis_info = self.active_analyses.pop(analysis_id)
        start_time = analysis_info['start_time']
        processing_time = end_time - start_time
        total_tokens = prompt_tokens + response_tokens
        
        # Calcular costo estimado
        model = analysis_info['model']
        cost_estimate = total_tokens * self.cost_per_token.get(model, 0.00001)
        
        # Crear métricas del análisis
        metrics = AnalysisMetrics(
            analysis_id=analysis_id,
            analysis_type=analysis_info['analysis_type'],
            start_time=start_time,
            end_time=end_time,
            processing_time=processing_time,
            success=success,
            model_used=model,
            prompt_tokens=prompt_tokens,
            response_tokens=response_tokens,
            total_tokens=total_tokens,
            cost_estimate=cost_estimate,
            error_message=error_message
        )
        
        # Agregar a historial
        self.analysis_history.append(metrics)
        
        # Actualizar estadísticas diarias
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.daily_stats:
            self.daily_stats[today] = {
                'total_analyses': 0,
                'successful_analyses': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'avg_processing_time': 0.0,
                'analysis_types': defaultdict(int)
            }
        
        stats = self.daily_stats[today]
        stats['total_analyses'] += 1
        if success:
            stats['successful_analyses'] += 1
        stats['total_tokens'] += total_tokens
        stats['total_cost'] += cost_estimate
        stats['analysis_types'][analysis_info['analysis_type']] += 1
        
        # Calcular tiempo promedio
        total_time = sum(m.processing_time for m in self.analysis_history 
                        if datetime.fromtimestamp(m.start_time).strftime('%Y-%m-%d') == today)
        total_count = len([m for m in self.analysis_history 
                          if datetime.fromtimestamp(m.start_time).strftime('%Y-%m-%d') == today])
        stats['avg_processing_time'] = total_time / total_count if total_count > 0 else 0
        
        # Registrar errores
        if not success and error_message:
            self.error_counts[error_message] += 1
        
        logger.info(f"Análisis completado: {analysis_id} ({processing_time:.2f}s, "
                   f"{total_tokens} tokens, ${cost_estimate:.4f})")
    
    def record_system_metrics(self):
        """Registra métricas del sistema actual"""
        try:
            # Métricas de CPU y memoria
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(os.getcwd())
            
            # Tamaño de cache
            cache_size = self._get_directory_size("data/cache") if os.path.exists("data/cache") else 0
            
            # Tamaño de logs
            log_size = self._get_directory_size("logs") if os.path.exists("logs") else 0
            
            metrics = SystemMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                disk_usage_percent=disk.percent,
                active_analyses=len(self.active_analyses),
                cache_size_mb=cache_size / 1024 / 1024,
                log_size_mb=log_size / 1024 / 1024
            )
            
            self.system_metrics.append(metrics)
            
        except Exception as e:
            logger.error(f"Error registrando métricas del sistema: {e}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """
        Obtiene estado actual del sistema
        
        Returns:
            Estado actual con métricas
        """
        now = time.time()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Métricas de las últimas 24 horas
        last_24h = [m for m in self.analysis_history 
                   if now - m.start_time <= 86400]
        
        # Estadísticas de hoy
        today_stats = self.daily_stats.get(today, {})
        
        # Análisis activos
        active_analyses_info = []
        for aid, info in self.active_analyses.items():
            duration = now - info['start_time']
            active_analyses_info.append({
                'id': aid,
                'type': info['analysis_type'],
                'model': info['model'],
                'duration_seconds': duration
            })
        
        # Últimas métricas del sistema
        latest_system_metrics = self.system_metrics[-1] if self.system_metrics else None
        
        return {
            'status': 'healthy' if len(self.active_analyses) < 5 else 'busy',
            'timestamp': datetime.now().isoformat(),
            'active_analyses': {
                'count': len(self.active_analyses),
                'details': active_analyses_info
            },
            'today_stats': {
                'total_analyses': today_stats.get('total_analyses', 0),
                'successful_analyses': today_stats.get('successful_analyses', 0),
                'success_rate': (today_stats.get('successful_analyses', 0) / 
                               max(today_stats.get('total_analyses', 1), 1)) * 100,
                'total_tokens': today_stats.get('total_tokens', 0),
                'total_cost': today_stats.get('total_cost', 0.0),
                'avg_processing_time': today_stats.get('avg_processing_time', 0.0)
            },
            'last_24h_stats': {
                'total_analyses': len(last_24h),
                'successful_analyses': len([m for m in last_24h if m.success]),
                'avg_processing_time': sum(m.processing_time for m in last_24h) / len(last_24h) if last_24h else 0,
                'total_tokens': sum(m.total_tokens for m in last_24h),
                'total_cost': sum(m.cost_estimate for m in last_24h)
            },
            'system_metrics': asdict(latest_system_metrics) if latest_system_metrics else None,
            'top_errors': dict(list(self.error_counts.items())[:5]),
            'model_usage': self._get_model_usage_stats()
        }
    
    def get_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """
        Obtiene tendencias de rendimiento
        
        Args:
            days: Número de días para el análisis
            
        Returns:
            Tendencias de rendimiento
        """
        cutoff_time = time.time() - (days * 86400)
        recent_analyses = [m for m in self.analysis_history if m.start_time >= cutoff_time]
        
        # Agrupar por día
        daily_metrics = defaultdict(lambda: {
            'count': 0,
            'success_count': 0,
            'total_time': 0.0,
            'total_tokens': 0,
            'total_cost': 0.0
        })
        
        for metrics in recent_analyses:
            day = datetime.fromtimestamp(metrics.start_time).strftime('%Y-%m-%d')
            daily = daily_metrics[day]
            daily['count'] += 1
            if metrics.success:
                daily['success_count'] += 1
            daily['total_time'] += metrics.processing_time
            daily['total_tokens'] += metrics.total_tokens
            daily['total_cost'] += metrics.cost_estimate
        
        # Calcular tendencias
        trend_data = {}
        for day, metrics in daily_metrics.items():
            trend_data[day] = {
                'total_analyses': metrics['count'],
                'success_rate': (metrics['success_count'] / metrics['count'] * 100) if metrics['count'] > 0 else 0,
                'avg_processing_time': metrics['total_time'] / metrics['count'] if metrics['count'] > 0 else 0,
                'total_tokens': metrics['total_tokens'],
                'total_cost': metrics['total_cost'],
                'tokens_per_analysis': metrics['total_tokens'] / metrics['count'] if metrics['count'] > 0 else 0
            }
        
        return {
            'period_days': days,
            'daily_trends': trend_data,
            'summary': {
                'total_analyses': len(recent_analyses),
                'overall_success_rate': (len([m for m in recent_analyses if m.success]) / 
                                       len(recent_analyses) * 100) if recent_analyses else 0,
                'avg_daily_analyses': len(recent_analyses) / days,
                'total_cost': sum(m.cost_estimate for m in recent_analyses),
                'avg_cost_per_analysis': (sum(m.cost_estimate for m in recent_analyses) / 
                                        len(recent_analyses)) if recent_analyses else 0
            }
        }
    
    def get_health_check(self) -> Dict[str, Any]:
        """
        Realiza chequeo de salud del sistema
        
        Returns:
            Estado de salud del sistema
        """
        issues = []
        warnings = []
        
        # Verificar análisis activos
        now = time.time()
        stuck_analyses = []
        for aid, info in self.active_analyses.items():
            duration = now - info['start_time']
            if duration > 300:  # 5 minutos
                stuck_analyses.append(aid)
        
        if stuck_analyses:
            issues.append(f"Análisis posiblemente atascados: {len(stuck_analyses)}")
        
        # Verificar tasa de errores reciente
        recent_analyses = [m for m in self.analysis_history 
                          if now - m.start_time <= 3600]  # Última hora
        if recent_analyses:
            error_rate = len([m for m in recent_analyses if not m.success]) / len(recent_analyses)
            if error_rate > 0.5:
                issues.append(f"Alta tasa de errores: {error_rate:.1%}")
            elif error_rate > 0.2:
                warnings.append(f"Tasa de errores elevada: {error_rate:.1%}")
        
        # Verificar métricas del sistema
        if self.system_metrics:
            latest = self.system_metrics[-1]
            if latest.memory_percent > 90:
                issues.append(f"Uso de memoria alto: {latest.memory_percent:.1f}%")
            elif latest.memory_percent > 80:
                warnings.append(f"Uso de memoria elevado: {latest.memory_percent:.1f}%")
            
            if latest.disk_usage_percent > 95:
                issues.append(f"Espacio en disco bajo: {100 - latest.disk_usage_percent:.1f}% libre")
            elif latest.disk_usage_percent > 85:
                warnings.append(f"Espacio en disco limitado: {100 - latest.disk_usage_percent:.1f}% libre")
            
            if latest.cache_size_mb > 1000:  # 1GB
                warnings.append(f"Cache grande: {latest.cache_size_mb:.1f} MB")
        
        # Determinar estado general
        if issues:
            health_status = "critical"
        elif warnings:
            health_status = "warning"
        else:
            health_status = "healthy"
        
        return {
            'status': health_status,
            'timestamp': datetime.now().isoformat(),
            'issues': issues,
            'warnings': warnings,
            'active_analyses_count': len(self.active_analyses),
            'stuck_analyses': stuck_analyses,
            'monitoring_active': self.monitoring_active
        }
    
    def save_metrics(self):
        """Guarda métricas a archivo"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Guardar métricas de análisis
            analysis_file = self.metrics_dir / f"analysis_metrics_{timestamp}.json"
            analysis_data = {
                'timestamp': datetime.now().isoformat(),
                'analysis_history': [asdict(m) for m in self.analysis_history],
                'daily_stats': self.daily_stats,
                'error_counts': dict(self.error_counts)
            }
            
            with open(analysis_file, 'w') as f:
                json.dump(analysis_data, f, indent=2, default=str)
            
            # Guardar métricas del sistema
            system_file = self.metrics_dir / f"system_metrics_{timestamp}.json"
            system_data = {
                'timestamp': datetime.now().isoformat(),
                'system_metrics': [asdict(m) for m in self.system_metrics]
            }
            
            with open(system_file, 'w') as f:
                json.dump(system_data, f, indent=2, default=str)
            
            logger.info(f"Métricas guardadas: {analysis_file}, {system_file}")
            
        except Exception as e:
            logger.error(f"Error guardando métricas: {e}")
    
    def load_historical_metrics(self):
        """Carga métricas históricas"""
        try:
            # Buscar archivos de métricas más recientes
            analysis_files = sorted(self.metrics_dir.glob("analysis_metrics_*.json"))
            system_files = sorted(self.metrics_dir.glob("system_metrics_*.json"))
            
            # Cargar último archivo de análisis
            if analysis_files:
                with open(analysis_files[-1]) as f:
                    data = json.load(f)
                    
                # Restaurar historial de análisis (últimos 100)
                for analysis_data in data.get('analysis_history', [])[-100:]:
                    metrics = AnalysisMetrics(**analysis_data)
                    self.analysis_history.append(metrics)
                
                # Restaurar estadísticas diarias
                self.daily_stats.update(data.get('daily_stats', {}))
                
                # Restaurar conteos de errores
                self.error_counts.update(data.get('error_counts', {}))
                
                logger.info(f"Cargado historial de {len(self.analysis_history)} análisis")
            
            # Cargar último archivo de sistema
            if system_files:
                with open(system_files[-1]) as f:
                    data = json.load(f)
                
                # Restaurar métricas del sistema (últimas 100)
                for system_data in data.get('system_metrics', [])[-100:]:
                    metrics = SystemMetrics(**system_data)
                    self.system_metrics.append(metrics)
                
                logger.info(f"Cargadas {len(self.system_metrics)} métricas del sistema")
                
        except Exception as e:
            logger.warning(f"No se pudieron cargar métricas históricas: {e}")
    
    def cleanup_old_metrics(self, days_to_keep: int = 30):
        """
        Limpia métricas antiguas
        
        Args:
            days_to_keep: Días de métricas a mantener
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            # Limpiar archivos de métricas antiguos
            for metrics_file in self.metrics_dir.glob("*_metrics_*.json"):
                try:
                    # Extraer fecha del nombre del archivo
                    date_str = metrics_file.stem.split('_')[-2]  # formato: YYYYMMDD
                    file_date = datetime.strptime(date_str, '%Y%m%d')
                    
                    if file_date < cutoff_date:
                        metrics_file.unlink()
                        logger.info(f"Archivo de métricas eliminado: {metrics_file}")
                        
                except (ValueError, IndexError):
                    continue
            
            # Limpiar estadísticas diarias en memoria
            dates_to_remove = []
            for date_str in self.daily_stats.keys():
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    if date < cutoff_date:
                        dates_to_remove.append(date_str)
                except ValueError:
                    continue
            
            for date_str in dates_to_remove:
                del self.daily_stats[date_str]
            
            logger.info(f"Limpieza completada: {len(dates_to_remove)} días eliminados")
            
        except Exception as e:
            logger.error(f"Error en limpieza de métricas: {e}")
    
    def _monitoring_loop(self, interval: int):
        """Loop principal de monitoreo"""
        while self.monitoring_active:
            try:
                self.record_system_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error en loop de monitoreo: {e}")
                time.sleep(interval)
    
    def _get_directory_size(self, path: str) -> int:
        """Obtiene tamaño de directorio en bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception:
            pass
        return total_size
    
    def _get_model_usage_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas de uso por modelo"""
        model_counts = defaultdict(int)
        for metrics in self.analysis_history:
            model_counts[metrics.model_used] += 1
        return dict(model_counts)

# Instancia global del monitor
monitor = AIMonitor()