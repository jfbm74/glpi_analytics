# Dashboard IT - Clínica Bonsana

Dashboard web avanzado para visualización y análisis de métricas de tickets de soporte IT desarrollado con Flask, Pandas y Bootstrap.

## 🆕 Nuevas Funcionalidades v1.1

### 🎯 Estadísticas por Técnico
- **SLA por Técnico**: Cumplimiento de SLA individualizado por cada técnico
- **CSAT por Técnico**: Satisfacción del cliente por técnico asignado  
- **Tiempo de Resolución por Técnico**: Métricas de eficiencia individual

## 🏥 Características Principales

### 📊 Métricas Generales
- **Total de Tickets**: Conteo general de todos los tickets
- **Tasa de Resolución**: Porcentaje de tickets resueltos (Estados: 'Resueltas' y 'Cerrado')
- **Tiempo Promedio de Resolución**: Calculado en horas para tickets resueltos
- **Cumplimiento SLA**: Porcentaje de incidencias resueltas dentro del SLA

### 📈 Visualizaciones Avanzadas
- 📊 Distribución por tipo (Incidencia vs Requerimiento) con valores y porcentajes
- 📈 Estado actual de tickets con conteos visibles
- ⚡ Distribución por prioridad con valores y porcentajes
- 👥 Carga de trabajo por técnico (incluye tickets sin asignar) con valores
- 🌟 Puntuación CSAT (Customer Satisfaction) con distribución numérica
- 📋 Top categorías de problemas con conteos
- 🔍 Análisis de SLA por nivel

### 👨‍💻 Estadísticas por Técnico (NUEVO)

#### 🛡️ SLA por Técnico
- Cumplimiento de SLA individualizado
- Total de incidencias por técnico
- Porcentaje de cumplimiento
- Indicadores de performance visual

#### 😊 CSAT por Técnico  
- Satisfacción promedio del cliente
- Distribución de calificaciones
- Conteo de encuestas respondidas
- Identificación de ratings excelentes vs pobres

#### ⏱️ Tiempo de Resolución por Técnico
- Tiempo promedio de resolución
- Tiempo mínimo y máximo
- Conteo de resoluciones rápidas (<24h)
- Conteo de resoluciones lentas (>72h)
- Índice de eficiencia

### 🎨 Mejoras de Visualización

#### 📊 Valores en Gráficos
- **Gráficos de Barras**: Valores numéricos visibles en cada barra
- **Gráficos de Dona**: Valores y porcentajes mostrados en cada segmento
- **Colores Inteligentes**: Contraste automático para mejor legibilidad
- **Animaciones Suaves**: Transiciones fluidas al cargar datos

#### 🎯 Indicadores Visuales
- **Tickets Sin Asignar**: Color naranja distintivo con icono de advertencia
- **Estados de Performance**: Colores semáforo (verde/amarillo/rojo)
- **Tooltips Informativos**: Información detallada al hacer hover
- **Leyendas Mejoradas**: Mejor organización y legibilidad

### 🔍 Análisis de Calidad de Datos
- Tickets sin técnico asignado (visualizados en gráfico de carga)
- Tickets sin categoría definida
- Tickets de hardware sin elementos asociados
- Recomendaciones para mejorar la calidad de datos

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3.8+, Flask
- **Procesamiento de Datos**: Pandas, NumPy
- **Frontend**: Bootstrap 5, Chart.js
- **Estilos**: CSS personalizado con colores corporativos (rojo y blanco)

## 📂 Estructura del Proyecto

```
proyecto/
├── app.py                 # Aplicación Flask principal
├── config.py              # Configuración del sistema
├── utils.py               # Utilidades y herramientas
├── requirements.txt       # Dependencias Python
├── install.py             # Script de instalación
├── test_dashboard.py      # Suite de pruebas
├── README.md             # Este archivo
├── data/
│   └── glpi.csv          # Archivo de datos CSV
├── templates/
│   └── index.html        # Template principal
├── static/
│   └── style.css         # Estilos CSS personalizados
├── logs/                 # Archivos de log
└── backups/              # Respaldos automáticos
```

## 🚀 Instalación Rápida

### Opción 1: Instalación Automática (Recomendada)

```bash
# Clonar o descargar el proyecto
cd dashboard-clinica-bonsana

# Ejecutar instalador automático
python install.py
```

### Opción 2: Instalación Manual

1. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Crear directorios necesarios**
   ```bash
   mkdir data logs backups
   ```

4. **Configurar datos**
   - Colocar archivo `glpi.csv` en directorio `data/`
   - Usar `;` como delimitador en el CSV

