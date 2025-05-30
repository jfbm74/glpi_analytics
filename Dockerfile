# Dashboard IT - Clínica Bonsana
# Dockerfile para containerización de la aplicación

# Usar imagen base oficial de Python 3.12
FROM python:3.12-slim

# Información del mantenedor
LABEL maintainer="IT Team - Clínica Bonsana"
LABEL description="Dashboard de análisis de tickets IT para Clínica Bonsana"
LABEL version="1.0.0"

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    DEBIAN_FRONTEND=noninteractive

# Crear usuario no-root para seguridad
RUN groupadd -r dashboard && \
    useradd -r -g dashboard -d /app -s /bin/bash dashboard

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivo de requirements primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

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

# Script de healthcheck
COPY <<EOF /app/healthcheck.py
#!/usr/bin/env python3
import requests
import sys

try:
    response = requests.get('http://localhost:5000/api/metrics', timeout=10)
    if response.status_code == 200:
        print("✅ Aplicación saludable")
        sys.exit(0)
    else:
        print(f"❌ Error HTTP: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    sys.exit(1)
EOF

RUN chmod +x /app/healthcheck.py

# Configurar healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python /app/healthcheck.py

# Cambiar a usuario no-root
USER dashboard

# Exponer puerto
EXPOSE 5000

# Configurar volúmenes para persistencia de datos
VOLUME ["/app/data", "/app/logs", "/app/backups"]

# Comando por defecto
CMD ["python", "app.py"]

# --- Multi-stage build para producción ---
FROM python:3.12-slim as production

# Variables de entorno para producción
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    WEB_CONCURRENCY=4 \
    PORT=5000

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    nginx \
    supervisor \
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

# Copiar aplicación
COPY . .

# Configuración de Nginx
COPY <<EOF /etc/nginx/sites-available/dashboard
server {
    listen 80;
    server_name _;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    location /static {
        alias /app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Habilitar sitio de Nginx
RUN ln -s /etc/nginx/sites-available/dashboard /etc/nginx/sites-enabled/ && \
    rm -f /etc/nginx/sites-enabled/default

# Configuración de Supervisor
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
command=gunicorn --bind 127.0.0.1:5000 --workers 4 --timeout 300 app:app
directory=/app
user=dashboard
autostart=true
autorestart=true
stderr_logfile=/app/logs/gunicorn.err.log
stdout_logfile=/app/logs/gunicorn.out.log
environment=PATH="/usr/local/bin",FLASK_ENV="production"
EOF

# Configuración de Gunicorn
COPY <<EOF /app/gunicorn.conf.py
# Configuración de Gunicorn para Dashboard IT
import os

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = int(os.environ.get('WEB_CONCURRENCY', 4))
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/app/logs/gunicorn_access.log"
errorlog = "/app/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%h %l %u %t "%r" %s %b "%{Referer}i" "%{User-Agent}i" %D'

# Process naming
proc_name = "dashboard_bonsana"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Preload app for better performance
preload_app = True
EOF

# Crear directorios y establecer permisos
RUN mkdir -p /app/logs /app/data /app/backups /var/log/nginx && \
    chown -R dashboard:dashboard /app && \
    chmod +x /app/start_dashboard.sh

# Healthcheck para producción
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Exponer puerto
EXPOSE 80

# Volúmenes
VOLUME ["/app/data", "/app/logs", "/app/backups"]

# Comando por defecto para producción
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/dashboard.conf"]

# --- Etapa de desarrollo ---
FROM python:3.12-slim as development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=development \
    FLASK_DEBUG=1

# Instalar dependencias adicionales para desarrollo
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias de desarrollo
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
        pytest \
        pytest-cov \
        black \
        flake8 \
        ipython

# Copiar todo el código fuente
COPY . .

# Crear directorios
RUN mkdir -p data logs backups temp

# Exponer puerto para desarrollo
EXPOSE 5000

# Comando para desarrollo (con recarga automática)
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]