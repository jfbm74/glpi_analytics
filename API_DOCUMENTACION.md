# API Documentation - Dashboard IT Clínica Bonsana

## Introducción

Esta documentación describe la API REST del sistema Dashboard IT con análisis de IA para Clínica Bonsana. La API proporciona acceso programático a todas las funcionalidades del sistema, incluyendo análisis de IA, métricas de tickets, monitoreo del sistema y gestión de reportes.

## Información General

- **Base URL**: `https://dashboard.clinicabonsana.com/api`
- **Versión**: 1.0.0
- **Formato de respuesta**: JSON
- **Encoding**: UTF-8
- **Rate Limiting**: 60 requests/minuto por IP

## Autenticación

Actualmente el sistema utiliza autenticación básica. En futuras versiones se implementará autenticación por tokens JWT.

```bash
# Ejemplo con autenticación básica
curl -u "username:password" https://dashboard.clinicabonsana.com/api/metrics
```

## Endpoints Principales

### 1. Dashboard y Métricas

#### GET /api/metrics
Obtiene métricas generales del dashboard.

**Respuesta**:
```json
{
  "total_tickets": 150,
  "resolution_rate": 95.5,
  "avg_resolution_time_hours": 12.5,
  "sla_compliance": 98.2,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### GET /api/distributions
Obtiene distribución de tickets por diferentes categorías.

**Respuesta**:
```json
{
  "by_type": {
    "Incidencia": 120,
    "Requerimiento": 30
  },
  "by_status": {
    "Resueltas": 140,
    "En curso": 8,
    "Nuevo": 2
  },
  "by_priority": {
    "Alta": 45,
    "Mediana": 75,
    "Baja": 30
  },
  "by_category": {
    "Hardware > Impresora": 25,
    "Software > Sistema operativo": 20,
    "Red > Conectividad": 15
  }
}
```

#### GET /api/technicians
Obtiene carga de trabajo por técnico.

**Respuesta**:
```json
{
  "JORGE AURELIO BETANCOURT": 45,
  "SANTIAGO HURTADO MORENO": 38,
  "CARLOS MARTINEZ LOPEZ": 25,
  "SIN ASIGNAR": 5
}
```

### 2. Análisis de IA

#### POST /ai/api/ai/analyze
Ejecuta análisis de IA sobre los datos de tickets.

**Parámetros**:
```json
{
  "analysis_type": "comprehensive|quick|technician|sla|trends|cost",
  "custom_focus": "string (opcional)",
  "specific_questions": ["string1", "string2"] // opcional
}
```

**Respuesta**:
```json
{
  "success": true,
  "analysis": "# Análisis Exhaustivo de IT...\n\n## Resumen Ejecutivo...",
  "analysis_type": "comprehensive",
  "model_used": "gemini-2.0-flash-exp",
  "processing_time": 45.2,
  "timestamp": 1705312200.123,
  "prompt_tokens": 2500,
  "response_tokens": 1800,
  "cache_key": "comprehensive_20240115_103000"
}
```

#### GET /ai/api/ai/test-connection
Prueba la conexión con la API de IA.

**Respuesta**:
```json
{
  "success": true,
  "message": "Conexión exitosa con Gemini AI",
  "response": "¡Estoy funcionando correctamente!",
  "model": "gemini-2.0-flash-exp"
}
```

#### GET /ai/api/ai/model-info
Obtiene información del modelo de IA actual.

**Respuesta**:
```json
{
  "success": true,
  "model_info": {
    "model_name": "gemini-2.0-flash-exp",
    "available": true,
    "details": {
      "name": "models/gemini-2.0-flash-exp",
      "description": "Gemini 2.0 Flash Experimental",
      "input_token_limit": 1000000,
      "output_token_limit": 8192
    }
  }
}
```

#### GET /ai/api/ai/available-types
Obtiene tipos de análisis disponibles.

**Respuesta**:
```json
{
  "success": true,
  "analysis_types": {
    "comprehensive": "Análisis Exhaustivo Completo",
    "quick": "Análisis Rápido de KPIs",
    "technician": "Rendimiento por Técnico",
    "sla": "Análisis de SLA",
    "trends": "Análisis de Tendencias",
    "cost": "Optimización de Costos"
  }
}
```

#### GET /ai/api/ai/history
Obtiene historial de análisis realizados.

**Respuesta**:
```json
{
  "success": true,
  "history": [
    {
      "cache_key": "comprehensive_20240115_103000",
      "analysis_type": "comprehensive",
      "timestamp": "2024-01-15T10:30:00Z",
      "processing_time": 45.2,
      "success": true
    }
  ]
}
```

#### POST /ai/api/ai/save-analysis
Guarda análisis en archivo.

**Parámetros**:
```json
{
  "analysis": "contenido del análisis",
  "analysis_type": "comprehensive",
  "format": "json|html|pdf|word"
}
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Análisis guardado exitosamente",
  "filepath": "/data/reports/analysis_comprehensive_20240115.json",
  "filename": "analysis_comprehensive_20240115.json"
}
```

### 3. Monitoreo y Sistema

#### GET /ai/api/ai/status
Obtiene estado actual del sistema de IA.

**Respuesta**:
```json
{
  "success": true,
  "status": {
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "active_analyses": {
      "count": 2,
      "details": [
        {
          "id": "analysis_123",
          "type": "comprehensive",
          "model": "gemini-2.0-flash-exp",
          "duration_seconds": 120.5
        }
      ]
    },
    "today_stats": {
      "total_analyses": 15,
      "successful_analyses": 14,
      "success_rate": 93.3,
      "total_tokens": 45000,
      "total_cost": 0.45,
      "avg_processing_time": 35.2
    },
    "system_metrics": {
      "cpu_percent": 25.3,
      "memory_percent": 45.7,
      "disk_usage_percent": 32.1,
      "cache_size_mb": 128.5
    },
    "model_usage": {
      "gemini-2.0-flash-exp": 12,
      "gemini-1.5-pro": 3
    },
    "top_errors": {
      "API quota exceeded": 2,
      "Network timeout": 1
    }
  }
}
```

#### GET /ai/api/ai/trends?days=7
Obtiene tendencias de rendimiento.

**Parámetros de consulta**:
- `days`: Número de días para el análisis (default: 7)

**Respuesta**:
```json
{
  "success": true,
  "period_days": 7,
  "daily_trends": {
    "2024-01-15": {
      "total_analyses": 15,
      "success_rate": 93.3,
      "avg_processing_time": 35.2,
      "total_tokens": 45000,
      "total_cost": 0.45
    }
  },
  "summary": {
    "total_analyses": 105,
    "overall_success_rate": 94.3,
    "avg_daily_analyses": 15,
    "total_cost": 3.15
  }
}
```

#### GET /ai/api/ai/health
Realiza chequeo de salud del sistema.

**Respuesta**:
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "issues": [],
  "warnings": [
    "Uso de memoria elevado: 85.2%"
  ],
  "active_analyses_count": 2,
  "stuck_analyses": [],
  "monitoring_active": true
}
```