## 🔧 Configuración

### Archivo de Configuración (config.py)

El sistema incluye configuración avanzada:

```python
# Configuración básica
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

# Umbrales de performance
METRICS_CONFIG = {
    'sla_excellent_threshold': 90,    # >= 90% SLA es excelente
    'csat_excellent_threshold': 4.0,  # >= 4.0 CSAT es excelente
    'resolution_fast_threshold': 24,  # <= 24h es resolución rápida
}
```

### Variables de Entorno

```bash
export FLASK_ENV=development    # development/production/testing
export FLASK_PORT=5000
export DATA_PATH=data
export LOG_LEVEL=INFO
```

## 📊 Nuevos Endpoints API

### Estadísticas por Técnico

#### SLA por Técnico
```http
GET /api/technicians/sla
```

Respuesta:
```json
{
  "JORGE AURELIO BETANCOURT": {
    "total_incidents": 25,
    "sla_compliant": 22,
    "sla_exceeded": 3,
    "compliance_rate": 88.0
  }
}
```

#### CSAT por Técnico
```http
GET /api/technicians/csat
```

Respuesta:
```json
{
  "SANTIAGO HURTADO MORENO": {
    "total_surveys": 15,
    "average_csat": 4.2,
    "excellent_ratings": 12,
    "poor_ratings": 1,
    "csat_distribution": {
      "1": 1, "2": 0, "3": 2, "4": 5, "5": 7
    }
  }
}
```

#### Tiempo de Resolución por Técnico
```http
GET /api/technicians/resolution-time
```

Respuesta:
```json
{
  "CARLOS MARTINEZ LOPEZ": {
    "total_resolved": 30,
    "avg_resolution_hours": 18.5,
    "min_resolution_hours": 2.0,
    "max_resolution_hours": 68.5,
    "median_resolution_hours": 16.0,
    "fast_resolutions": 20,
    "slow_resolutions": 2
  }
}
```

## 📋 Formato de Datos CSV

### Columnas Requeridas
- `ID`: Identificador único del ticket
- `Título`: Descripción del ticket
- `Tipo`: 'Incidencia' o 'Requerimiento'
- `Categoría`: Categoría del problema
- `Prioridad`: 'Alta', 'Mediana', 'Baja'
- `Estado`: 'Resueltas', 'Cerrado', 'En curso (asignada)', etc.
- `Fecha de Apertura`: Formato 'YYYY-MM-DD HH:MM'
- `Fecha de solución`: Formato 'YYYY-MM-DD HH:MM'
- `Se superó el tiempo de resolución`: 'Si' o 'No'
- `Asignado a: - Técnico`: Nombre del técnico asignado
- `Solicitante - Solicitante`: Nombre del solicitante

### Columnas Opcionales (para funcionalidades avanzadas)
- `Elementos asociados`: Equipos asociados
- `ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución`: Nivel SLA
- `Encuesta de satisfacción - Satisfacción`: Puntuación 1-5

## 🚀 Ejecución

### Inicio Manual
```bash
python app.py
```

### Scripts de Inicio
```bash
# Windows
start_dashboard.bat

# Linux/Mac
./start_dashboard.sh
```

### Acceso
Abrir navegador en: `http://localhost:5000`

## 🧪 Pruebas

### Ejecutar Suite de Pruebas
```bash
python test_dashboard.py
```

### Validar Estructura CSV
```bash
python utils.py validate data/glpi.csv
```

### Generar Datos de Prueba
```bash
python utils.py generate-sample data/sample.csv --records 100
```

### Analizar Calidad de Datos
```bash
python utils.py analyze-quality data/glpi.csv
```

## 📊 Métricas y KPIs

### 🎯 KPIs Principales
1. **Tasa de Resolución**: (Tickets Resueltos / Total Tickets) × 100
2. **Cumplimiento SLA**: (Incidencias dentro SLA / Total Incidencias) × 100
3. **CSAT Score**: Promedio de puntuaciones de satisfacción (1-5)
4. **Tiempo Promedio de Resolución**: En horas, solo tickets resueltos

### 📈 Métricas por Técnico (NUEVO)
- **SLA Individual**: Cumplimiento por técnico
- **CSAT Individual**: Satisfacción por técnico
- **Eficiencia**: Basada en tiempos de resolución

### 🔍 Métricas de Calidad
- Backlog actual (tickets pendientes)
- Distribución por prioridad
- Top categorías de problemas
- Insights de validación de datos

## 🎨 Personalización

