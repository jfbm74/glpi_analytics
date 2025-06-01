# Dashboard IT - Clínica Bonsana
## Análisis Inteligente con IA

### 🚀 Inicio Rápido

1. **Ejecutar el dashboard:**
   ```bash
   python run_dashboard.py
   ```

2. **Acceder a la aplicación:**
   - Dashboard principal: http://localhost:5000
   - Análisis de IA: http://localhost:5000/ai-analysis

### 🤖 Funcionalidades de IA

- **Análisis Exhaustivo Completo**: Evaluación estratégica completa
- **Análisis Rápido**: KPIs principales y insights inmediatos
- **Análisis por Técnico**: Rendimiento individual del equipo
- **Análisis de SLA**: Cumplimiento y optimización
- **Análisis de Tendencias**: Patrones temporales y predicciones
- **Optimización de Costos**: Eficiencia y ROI

### 📊 Tipos de Insights

1. **Rendimiento Actual**: Métricas clave y benchmarking
2. **Análisis Profundo**: Patrones, anomalías y tendencias
3. **Benchmarking Clínico**: Comparación con estándares healthcare
4. **Fortalezas y Debilidades**: Identificación de áreas críticas
5. **Análisis de Riesgos**: Continuidad y vulnerabilidades
6. **Plan de Acción**: Recomendaciones estratégicas

### ⚙️ Configuración

Edita el archivo `.env` para personalizar:

```bash
# API de Google AI
GOOGLE_AI_API_KEY=tu-api-key-aqui
GOOGLE_AI_MODEL=gemini-2.0-flash-exp

# Configuración de análisis
AI_MAX_CSV_ROWS=1000
AI_CACHE_TIMEOUT=3600
```

### 📁 Estructura del Proyecto

```
├── ai/                     # Módulo de IA
│   ├── __init__.py
│   ├── gemini_client.py    # Cliente Google AI
│   ├── prompts.py          # Gestión de prompts
│   └── analyzer.py         # Analizador principal
├── data/                   # Datos y reportes
│   ├── glpi.csv           # Datos de tickets
│   └── reports/           # Reportes generados
├── templates/             # Plantillas HTML
│   ├── index.html         # Dashboard principal
│   └── ai_analysis.html   # Página de IA
├── static/               # Archivos estáticos
├── logs/                 # Archivos de log
└── .env                  # Configuración
```

### 🔧 Solución de Problemas

1. **Error de API Key:**
   - Verifica que la API key de Google AI sea válida
   - Asegúrate de tener créditos disponibles

2. **Error de módulos:**
   ```bash
   pip install -r requirements_ai.txt
   ```

3. **Error de datos:**
   - Verifica que exista el archivo `data/glpi.csv`
   - Ejecuta: `python utils.py generate-sample data/sample.csv`

### 📞 Soporte

Para soporte técnico, contacta al equipo de desarrollo.
