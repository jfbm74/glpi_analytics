# Dockerfile para Dashboard IT - Clínica Bonsana
# Imagen base optimizada para aplicaciones Python
FROM python:3.11-slim-bullseye

# Información del mantenedor
LABEL maintainer="Clínica Bonsana IT Department"
LABEL description="Dashboard IT con Análisis de IA para Clínica Bonsana"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=America/Bogota

# Crear usuario no privilegiado
RUN groupadd -r dashboard && useradd --no-log-init -r -g dashboard dashboard

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    curl \
    wget \
    git \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Configurar timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Crear directorio de la aplicación
WORKDIR /app

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs data/cache data/reports data/backups data/metrics && \
    chown -R dashboard:dashboard /app

# Configurar permisos
RUN chmod +x start_server.sh 2>/dev/null || true && \
    chmod +x deploy.py 2>/dev/null || true && \
    chmod +x maintenance.py 2>/dev/null || true

# Cambiar a usuario no privilegiado
USER dashboard

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Exponer puerto
EXPOSE 5000

# Variables de entorno por defecto
ENV FLASK_ENV=production \
    HOST=0.0.0.0 \
    PORT=5000 \
    WORKERS=4

# Comando por defecto
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "300", "--keep-alive", "2", "--max-requests", "1000", "--max-requests-jitter", "50", "app:app"]