### 4. Gestión de Reportes

#### GET /api/reports
Lista reportes disponibles.

**Respuesta**:
```json
{
  "reports": [
    {
      "filename": "analysis_comprehensive_20240115.pdf",
      "created_at": "2024-01-15T10:30:00Z",
      "size_mb": 2.5,
      "type": "pdf",
      "analysis_type": "comprehensive"
    }
  ]
}
```

#### GET /api/reports/{filename}
Descarga un reporte específico.

**Respuesta**: Archivo binario con headers apropiados.

#### POST /api/reports/export
Exporta análisis en formato específico.

**Parámetros**:
```json
{
  "analysis_data": {...},
  "format": "pdf|word|html|json",
  "filename": "custom_report.pdf"
}
```

**Respuesta**:
```json
{
  "success": true,
  "download_url": "/api/reports/custom_report.pdf",
  "filename": "custom_report.pdf"
}
```

### 5. Configuración

#### GET /ai/api/ai/config
Obtiene configuración actual del sistema.

**Respuesta**:
```json
{
  "ai_enabled": true,
  "model": "gemini-2.0-flash-exp",
  "api_configured": true,
  "max_csv_rows": 1000,
  "cache_timeout": 3600,
  "export_formats": {
    "pdf": true,
    "word": true,
    "html": true,
    "json": true
  }
}
```

## Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Solicitud malformada |
| 401 | Unauthorized - Autenticación requerida |
| 403 | Forbidden - Sin permisos suficientes |
| 404 | Not Found - Recurso no encontrado |
| 429 | Too Many Requests - Rate limit excedido |
| 500 | Internal Server Error - Error del servidor |
| 503 | Service Unavailable - Servicio no disponible |

## Manejo de Errores

Todas las respuestas de error siguen este formato:

