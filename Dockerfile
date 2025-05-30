# Dashboard IT - Clínica Bonsana con Soporte para IA
# Dockerfile para containerización de la aplicación con Google AI Studio

# Usar imagen base oficial de Python 3.12
FROM python:3.12-slim

# Información del mantenedor
LABEL maintainer="IT Team - Clínica Bonsana"
LABEL description="Dashboard de análisis de tickets IT para Clínica Bonsana con IA"
LABEL version="1.1.0"

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    DEBIAN_FRONTEND=noninteractive

# Variables de entorno para IA (valores por defecto)
ENV AI_ANALYSIS_ENABLED=True \
    GOOGLE_AI_MODEL=gemini-1.5-pro \
    MAX_CSV_SIZE_MB=10 \
    AI_ANALYSIS_TIMEOUT=300

# Crear usuario no-root para seguridad
RUN groupadd -r dashboard && \
    useradd -r -g dashboard -d /app -s /bin/bash dashboard

# Instalar dependencias del sistema necesarias para IA
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivo de requirements primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python incluyendo google-generativeai
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Verificar instalación de dependencias de IA
RUN python -c "import google.generativeai; print('✅ google-generativeai instalado correctamente')" || \
    (echo "❌ Error: google-generativeai no se instaló correctamente" && exit 1)

# Copiar archivos de la aplicación
COPY app.py .
COPY config.py .
COPY utils.py .
COPY templates/ templates/
COPY static/ static/

# Crear directorios necesarios
RUN mkdir -p data logs backups temp && \
    chown -R dashboard:dashboard /app

# Copiar scripts de inicio
COPY start_dashboard.sh .
RUN chmod +x start_dashboard.sh

# Script de healthcheck mejorado con verificación de IA
COPY <<EOF /app/healthcheck.py
#!/usr/bin/env python3
import requests
import sys
import os

def check_health():
    try:
        # Verificar endpoint principal
        response = requests.get('http://localhost:5000/health', timeout=10)
        if response.status_code != 200:
            print(f"❌ Health check falló: HTTP {response.status_code}")
            return False
        
        health_data = response.json()
        print(f"✅ Aplicación saludable (v{health_data.get('version', 'unknown')})")
        
        # Verificar estado de IA si está habilitado
        ai_enabled = health_data.get('ai_enabled', False)
        if ai_enabled:
            ai_response = requests.get('http://localhost:5000/api/ai/status', timeout=5)
            if ai_response.status_code == 200:
                ai_data = ai_response.json()
                if ai_data.get('service_available', False):
                    print("🤖 Servicio IA disponible")
                else:
                    print("⚠️  Servicio IA no disponible")
            else:
                print("⚠️  No se pudo verificar estado de IA")
        else:
            print("ℹ️  IA deshabilitada")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    if check_health():
        sys.exit(0)
    else:
        sys.exit(1)
EOF

RUN chmod +x /app/healthcheck.py

# Configurar healthcheck mejorado
HEALTHCHECK --interval=30s --timeout=15s --start-period=10s --retries=3 \
    CMD python /app/healthcheck.py

# Script de inicialización para verificar configuración de IA
COPY <<EOF /app/init_ai.py
#!/usr/bin/env python3
"""
Script de inicialización para verificar configuración de IA
"""
import os
import sys

def check_ai_config():
    """Verifica la configuración de IA al inicio del contenedor"""
    print("🔍 Verificando configuración de IA...")
    
    ai_enabled = os.getenv('AI_ANALYSIS_ENABLED', 'True').lower() == 'true'
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    
    if not ai_enabled:
        print("ℹ️  IA deshabilitada por configuración")
        return True
    
    if not api_key:
        print("⚠️  ADVERTENCIA: AI_ANALYSIS_ENABLED=True pero GOOGLE_AI_API_KEY no está configurada")
        print("   La funcionalidad de IA no estará disponible")
        print("   Para configurar: docker run -e GOOGLE_AI_API_KEY=tu-api-key ...")
        return True
    
    # Verificar que la API key no esté vacía o sea un placeholder
    if api_key in ['tu-api-key-aqui', 'your-api-key-here', '']:
        print("⚠️  ADVERTENCIA: GOOGLE_AI_API_KEY parece ser un placeholder")
        print("   Configura una API key válida de Google AI Studio")
        return True
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Intentar listar modelos para verificar conectividad
        models = list(genai.list_models())
        if models:
            print(f"✅ IA configurada correctamente ({len(models)} modelos disponibles)")
        else:
            print("⚠️  API key válida pero no se encontraron modelos")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Error verificando configuración de IA: {e}")
        print("   La aplicación continuará sin funcionalidad de IA")
        return True  # No fallar el inicio por problemas de IA

if __name__ == "__main__":
    check_ai_config()
EOF

RUN chmod +x /app/init_ai.py

# Cambiar a usuario no-root
USER dashboard

# Exponer puerto
EXPOSE 5000

# Configurar volúmenes para persistencia de datos
VOLUME ["/app/data", "/app/logs", "/app/backups"]

# Comando de inicio que incluye verificación de IA
CMD ["sh", "-c", "python /app/init_ai.py && python app.py"]

# --- Multi-stage build para producción ---
FROM python:3.12-slim as production

# Variables de entorno para producción
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    WEB_CONCURRENCY=4 \
    PORT=5000

# Variables de entorno para IA en producción
ENV AI_ANALYSIS_ENABLED=True \
    GOOGLE_AI_MODEL=gemini-1.5-pro \
    MAX_CSV_SIZE_MB=10 \
    AI_ANALYSIS_TIMEOUT=300

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    nginx \
    supervisor \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario
RUN groupadd -r dashboard && \
    useradd -r -g dashboard -d /app -s /bin/bash dashboard

WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Verificar instalación de IA
RUN python -c "import google.generativeai; print('✅ IA dependencies installed')"

# Copiar aplicación
COPY . .

# Configuración de Nginx actualizada
COPY <<EOF /etc/nginx/sites-available/dashboard
server {
    listen 80;
    server_name _;
    
    client_max_body_size 100M;
    
    # Timeout aumentado para análisis de IA
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Endpoint específico para análisis IA con timeout extendido
    location /api/ai/analyze {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
    
    location /static {
        alias /app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:5000;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
EOF

# Habilitar sitio de Nginx
RUN ln -s /etc/nginx/sites-available/dashboard /etc/nginx/sites-enabled/ && \
    rm -f /etc/nginx/sites-enabled/default

# Configuración de Supervisor actualizada
COPY <<EOF /etc/supervisor/conf.d/dashboard.conf
[supervisord]
nodaemon=true
user=root

[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
autostart=true
autorestart=true
stderr_logfile=/var/log/nginx/error.log
stdout_logfile=/var/log/nginx/access.log

[program:dashboard]
command=gunicorn --bind 127.0.0.1:5000 --workers 4 --timeout 600 --worker-class sync app:app
directory=/app
user=dashboard
autostart=true
autorestart=true
stderr_logfile=/app/logs/gunicorn.err.log
stdout_logfile=/app/logs/gunicorn.out.log
environment=PATH="/usr/local/bin",FLASK_ENV="production"
EOF

# Configuración de Gunicorn actualizada para IA
COPY <<EOF /app/gunicorn.conf.py
# Configuración de Gunicorn para Dashboard IT con IA
import os

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = int(os.environ.get('WEB_CONCURRENCY', 4))
worker_class = "sync"
worker_connections = 1000
timeout = 600  # Aumentado para análisis de IA
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 500  # Reducido debido a análisis de IA que puede usar más memoria
max_requests_jitter = 50

# Logging
accesslog = "/app/logs/gunicorn_access.log"
errorlog = "/app/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%h %l %u %t "%r" %s %b "%{Referer}i" "%{User-Agent}i" %D'

# Process naming
proc_name = "dashboard_bonsana_ai"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Preload app for better performance
preload_app = True

# Worker restart for memory management with AI analysis
max_worker_memory = 400000  # 400MB limit per worker
EOF

# Crear directorios y establecer permisos
RUN mkdir -p /app/logs /app/data /app/backups /var/log/nginx && \
    chown -R dashboard:dashboard /app && \
    chmod +x /app/start_dashboard.sh

# Healthcheck para producción con verificación de IA
HEALTHCHECK --interval=30s --timeout=15s --start-period=15s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Exponer puerto
EXPOSE 80

# Volúmenes
VOLUME ["/app/data", "/app/logs", "/app/backups"]

# Comando por defecto para producción con inicialización de IA
CMD ["sh", "-c", "python /app/init_ai.py && /usr/bin/supervisord -c /etc/supervisor/conf.d/dashboard.conf"]

# --- Etapa de desarrollo con IA ---
FROM python:3.12-slim as development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=development \
    FLASK_DEBUG=1

# Variables de entorno para IA en desarrollo
ENV AI_ANALYSIS_ENABLED=True \
    GOOGLE_AI_MODEL=gemini-1.5-pro \
    MAX_CSV_SIZE_MB=5 \
    AI_ANALYSIS_TIMEOUT=180

# Instalar dependencias adicionales para desarrollo
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    git \
    vim \
    htop \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias de desarrollo incluyendo IA
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
        pytest \
        pytest-cov \
        black \
        flake8 \
        ipython

# Verificar instalación de IA
RUN python -c "import google.generativeai; print('✅ AI dependencies ready for development')"

# Copiar todo el código fuente
COPY . .

# Crear directorios
RUN mkdir -p data logs backups temp

# Script de desarrollo con verificación de IA
COPY <<EOF /app/dev_init.py
#!/usr/bin/env python3
"""
Script de inicialización para desarrollo con IA
"""
import os

def init_dev_environment():
    print("🚀 Iniciando entorno de desarrollo con IA...")
    
    # Verificar configuración de IA
    if os.getenv('AI_ANALYSIS_ENABLED', 'True').lower() == 'true':
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        if api_key and api_key not in ['tu-api-key-aqui', 'your-api-key-here']:
            print("🤖 IA habilitada para desarrollo")
        else:
            print("⚠️  IA habilitada pero API Key no configurada")
            print("   Configura GOOGLE_AI_API_KEY para usar funcionalidad de IA")
    else:
        print("ℹ️  IA deshabilitada")
    
    print("✅ Entorno de desarrollo listo")

if __name__ == "__main__":
    init_dev_environment()
EOF

RUN chmod +x /app/dev_init.py

# Exponer puerto para desarrollo
EXPOSE 5000

# Comando para desarrollo con verificación de IA
CMD ["sh", "-c", "python /app/dev_init.py && python -m flask run --host=0.0.0.0 --port=5000 --reload"]

# --- Build arguments para diferentes configuraciones ---
ARG BUILD_TYPE=production
ARG AI_ENABLED=true
ARG GOOGLE_AI_MODEL=gemini-1.5-pro

# Aplicar configuración basada en argumentos
ENV BUILD_TYPE=${BUILD_TYPE}
ENV AI_ANALYSIS_ENABLED=${AI_ENABLED}
ENV GOOGLE_AI_MODEL=${GOOGLE_AI_MODEL}

# Metadata adicional
LABEL ai.enabled=${AI_ENABLED}
LABEL ai.model=${GOOGLE_AI_MODEL}
LABEL build.type=${BUILD_TYPE}