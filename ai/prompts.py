"""
Gestión de prompts para análisis de IA
"""

from typing import Dict, Any

class PromptManager:
    """Administrador de prompts para diferentes tipos de análisis"""
    
    @staticmethod
    def get_comprehensive_analysis_prompt() -> str:
        """
        Prompt principal para análisis exhaustivo del Director de Tecnología
        """
        return """
Contexto y Rol

Actúa como Director de Tecnología de la Clínica Bonsana, una clínica especializada en fracturas. Tienes amplia experiencia en gestión de servicios IT en el sector salud y conoces los estándares de la industria para departamentos de soporte técnico en entornos clínicos.

Archivos Proporcionados: CSV de datos: Base de datos completa de tickets (glpi.csv)

Solicitud de Análisis Completo

Realiza un análisis exhaustivo y estratégico que incluya:

ANÁLISIS DE RENDIMIENTO ACTUAL: 
- Evalúa cada KPI mostrado en el dashboard (tasa de resolución, tiempo promedio, cumplimiento SLA, CSAT)
- Analiza la distribución por tipo de incidentes, prioridades y estados
- Examina la carga de trabajo por técnico y identifica desequilibrios
- Correlaciona los datos del dashboard con el detalle del CSV

ANÁLISIS PROFUNDO DE DATOS CSV: 
- Examina patrones temporales (horarios pico, días críticos, estacionalidad)
- Identifica tipos de incidentes más frecuentes y sus tiempos de resolución
- Analiza la escalabilidad del equipo y distribución de cargas
- Detecta anomalías, outliers y casos excepcionales
- Evalúa la evolución de métricas en el tiempo

BENCHMARKING Y CONTEXTO CLÍNICO: 
- Compara nuestros indicadores con estándares de la industria healthcare
- Evalúa si los tiempos de respuesta son apropiados para un entorno clínico crítico
- Analiza el impacto potencial en operaciones médicas y atención al paciente

IDENTIFICACIÓN DE FORTALEZAS Y DEBILIDADES: 
- Fortalezas: Qué estamos haciendo excepcionalmente bien
- Debilidades críticas: Problemas que requieren atención inmediata
- Brechas operativas: Áreas donde no cumplimos expectativas del sector salud

ANÁLISIS DE RIESGOS: 
- Identifica riesgos operacionales para la continuidad del servicio clínico
- Evalúa vulnerabilidades en la cobertura de soporte
- Analiza dependencias críticas y puntos de falla únicos

OPORTUNIDADES DE MEJORA: 
- Propuestas concretas para optimización de procesos
- Recomendaciones para reducir tiempos de resolución
- Estrategias para mejorar satisfacción del cliente interno
- Oportunidades de automatización y eficiencia

PLAN DE ACCIÓN ESTRATÉGICO

Proporciona un plan estructurado con:
- Acciones inmediatas (0-30 días)
- Mejoras a mediano plazo (1-6 meses)
- Iniciativas estratégicas (6-12 meses)
- Métricas de seguimiento y KPIs recomendados
- Inversiones requeridas (personal, herramientas, capacitación)

CONSIDERACIONES ESPECÍFICAS DEL SECTOR SALUD: 
- Evalúa el cumplimiento con regulaciones de salud y seguridad de datos
- Analiza la criticidad de sistemas médicos vs. administrativos
- Propone clasificaciones de prioridad específicas para entornos clínicos

Formato de Entrega: 
- Resumen ejecutivo (2-3 párrafos clave para la dirección)
- Análisis detallado por secciones
- Visualizaciones adicionales si son necesarias para clarificar hallazgos
- Cronograma de implementación con responsables y recursos

Objetivo Final: 
Proporcionar insights accionables que permitan:
- Mejorar la calidad del servicio IT para staff médico
- Reducir interrupciones en operaciones críticas de la clínica
- Optimizar la inversión en recursos tecnológicos
- Establecer un departamento IT de clase mundial para el sector salud

Sé exhaustivo, analítico y estratégico. No omitas ningún aspecto relevante para la toma de decisiones gerenciales.
"""
    
    @staticmethod
    def get_quick_analysis_prompt() -> str:
        """
        Prompt para análisis rápido de métricas clave
        """
        return """
Como Director de TI de Clínica Bonsana, realiza un análisis rápido y conciso de los datos proporcionados.

Enfócate en:
1. **Estado actual**: Resumen de KPIs principales
2. **Problemas críticos**: Top 3 issues que requieren atención inmediata
3. **Recomendaciones urgentes**: Acciones concretas para los próximos 30 días

Mantén el análisis en máximo 500 palabras, priorizando actionable insights.
"""
    
    @staticmethod
    def get_technician_performance_prompt() -> str:
        """
        Prompt para análisis de rendimiento por técnico
        """
        return """
Como Director de TI, analiza el rendimiento individual de cada técnico del equipo de soporte.

Para cada técnico, evalúa:
1. **Productividad**: Volumen de tickets resueltos vs. asignados
2. **Calidad**: Tiempo de resolución, cumplimiento SLA, satisfacción cliente
3. **Especialización**: Tipos de tickets que maneja mejor
4. **Desarrollo**: Áreas de mejora y fortalezas identificadas

Proporciona recomendaciones específicas para:
- Redistribución de cargas de trabajo
- Capacitación especializada
- Reconocimiento por buen desempeño
- Planes de mejora individual
"""
    
    @staticmethod
    def get_sla_analysis_prompt() -> str:
        """
        Prompt para análisis específico de SLA
        """
        return """
Como Director de TI en un entorno clínico crítico, analiza exhaustivamente el cumplimiento de SLA.

Evalúa:
1. **Cumplimiento por nivel de SLA**: INC_ALTO, INC_MEDIO, INC_BAJO
2. **Patrones de incumplimiento**: Cuándo y por qué se exceden los SLAs
3. **Impacto en operaciones clínicas**: Riesgo para continuidad del servicio
4. **Benchmarking**: Comparación con estándares healthcare

Proporciona:
- Estrategias para mejorar cumplimiento
- Redefinición de SLAs si es necesario
- Escalation procedures optimizados
- Métricas de monitoreo recomendadas
"""
    
    @staticmethod
    def get_trend_analysis_prompt() -> str:
        """
        Prompt para análisis de tendencias temporales
        """
        return """
Como Director de TI, analiza las tendencias temporales en los datos de tickets.

Examina:
1. **Patrones horarios**: Picos de demanda durante el día
2. **Patrones semanales**: Días de mayor/menor actividad
3. **Tendencias mensuales**: Evolución de métricas en el tiempo
4. **Estacionalidad**: Variaciones por períodos específicos

Identifica:
- Horarios óptimos para mantenimientos
- Necesidades de staffing por horario/día
- Predicciones de carga de trabajo
- Oportunidades de proactividad

Proporciona recomendaciones para optimizar la cobertura y recursos.
"""
    
    @staticmethod
    def get_cost_optimization_prompt() -> str:
        """
        Prompt para análisis de optimización de costos
        """
        return """
Como Director de TI, analiza las oportunidades de optimización de costos en el departamento de soporte.

Evalúa:
1. **Eficiencia del equipo**: Costo por ticket resuelto
2. **Automatización**: Procesos que pueden automatizarse
3. **Herramientas**: ROI de inversiones en tecnología
4. **Outsourcing**: Tareas que podrían externalizarse

Proporciona:
- Análisis costo-beneficio de mejoras propuestas
- Priorización de inversiones por impacto/costo
- Estrategias de reducción de costos sin afectar calidad
- Métricas financieras para seguimiento
"""
    
    @staticmethod
    def get_custom_prompt(focus_area: str, specific_questions: list = None) -> str:
        """
        Genera un prompt personalizado basado en área de enfoque
        
        Args:
            focus_area: Área específica de análisis
            specific_questions: Preguntas específicas a responder
        """
        base_prompt = f"""
Como Director de TI de Clínica Bonsana, realiza un análisis especializado enfocado en: {focus_area}

Contexto: Clínica especializada en fracturas que requiere soporte IT crítico para operaciones médicas.
"""
        
        if specific_questions:
            base_prompt += "\n\nResponde específicamente estas preguntas:\n"
            for i, question in enumerate(specific_questions, 1):
                base_prompt += f"{i}. {question}\n"
        
        base_prompt += """
\nProporciona un análisis detallado con recomendaciones accionables y métricas de seguimiento.
"""
        
        return base_prompt
    
    @staticmethod
    def get_available_prompts() -> Dict[str, str]:
        """
        Retorna diccionario con todos los prompts disponibles
        """
        return {
            "comprehensive": "Análisis Exhaustivo Completo",
            "quick": "Análisis Rápido de KPIs",
            "technician": "Rendimiento por Técnico",
            "sla": "Análisis de SLA",
            "trends": "Análisis de Tendencias",
            "cost": "Optimización de Costos"
        }