### Colores Corporativos
```css
:root {
    --bonsana-red: #dc3545;
    --bonsana-red-dark: #b02a37;
    --bonsana-white: #ffffff;
    --bonsana-gray-light: #f8f9fa;
}
```

### Umbrales Personalizables
```python
# En config.py
METRICS_CONFIG = {
    'sla_excellent_threshold': 90,     # Personalizar umbral SLA
    'csat_excellent_threshold': 4.0,   # Personalizar umbral CSAT
    'resolution_fast_threshold': 24,   # Personalizar umbral resolución
}
```

## 🔧 Herramientas de Utilidad

### Validación de Datos
```bash
python utils.py validate data/glpi.csv
```

### Generación de Reportes
```bash
python utils.py export-report data/glpi.csv reportes/reporte.json
```

### Análisis de Calidad
```bash
python utils.py analyze-quality data/glpi.csv
```

## 🐛 Resolución de Problemas

### Error: "No se encontraron archivos CSV"
- ✅ Verificar que el directorio `data/` existe
- ✅ Asegurar que `glpi.csv` está en el directorio correcto
- ✅ Comprobar permisos de lectura del archivo

### Error: "Error al cargar los datos"
- ✅ Verificar que el CSV usa `;` como delimitador
- ✅ Comprobar que todas las columnas requeridas existen
- ✅ Revisar formato de fechas: 'YYYY-MM-DD HH:MM'

### Las nuevas estadísticas por técnico no aparecen
- ✅ Verificar que hay técnicos asignados en los datos
- ✅ Para SLA: verificar que hay incidencias con campo SLA
- ✅ Para CSAT: verificar que hay encuestas de satisfacción
- ✅ Revisar logs en `logs/dashboard.log`

### Gráficos no se muestran
- ✅ Verificar conexión a internet (Chart.js desde CDN)
- ✅ Comprobar consola del navegador para errores JavaScript
- ✅ Asegurar que los datos API se cargan correctamente

## 🚀 Extensiones Futuras

### 📅 Filtros Temporales
- Filtrado por mes específico
- Rango de fechas personalizado
- Análisis de tendencias históricas

### 📊 Exportación Avanzada
- PDF con métricas principales
- Excel con datos detallados por técnico
- Reportes programados automáticos

### 🔔 Alertas y Notificaciones
- Alertas de SLA en riesgo
- Notificaciones de baja satisfacción
- Reportes automáticos por email

### 📱 Dashboard Móvil
- Interfaz responsiva mejorada
- App móvil nativa
- Notificaciones push

## 🔐 Seguridad

### Consideraciones de Producción
- ✅ Usar HTTPS en producción
- ✅ Implementar autenticación de usuarios
- ✅ Validar entrada de archivos CSV
- ✅ No exponer datos sensibles en logs
- ✅ Configurar rate limiting para API

### Variables de Entorno Sensibles
```bash
export SECRET_KEY=tu-clave-secreta-aqui
export FLASK_ENV=production
export DATABASE_URL=postgresql://...  # Para futuras versiones
```

## 📞 Soporte y Contribución

### Reporte de Bugs
1. Revisar logs en `logs/dashboard.log`
2. Ejecutar `python test_dashboard.py` para diagnosticar
3. Verificar formato de datos con `python utils.py validate`

### Contribuir
1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📄 Changelog

### v1.1.0 (Actual)
- ✨ **NUEVO**: Estadísticas de SLA por técnico
- ✨ **NUEVO**: Estadísticas de CSAT por técnico  
- ✨ **NUEVO**: Tiempo de resolución por técnico
- ✨ **NUEVO**: Script de instalación automática
- ✨ **NUEVO**: Suite de pruebas completa
- ✨ **NUEVO**: Sistema de configuración avanzado
- 🔧 Mejorada interfaz de usuario con nueva pestaña
- 🔧 Optimizado rendimiento de carga de datos
- 🔧 Agregados endpoints API especializados
- 🔧 **NUEVO**: Gráfico de carga por técnico incluye tickets sin asignar
- 🔧 **NUEVO**: Valores mostrados directamente en todos los gráficos

### v1.0.0
- 🎉 Lanzamiento inicial
- 📊 Métricas básicas de tickets
- 📈 Visualizaciones principales
- 🔍 Análisis de calidad de datos

## 📄 Licencia

Proyecto desarrollado para **Clínica Bonsana** - Uso interno

---

**Desarrollado con ❤️ para Clínica Bonsana**

*Dashboard IT v1.1.0 - Análisis Avanzado de Soporte Técnico*