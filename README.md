# Dashboard IT - Clínica Bonsana

Dashboard web para visualización y análisis de métricas de tickets de soporte IT desarrollado con Flask, Pandas y Bootstrap.

## 🏥 Características

### Métricas Principales
- **Total de Tickets**: Conteo general de todos los tickets
- **Tasa de Resolución**: Porcentaje de tickets resueltos (Estados: 'Resueltas' y 'Cerrado')
- **Tiempo Promedio de Resolución**: Calculado en horas para tickets resueltos
- **Cumplimiento SLA**: Porcentaje de incidencias resueltas dentro del SLA

### Visualizaciones
- 📊 Distribución por tipo (Incidencia vs Requerimiento)
- 📈 Estado actual de tickets
- ⚡ Distribución por prioridad
- 👥 Carga de trabajo por técnico
- 🌟 Puntuación CSAT (Customer Satisfaction)
- 📋 Top categorías de problemas
- 🔍 Análisis de SLA por nivel

### Análisis de Calidad de Datos
- Tickets sin técnico asignado
- Tickets sin categoría definida
- Tickets de hardware sin elementos asociados
- Recomendaciones para mejorar la calidad de datos

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3.12, Flask
- **Procesamiento de Datos**: Pandas, NumPy
- **Frontend**: Bootstrap 5, Chart.js
- **Estilos**: CSS personalizado con colores corporativos (rojo y blanco)

## 📂 Estructura del Proyecto

```
proyecto/
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
├── data/
│   └── glpi.csv          # Archivo de datos CSV
├── templates/
│   └── index.html        # Template principal
└── static/
    └── style.css         # Estilos CSS personalizados
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.12 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   cd dashboard-clinica-bonsana
   ```

2. **Crear un entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Preparar los datos**
   - Crear el directorio `data/` si no existe
   - Colocar el archivo `glpi.csv` en el directorio `data/`
   - Asegurarse de que el CSV use `;` como delimitador

5. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

6. **Acceder al dashboard**
   - Abrir navegador web
   - Ir a: `http://localhost:5000`

## 📋 Formato de Datos CSV

El archivo CSV debe tener las siguientes columnas (delimitador: `;`):

### Columnas Principales
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
- `Elementos asociados`: Equipos asociados
- `ANS (Acuerdo de nivel de servicio) - ANS (Acuerdo de nivel de servicio) Tiempo de solución`: Nivel SLA
- `Encuesta de satisfacción - Satisfacción`: Puntuación 1-5

## 🎨 Personalización

### Colores Corporativos
El dashboard utiliza la paleta de colores de Clínica Bonsana:
- **Rojo Principal**: `#dc3545`
- **Rojo Oscuro**: `#b02a37`
- **Blanco**: `#ffffff`
- **Gris Claro**: `#f8f9fa`

### Modificar Estilos
Los estilos se pueden personalizar editando:
- `static/style.css`: Estilos CSS principales
- `templates/index.html`: Variables CSS y estilos en línea

## 📊 API Endpoints

La aplicación proporciona varios endpoints para acceso a datos:

- `GET /api/metrics`: Métricas generales
- `GET /api/distributions`: Distribuciones por categoría
- `GET /api/technicians`: Carga de trabajo por técnico
- `GET /api/requesters`: Top solicitantes
- `GET /api/sla`: Análisis de SLA
- `GET /api/csat`: Puntuación CSAT
- `GET /api/validation`: Insights de validación
- `GET /api/trends`: Tendencias mensuales

## 🔄 Extensiones Futuras

### Múltiples Archivos CSV
El sistema está diseñado para soportar múltiples archivos CSV mensuales:

```python
# Ejemplo para cargar múltiples archivos
csv_files = ['enero.csv', 'febrero.csv', 'marzo.csv']
# La clase TicketAnalyzer puede extenderse para manejar múltiples archivos
```

### Filtros por Periodo
Se puede implementar filtrado por:
- Mes específico
- Rango de fechas
- Año fiscal

### Exportación de Reportes
- PDF con métricas principales
- Excel con datos detallados
- Programación de reportes automáticos

## 🐛 Resolución de Problemas

### Error: "No se encontraron archivos CSV"
- Verificar que el directorio `data/` existe
- Asegurar que `glpi.csv` está en el directorio correcto
- Comprobar permisos de lectura del archivo

### Error: "Error al cargar los datos"
- Verificar que el CSV usa `;` como delimitador
- Comprobar que todas las columnas requeridas existen
- Revisar formato de fechas: 'YYYY-MM-DD HH:MM'

### Gráficos no se muestran
- Verificar conexión a internet (Chart.js se carga desde CDN)
- Comprobar consola del navegador para errores JavaScript
- Asegurar que los datos API se cargan correctamente

## 📈 Métricas y KPIs Implementados

### KPIs Principales
1. **Tasa de Resolución**: (Tickets Resueltos / Total Tickets) × 100
2. **Cumplimiento SLA**: (Incidencias dentro SLA / Total Incidencias) × 100
3. **CSAT Score**: Promedio de puntuaciones de satisfacción (1-5)
4. **Tiempo Promedio de Resolución**: En horas, solo tickets resueltos

### Métricas Secundarias
- Backlog actual (tickets pendientes)
- Distribución por prioridad
- Carga de trabajo por técnico
- Top categorías de problemas
- Análisis de calidad de datos

## 🔐 Seguridad

### Consideraciones
- No exponer datos sensibles en logs
- Validar entrada de archivos CSV
- Implementar autenticación para producción
- Usar HTTPS en entorno de producción

## 📞 Soporte

Para soporte técnico o consultas sobre la implementación:
- Revisar logs de la aplicación Flask
- Verificar formato de datos CSV
- Consultar documentación de dependencias

## 📄 Licencia

Proyecto desarrollado para Clínica Bonsana - Uso interno

---

**Desarrollado con ❤️ para Clínica Bonsana**