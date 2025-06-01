#!/usr/bin/env python3
"""
Script de mantenimiento para el Dashboard IT con módulo de IA
Clínica Bonsana
"""

import os
import sys
import json
import shutil
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import subprocess

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/maintenance.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MaintenanceManager:
    """Gestor de mantenimiento del sistema"""
    
    def __init__(self):
        """Inicializa el gestor de mantenimiento"""
        self.base_dir = Path(os.getcwd())
        self.data_dir = self.base_dir / "data"
        self.logs_dir = self.base_dir / "logs"
        self.cache_dir = self.data_dir / "cache"
        self.reports_dir = self.data_dir / "reports"
        self.metrics_dir = self.data_dir / "metrics"
        
        # Configuración de limpieza
        self.cleanup_config = {
            'cache_max_age_days': 7,
            'reports_max_age_days': 30,
            'metrics_max_age_days': 90,
            'logs_max_age_days': 30,
            'temp_files_max_age_hours': 24,
            'max_cache_size_mb': 500,
            'max_logs_size_mb': 100
        }
    
    def run_full_maintenance(self) -> Dict[str, bool]:
        """
        Ejecuta mantenimiento completo del sistema
        
        Returns:
            Diccionario con resultados de cada tarea
        """
        logger.info("="*60)
        logger.info("INICIANDO MANTENIMIENTO COMPLETO DEL SISTEMA")
        logger.info("="*60)
        
        tasks = [
            ("Verificar estructura de directorios", self.verify_directory_structure),
            ("Limpiar archivos temporales", self.cleanup_temp_files),
            ("Limpiar cache antiguo", self.cleanup_old_cache),
            ("Rotar logs", self.rotate_logs),
            ("Limpiar reportes antiguos", self.cleanup_old_reports),
            ("Limpiar métricas antiguas", self.cleanup_old_metrics),
            ("Optimizar base de datos", self.optimize_databases),
            ("Verificar integridad de datos", self.verify_data_integrity),
            ("Actualizar índices", self.update_indexes),
            ("Crear backup de configuración", self.backup_configuration),
            ("Verificar espacio en disco", self.check_disk_space),
            ("Verificar dependencias", self.check_dependencies),
            ("Generar reporte de salud", self.generate_health_report)
        ]
        
        results = {}
        total_tasks = len(tasks)
        
        for i, (task_name, task_func) in enumerate(tasks, 1):
            logger.info(f"\n[{i}/{total_tasks}] {task_name}...")
            try:
                success = task_func()
                results[task_name] = success
                status = "✅ COMPLETADO" if success else "❌ FALLÓ"
                logger.info(f"    {status}")
            except Exception as e:
                logger.error(f"    ❌ ERROR: {str(e)}")
                results[task_name] = False
        
        # Resumen
        successful_tasks = sum(results.values())
        logger.info("\n" + "="*60)
        logger.info("RESUMEN DE MANTENIMIENTO")
        logger.info("="*60)
        logger.info(f"Tareas completadas exitosamente: {successful_tasks}/{total_tasks}")
        
        for task_name, success in results.items():
            status = "✅" if success else "❌"
            logger.info(f"  {status} {task_name}")
        
        if successful_tasks == total_tasks:
            logger.info("\n🎉 MANTENIMIENTO COMPLETADO EXITOSAMENTE")
        else:
            logger.warning(f"\n⚠️  MANTENIMIENTO PARCIAL ({successful_tasks}/{total_tasks} tareas)")
        
        return results
    
    def verify_directory_structure(self) -> bool:
        """Verifica y crea estructura de directorios necesaria"""
        try:
            required_dirs = [
                "data",
                "data/cache",
                "data/reports", 
                "data/metrics",
                "data/backups",
                "logs",
                "ai",
                "templates",
                "static"
            ]
            
            created_count = 0
            for dir_path in required_dirs:
                full_path = self.base_dir / dir_path
                if not full_path.exists():
                    full_path.mkdir(parents=True, exist_ok=True)
                    created_count += 1
                    logger.debug(f"    Directorio creado: {dir_path}")
            
            if created_count > 0:
                logger.info(f"    {created_count} directorios creados")
            else:
                logger.info("    Estructura de directorios verificada")
            
            return True
            
        except Exception as e:
            logger.error(f"    Error verificando directorios: {e}")
            return False
    
    def cleanup_temp_files(self) -> bool:
        """Limpia archivos temporales"""
        try:
            removed_count = 0
            removed_size = 0
            cutoff_time = datetime.now() - timedelta(hours=self.cleanup_config['temp_files_max_age_hours'])
            
            # Buscar archivos temporales en varios directorios
            temp_patterns = [
                "*.tmp",
                "*.temp",
                "*~",
                "*.bak",
                ".DS_Store",
                "Thumbs.db"
            ]
            
            search_dirs = [self.data_dir, self.base_dir, tempfile.gettempdir()]
            
            for search_dir in search_dirs:
                if not os.path.exists(search_dir):
                    continue
                    
                for pattern in temp_patterns:
                    for temp_file in Path(search_dir).rglob(pattern):
                        try:
                            if temp_file.is_file():
                                stat_info = temp_file.stat()
                                if datetime.fromtimestamp(stat_info.st_mtime) < cutoff_time:
                                    file_size = stat_info.st_size
                                    temp_file.unlink()
                                    removed_count += 1
                                    removed_size += file_size
                                    logger.debug(f"    Removido: {temp_file}")
                        except Exception as e:
                            logger.debug(f"    No se pudo remover {temp_file}: {e}")
            
            logger.info(f"    {removed_count} archivos temporales removidos ({removed_size / 1024 / 1024:.1f} MB)")
            return True
            
        except Exception as e:
            logger.error(f"    Error limpiando temporales: {e}")
            return False
    
    def cleanup_old_cache(self) -> bool:
        """Limpia cache antiguo"""
        try:
            if not self.cache_dir.exists():
                logger.info("    No hay directorio de cache")
                return True
            
            removed_count = 0
            removed_size = 0
            cutoff_time = datetime.now() - timedelta(days=self.cleanup_config['cache_max_age_days'])
            
            for cache_file in self.cache_dir.rglob("*"):
                if cache_file.is_file():
                    try:
                        stat_info = cache_file.stat()
                        if datetime.fromtimestamp(stat_info.st_mtime) < cutoff_time:
                            file_size = stat_info.st_size
                            cache_file.unlink()
                            removed_count += 1
                            removed_size += file_size
                    except Exception as e:
                        logger.debug(f"    No se pudo remover cache {cache_file}: {e}")
            
            # Verificar tamaño total del cache
            total_cache_size = self._get_directory_size(self.cache_dir)
            max_cache_size = self.cleanup_config['max_cache_size_mb'] * 1024 * 1024
            
            if total_cache_size > max_cache_size:
                # Remover archivos más antiguos hasta llegar al límite
                cache_files = []
                for cache_file in self.cache_dir.rglob("*"):
                    if cache_file.is_file():
                        cache_files.append((cache_file.stat().st_mtime, cache_file))
                
                cache_files.sort()  # Más antiguos primero
                current_size = total_cache_size
                
                for mtime, cache_file in cache_files:
                    if current_size <= max_cache_size:
                        break
                    try:
                        file_size = cache_file.stat().st_size
                        cache_file.unlink()
                        current_size -= file_size
                        removed_count += 1
                        removed_size += file_size
                    except Exception:
                        pass
            
            logger.info(f"    {removed_count} archivos de cache removidos ({removed_size / 1024 / 1024:.1f} MB)")
            return True
            
        except Exception as e:
            logger.error(f"    Error limpiando cache: {e}")
            return False
    
    def rotate_logs(self) -> bool:
        """Rota y comprime logs antiguos"""
        try:
            if not self.logs_dir.exists():
                logger.info("    No hay directorio de logs")
                return True
            
            rotated_count = 0
            cutoff_time = datetime.now() - timedelta(days=self.cleanup_config['logs_max_age_days'])
            
            for log_file in self.logs_dir.glob("*.log"):
                try:
                    stat_info = log_file.stat()
                    
                    # Si el log es muy antiguo, comprimirlo
                    if datetime.fromtimestamp(stat_info.st_mtime) < cutoff_time:
                        compressed_name = f"{log_file.stem}_{datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y%m%d')}.log.gz"
                        compressed_path = self.logs_dir / compressed_name
                        
                        if not compressed_path.exists():
                            import gzip
                            with open(log_file, 'rb') as f_in:
                                with gzip.open(compressed_path, 'wb') as f_out:
                                    shutil.copyfileobj(f_in, f_out)
                            
                            log_file.unlink()
                            rotated_count += 1
                            logger.debug(f"    Log rotado: {log_file} -> {compressed_path}")
                    
                    # Si el log actual es muy grande, rotarlo
                    elif stat_info.st_size > 10 * 1024 * 1024:  # 10MB
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        rotated_name = f"{log_file.stem}_{timestamp}.log"
                        rotated_path = self.logs_dir / rotated_name
                        
                        shutil.move(log_file, rotated_path)
                        rotated_count += 1
                        logger.debug(f"    Log grande rotado: {log_file} -> {rotated_path}")
                        
                except Exception as e:
                    logger.debug(f"    Error rotando log {log_file}: {e}")
            
            logger.info(f"    {rotated_count} logs rotados")
            return True
            
        except Exception as e:
            logger.error(f"    Error rotando logs: {e}")
            return False
    
    def cleanup_old_reports(self) -> bool:
        """Limpia reportes antiguos"""
        try:
            if not self.reports_dir.exists():
                logger.info("    No hay directorio de reportes")
                return True
            
            removed_count = 0
            removed_size = 0
            cutoff_time = datetime.now() - timedelta(days=self.cleanup_config['reports_max_age_days'])
            
            for report_file in self.reports_dir.rglob("*"):
                if report_file.is_file():
                    try:
                        stat_info = report_file.stat()
                        if datetime.fromtimestamp(stat_info.st_mtime) < cutoff_time:
                            file_size = stat_info.st_size
                            report_file.unlink()
                            removed_count += 1
                            removed_size += file_size
                    except Exception as e:
                        logger.debug(f"    No se pudo remover reporte {report_file}: {e}")
            
            logger.info(f"    {removed_count} reportes antiguos removidos ({removed_size / 1024 / 1024:.1f} MB)")
            return True
            
        except Exception as e:
            logger.error(f"    Error limpiando reportes: {e}")
            return False
    
    def cleanup_old_metrics(self) -> bool:
        """Limpia métricas antiguas"""
        try:
            if not self.metrics_dir.exists():
                logger.info("    No hay directorio de métricas")
                return True
            
            removed_count = 0
            cutoff_time = datetime.now() - timedelta(days=self.cleanup_config['metrics_max_age_days'])
            
            for metrics_file in self.metrics_dir.glob("*_metrics_*.json"):
                try:
                    stat_info = metrics_file.stat()
                    if datetime.fromtimestamp(stat_info.st_mtime) < cutoff_time:
                        metrics_file.unlink()
                        removed_count += 1
                except Exception as e:
                    logger.debug(f"    No se pudo remover métrica {metrics_file}: {e}")
            
            logger.info(f"    {removed_count} archivos de métricas antiguos removidos")
            return True
            
        except Exception as e:
            logger.error(f"    Error limpiando métricas: {e}")
            return False
    
    def optimize_databases(self) -> bool:
        """Optimiza bases de datos del sistema"""
        try:
            # Por ahora, principalmente archivos JSON y CSV
            optimized_count = 0
            
            # Optimizar archivos CSV (remover filas duplicadas)
            for csv_file in self.data_dir.rglob("*.csv"):
                try:
                    import pandas as pd
                    df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8')
                    original_size = len(df)
                    df_clean = df.drop_duplicates()
                    
                    if len(df_clean) < original_size:
                        df_clean.to_csv(csv_file, sep=';', index=False, encoding='utf-8')
                        optimized_count += 1
                        logger.debug(f"    CSV optimizado: {csv_file} ({original_size} -> {len(df_clean)} filas)")
                        
                except Exception as e:
                    logger.debug(f"    Error optimizando CSV {csv_file}: {e}")
            
            # Compactar archivos JSON grandes
            for json_file in self.data_dir.rglob("*.json"):
                try:
                    if json_file.stat().st_size > 1024 * 1024:  # > 1MB
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        with open(json_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, separators=(',', ':'), ensure_ascii=False)
                        
                        optimized_count += 1
                        logger.debug(f"    JSON compactado: {json_file}")
                        
                except Exception as e:
                    logger.debug(f"    Error compactando JSON {json_file}: {e}")
            
            logger.info(f"    {optimized_count} archivos optimizados")
            return True
            
        except Exception as e:
            logger.error(f"    Error optimizando bases de datos: {e}")
            return False
    
    def verify_data_integrity(self) -> bool:
        """Verifica integridad de datos críticos"""
        try:
            issues_found = 0
            
            # Verificar CSV principal
            main_csv = self.data_dir / "glpi.csv"
            if main_csv.exists():
                try:
                    import pandas as pd
                    df = pd.read_csv(main_csv, delimiter=';', encoding='utf-8')
                    
                    required_columns = ['ID', 'Título', 'Tipo', 'Estado']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    
                    if missing_columns:
                        logger.warning(f"    Columnas faltantes en CSV principal: {missing_columns}")
                        issues_found += 1
                    
                    # Verificar duplicados en ID
                    if 'ID' in df.columns:
                        duplicates = df['ID'].duplicated().sum()
                        if duplicates > 0:
                            logger.warning(f"    {duplicates} IDs duplicados encontrados")
                            issues_found += 1
                    
                    logger.debug(f"    CSV principal verificado: {len(df)} registros")
                    
                except Exception as e:
                    logger.warning(f"    Error verificando CSV principal: {e}")
                    issues_found += 1
            
            # Verificar archivos de configuración
            config_files = ['.env', 'requirements.txt']
            for config_file in config_files:
                config_path = self.base_dir / config_file
                if not config_path.exists():
                    logger.warning(f"    Archivo de configuración faltante: {config_file}")
                    issues_found += 1
            
            # Verificar módulos de IA
            ai_files = ['ai/__init__.py', 'ai/analyzer.py', 'ai/gemini_client.py']
            for ai_file in ai_files:
                ai_path = self.base_dir / ai_file
                if not ai_path.exists():
                    logger.warning(f"    Archivo de IA faltante: {ai_file}")
                    issues_found += 1
            
            if issues_found == 0:
                logger.info("    Integridad de datos verificada - Sin problemas")
            else:
                logger.warning(f"    {issues_found} problemas de integridad encontrados")
            
            return issues_found == 0
            
        except Exception as e:
            logger.error(f"    Error verificando integridad: {e}")
            return False
    
    def update_indexes(self) -> bool:
        """Actualiza índices del sistema"""
        try:
            # Crear índice de archivos de datos
            index_data = {
                'updated_at': datetime.now().isoformat(),
                'files': {},
                'stats': {
                    'total_csv_files': 0,
                    'total_json_files': 0,
                    'total_reports': 0,
                    'total_size_mb': 0
                }
            }
            
            total_size = 0
            
            # Indexar archivos CSV
            for csv_file in self.data_dir.rglob("*.csv"):
                try:
                    stat_info = csv_file.stat()
                    rel_path = str(csv_file.relative_to(self.base_dir))
                    
                    index_data['files'][rel_path] = {
                        'type': 'csv',
                        'size_bytes': stat_info.st_size,
                        'modified_at': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        'checksum': self._calculate_file_checksum(csv_file)
                    }
                    
                    total_size += stat_info.st_size
                    index_data['stats']['total_csv_files'] += 1
                    
                except Exception as e:
                    logger.debug(f"    Error indexando {csv_file}: {e}")
            
            # Indexar archivos JSON de datos
            for json_file in self.data_dir.rglob("*.json"):
                if 'metrics' not in str(json_file):  # Excluir métricas
                    try:
                        stat_info = json_file.stat()
                        rel_path = str(json_file.relative_to(self.base_dir))
                        
                        index_data['files'][rel_path] = {
                            'type': 'json',
                            'size_bytes': stat_info.st_size,
                            'modified_at': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                            'checksum': self._calculate_file_checksum(json_file)
                        }
                        
                        total_size += stat_info.st_size
                        index_data['stats']['total_json_files'] += 1
                        
                    except Exception as e:
                        logger.debug(f"    Error indexando {json_file}: {e}")
            
            # Contar reportes
            if self.reports_dir.exists():
                index_data['stats']['total_reports'] = len(list(self.reports_dir.rglob("*")))
            
            index_data['stats']['total_size_mb'] = total_size / 1024 / 1024
            
            # Guardar índice
            index_file = self.data_dir / "file_index.json"
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"    Índice actualizado: {len(index_data['files'])} archivos indexados")
            return True
            
        except Exception as e:
            logger.error(f"    Error actualizando índices: {e}")
            return False
    
    def backup_configuration(self) -> bool:
        """Crea backup de archivos de configuración"""
        try:
            backup_dir = self.data_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_subdir = backup_dir / f"config_backup_{timestamp}"
            backup_subdir.mkdir()
            
            # Archivos de configuración a respaldar
            config_files = [
                '.env',
                'requirements.txt',
                'ai_routes.py',
                'utils.py'
            ]
            
            # Directorios de configuración
            config_dirs = [
                'ai',
                'templates',
                'static'
            ]
            
            backed_up_count = 0
            
            # Respaldar archivos
            for config_file in config_files:
                source_path = self.base_dir / config_file
                if source_path.exists():
                    dest_path = backup_subdir / config_file
                    shutil.copy2(source_path, dest_path)
                    backed_up_count += 1
            
            # Respaldar directorios
            for config_dir in config_dirs:
                source_path = self.base_dir / config_dir
                if source_path.exists():
                    dest_path = backup_subdir / config_dir
                    shutil.copytree(source_path, dest_path, ignore_errors=True)
                    backed_up_count += 1
            
            # Crear archivo de metadatos del backup
            backup_metadata = {
                'created_at': datetime.now().isoformat(),
                'backed_up_files': backed_up_count,
                'python_version': sys.version,
                'system_info': {
                    'platform': sys.platform,
                    'cwd': str(self.base_dir)
                }
            }
            
            metadata_file = backup_subdir / "backup_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(backup_metadata, f, indent=2, ensure_ascii=False)
            
            # Limpiar backups antiguos (mantener solo últimos 10)
            backup_dirs = sorted([d for d in backup_dir.iterdir() if d.is_dir() and d.name.startswith('config_backup_')])
            if len(backup_dirs) > 10:
                for old_backup in backup_dirs[:-10]:
                    shutil.rmtree(old_backup, ignore_errors=True)
            
            logger.info(f"    Backup creado: {backup_subdir} ({backed_up_count} elementos)")
            return True
            
        except Exception as e:
            logger.error(f"    Error creando backup: {e}")
            return False
    
    def check_disk_space(self) -> bool:
        """Verifica espacio disponible en disco"""
        try:
            import psutil
            
            disk_usage = psutil.disk_usage(str(self.base_dir))
            
            free_gb = disk_usage.free / 1024 / 1024 / 1024
            total_gb = disk_usage.total / 1024 / 1024 / 1024
            used_percent = (disk_usage.used / disk_usage.total) * 100
            
            logger.info(f"    Espacio en disco: {free_gb:.1f} GB libres de {total_gb:.1f} GB ({used_percent:.1f}% usado)")
            
            if used_percent > 95:
                logger.error(f"    ❌ Espacio en disco crítico: solo {free_gb:.1f} GB libres")
                return False
            elif used_percent > 85:
                logger.warning(f"    ⚠️  Espacio en disco limitado: {free_gb:.1f} GB libres")
            
            return True
            
        except Exception as e:
            logger.error(f"    Error verificando espacio en disco: {e}")
            return False
    
    def check_dependencies(self) -> bool:
        """Verifica dependencias del sistema"""
        try:
            missing_deps = []
            
            # Dependencias críticas
            critical_deps = [
                'flask',
                'pandas',
                'python-dotenv',
                'google-generativeai'
            ]
            
            for dep in critical_deps:
                try:
                    __import__(dep.replace('-', '_'))
                except ImportError:
                    missing_deps.append(dep)
            
            # Dependencias opcionales
            optional_deps = {
                'reportlab': 'Exportación PDF',
                'docx': 'Exportación Word',
                'markdown': 'Procesamiento Markdown',
                'psutil': 'Monitoreo del sistema'
            }
            
            missing_optional = []
            for dep, description in optional_deps.items():
                try:
                    __import__(dep)
                except ImportError:
                    missing_optional.append(f"{dep} ({description})")
            
            if missing_deps:
                logger.error(f"    ❌ Dependencias críticas faltantes: {', '.join(missing_deps)}")
                return False
            
            if missing_optional:
                logger.warning(f"    ⚠️  Dependencias opcionales faltantes: {', '.join(missing_optional)}")
            
            logger.info("    Dependencias críticas verificadas")
            return True
            
        except Exception as e:
            logger.error(f"    Error verificando dependencias: {e}")
            return False
    
    def generate_health_report(self) -> bool:
        """Genera reporte de salud del sistema"""
        try:
            health_report = {
                'generated_at': datetime.now().isoformat(),
                'system_info': {
                    'python_version': sys.version,
                    'platform': sys.platform,
                    'working_directory': str(self.base_dir)
                },
                'directory_structure': {},
                'file_counts': {},
                'disk_usage': {},
                'recent_activity': {},
                'recommendations': []
            }
            
            # Información de directorios
            for dir_name in ['data', 'logs', 'ai', 'templates', 'static']:
                dir_path = self.base_dir / dir_name
                if dir_path.exists():
                    size = self._get_directory_size(dir_path)
                    file_count = len(list(dir_path.rglob("*")))
                    
                    health_report['directory_structure'][dir_name] = {
                        'exists': True,
                        'size_mb': size / 1024 / 1024,
                        'file_count': file_count
                    }
                else:
                    health_report['directory_structure'][dir_name] = {'exists': False}
            
            # Conteos de archivos por tipo
            file_types = {'.csv': 0, '.json': 0, '.log': 0, '.py': 0, '.html': 0}
            for file_type in file_types:
                count = len(list(self.base_dir.rglob(f"*{file_type}")))
                health_report['file_counts'][file_type] = count
            
            # Uso de disco
            try:
                import psutil
                disk_usage = psutil.disk_usage(str(self.base_dir))
                health_report['disk_usage'] = {
                    'total_gb': disk_usage.total / 1024 / 1024 / 1024,
                    'free_gb': disk_usage.free / 1024 / 1024 / 1024,
                    'used_percent': (disk_usage.used / disk_usage.total) * 100
                }
            except ImportError:
                health_report['disk_usage'] = {'error': 'psutil no disponible'}
            
            # Actividad reciente
            if self.logs_dir.exists():
                recent_logs = sorted(self.logs_dir.glob("*.log"), 
                                   key=lambda x: x.stat().st_mtime, reverse=True)
                if recent_logs:
                    latest_log = recent_logs[0]
                    health_report['recent_activity']['latest_log'] = {
                        'file': str(latest_log.name),
                        'modified': datetime.fromtimestamp(latest_log.stat().st_mtime).isoformat(),
                        'size_kb': latest_log.stat().st_size / 1024
                    }
            
            # Recomendaciones
            if health_report['disk_usage'].get('used_percent', 0) > 85:
                health_report['recommendations'].append("Considerar limpiar archivos antiguos - uso de disco alto")
            
            if health_report['directory_structure'].get('data', {}).get('size_mb', 0) > 1000:
                health_report['recommendations'].append("Directorio de datos grande - considerar archivado")
            
            if not health_report['recommendations']:
                health_report['recommendations'].append("Sistema en buen estado - sin recomendaciones")
            
            # Guardar reporte
            report_file = self.data_dir / "health_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(health_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"    Reporte de salud generado: {report_file}")
            
            # Mostrar resumen
            total_size = sum(d.get('size_mb', 0) for d in health_report['directory_structure'].values())
            logger.info(f"    Tamaño total del proyecto: {total_size:.1f} MB")
            
            return True
            
        except Exception as e:
            logger.error(f"    Error generando reporte de salud: {e}")
            return False
    
    def _get_directory_size(self, path: Path) -> int:
        """Calcula tamaño de directorio en bytes"""
        total_size = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
        except Exception:
            pass
        return total_size
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calcula checksum MD5 de archivo"""
        try:
            import hashlib
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return "error"

def main():
    """Función principal del script de mantenimiento"""
    parser = argparse.ArgumentParser(description='Script de mantenimiento para Dashboard IT')
    parser.add_argument('--full', action='store_true', help='Ejecutar mantenimiento completo')
    parser.add_argument('--cleanup', action='store_true', help='Solo ejecutar tareas de limpieza')
    parser.add_argument('--verify', action='store_true', help='Solo verificar integridad')
    parser.add_argument('--backup', action='store_true', help='Solo crear backup de configuración')
    parser.add_argument('--health', action='store_true', help='Solo generar reporte de salud')
    
    args = parser.parse_args()
    
    # Crear directorio de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    maintenance_manager = MaintenanceManager()
    
    if args.full or not any([args.cleanup, args.verify, args.backup, args.health]):
        # Mantenimiento completo
        results = maintenance_manager.run_full_maintenance()
        success_rate = sum(results.values()) / len(results)
        exit_code = 0 if success_rate >= 0.8 else 1
        
    elif args.cleanup:
        logger.info("Ejecutando solo tareas de limpieza...")
        tasks = [
            maintenance_manager.cleanup_temp_files,
            maintenance_manager.cleanup_old_cache,
            maintenance_manager.cleanup_old_reports,
            maintenance_manager.cleanup_old_metrics,
            maintenance_manager.rotate_logs
        ]
        results = [task() for task in tasks]
        exit_code = 0 if all(results) else 1
        
    elif args.verify:
        logger.info("Verificando integridad del sistema...")
        success = maintenance_manager.verify_data_integrity()
        exit_code = 0 if success else 1
        
    elif args.backup:
        logger.info("Creando backup de configuración...")
        success = maintenance_manager.backup_configuration()
        exit_code = 0 if success else 1
        
    elif args.health:
        logger.info("Generando reporte de salud...")
        success = maintenance_manager.generate_health_report()
        exit_code = 0 if success else 1
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()