```json
{
  "success": false,
  "error": "Descripción del error",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### Códigos de Error Específicos

| Código | Descripción |
|--------|-------------|
| `API_KEY_INVALID` | API key de IA inválida o expirada |
| `MODEL_UNAVAILABLE` | Modelo de IA no disponible |
| `QUOTA_EXCEEDED` | Cuota de API excedida |
| `ANALYSIS_TIMEOUT` | Análisis excedió tiempo límite |
| `DATA_INVALID` | Datos de entrada inválidos |
| `FILE_NOT_FOUND` | Archivo CSV no encontrado |
| `EXPORT_FAILED` | Error en exportación de reporte |

## Rate Limiting

El sistema implementa rate limiting para proteger los recursos:

- **API General**: 60 requests/minuto por IP
- **Análisis de IA**: 10 requests/minuto por IP
- **Descarga de reportes**: 20 requests/minuto por IP

Headers de respuesta para rate limiting:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705312800
```

## Webhooks

El sistema puede configurarse para enviar webhooks cuando ocurren eventos específicos:

### POST /api/webhooks/register
Registra un webhook.

**Parámetros**:
```json
{
  "url": "https://tu-sistema.com/webhook",
  "events": ["analysis_completed", "system_alert"],
  "secret": "webhook_secret_key"
}
```

### Eventos Disponibles

- `analysis_completed`: Análisis de IA completado
- `analysis_failed`: Análisis de IA falló
- `system_alert`: Alerta del sistema
- `quota_warning`: Advertencia de cuota
- `backup_completed`: Backup completado

### Formato de Webhook

```json
{
  "event": "analysis_completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "analysis_id": "analysis_123",
    "analysis_type": "comprehensive",
    "success": true,
    "processing_time": 45.2
  },
  "signature": "sha256=..."
}
```

## Ejemplos de Uso

### Ejecutar Análisis Completo

```bash
curl -X POST https://dashboard.clinicabonsana.com/ai/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_type": "comprehensive"
  }'
```

### Obtener Métricas del Dashboard

```bash
curl https://dashboard.clinicabonsana.com/api/metrics \
  -H "Accept: application/json"
```

### Descargar Reporte

```bash
curl https://dashboard.clinicabonsana.com/api/reports/analysis_20240115.pdf \
  -o reporte_analisis.pdf
```

### Verificar Estado del Sistema

```bash
curl https://dashboard.clinicabonsana.com/ai/api/ai/health \
  -H "Accept: application/json"
```

## SDKs y Librerías

### Python SDK

```python
from dashboard_client import DashboardClient

client = DashboardClient(
    base_url="https://dashboard.clinicabonsana.com",
    api_key="your_api_key"
)

# Ejecutar análisis
result = client.analyze(type="comprehensive")
print(result.analysis)

# Obtener métricas
metrics = client.get_metrics()
print(f"Total tickets: {metrics.total_tickets}")
```

### JavaScript SDK

```javascript
import { DashboardClient } from 'dashboard-client';

const client = new DashboardClient({
  baseURL: 'https://dashboard.clinicabonsana.com',
  apiKey: 'your_api_key'
});

// Ejecutar análisis
const result = await client.analyze({ type: 'quick' });
console.log(result.analysis);

// Obtener estado del sistema
const status = await client.getSystemStatus();
console.log(status);
```

## Límites y Cuotas

| Recurso | Límite |
|---------|--------|
| Tamaño máximo CSV | 50 MB |
| Análisis concurrentes | 3 |
| Retención de reportes | 30 días |
| Retención de cache | 24 horas |
| Tamaño máximo reporte | 100 MB |

## Versionado

La API utiliza versionado semántico. Los cambios breaking se introducen en nuevas versiones mayores.

- **v1.x**: Versión actual estable
- **v2.x**: Próxima versión mayor (en desarrollo)

Para especificar versión:
```bash
curl -H "Accept: application/vnd.dashboard.v1+json" \
  https://dashboard.clinicabonsana.com/api/metrics
```

## Soporte

Para soporte técnico:
- **Email**: soporte@clinicabonsana.com
- **Documentation**: https://dashboard.clinicabonsana.com/docs
- **Status Page**: https://status.clinicabonsana.com

## Changelog

### v1.0.0 (2024-01-15)
- ✨ Lanzamiento inicial de la API
- 🤖 Integración completa con IA
- 📊 Endpoints de métricas y análisis
- 🔒 Sistema de autenticación
- 📁 Gestión de reportes

### v1.1.0 (Próximamente)
- 🔑 Autenticación JWT
- 📈 Métricas avanzadas
- 🔔 Sistema de notificaciones
- 🌐 Soporte multi-idioma