# 🚀 Guía de Despliegue - Dashboard IT Clínica Bonsana

Esta guía proporciona instrucciones detalladas para desplegar el Dashboard IT en diferentes entornos.

## 📋 Prerrequisitos

### Software Requerido
- Python 3.8+ (recomendado: 3.12)
- Git
- Docker y Docker Compose (para despliegue containerizado)

### Hardware Mínimo
- **Desarrollo**: 2GB RAM, 1 CPU, 10GB espacio
- **Producción**: 4GB RAM, 2 CPU, 50GB espacio
- **Alta disponibilidad**: 8GB RAM, 4 CPU, 100GB espacio

## 🔧 Métodos de Despliegue

### 1. Instalación Local (Desarrollo/Testing)

#### Instalación Automática
```bash
# Clonar el repositorio
git clone <repository-url>
cd dashboard-clinica-bonsana

# Ejecutar script de instalación
python setup.py

# Iniciar la aplicación
python app.py
```

#### Instalación Manual
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Crear directorios necesarios
mkdir -p data logs backups

# Configurar datos de ejemplo (opcional)
python utils.py generate-sample data/glpi.csv --records 100

# Iniciar aplicación
python app.py
```

### 2. Despliegue con Docker

#### Desarrollo Rápido
```bash
# Construir y ejecutar contenedor de desarrollo
docker-compose --profile dev up -d dashboard_dev

# Acceder a la aplicación
open http://localhost:5000
```

#### Producción Básica
```bash
# Crear archivo de variables de entorno
cp .env.example .env
# Editar .env con valores de producción

# Desplegar servicios básicos
docker-compose up -d dashboard nginx redis

# Verificar estado
docker-compose ps
docker-compose logs dashboard
```

#### Producción Completa con Monitoreo
```bash
# Desplegar todos los servicios
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verificar servicios
docker-compose ps

# Acceder a los servicios:
# - Dashboard: http://localhost:8080
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
```

### 3. Despliegue en Servidor Linux

#### Ubuntu/Debian
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3.12 python3.12-venv python3-pip nginx git

# Crear usuario para la aplicación
sudo useradd -m -s /bin/bash dashboard
sudo usermod -aG www-data dashboard

# Cambiar al usuario dashboard
sudo su - dashboard

# Clonar y configurar aplicación
git clone <repository-url> /home/dashboard/app
cd /home/dashboard/app
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Crear servicio systemd
sudo tee /etc/systemd/system/dashboard-bonsana.service > /dev/null <<EOF
[Unit]
Description=Dashboard IT Clínica Bonsana
After=network.target

[Service]
User=dashboard
Group=www-data
WorkingDirectory=/home/dashboard/app
Environment=PATH=/home/dashboard/app/venv/bin
ExecStart=/home/dashboard/app/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Habilitar e iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable dashboard-bonsana
sudo systemctl start dashboard-bonsana

# Configurar Nginx
sudo tee /etc/nginx/sites-available/dashboard-bonsana > /dev/null <<EOF
server {
    listen 80;
    server_name dashboard.clinicabonsana.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /home/dashboard/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/dashboard-bonsana /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### CentOS/RHEL
```bash
# Instalar dependencias
sudo yum update -y
sudo yum install -y python3 python3-pip nginx git

# Seguir pasos similares adaptando comandos para CentOS
```

### 4. Despliegue en la Nube

#### AWS EC2
```bash
# Lanzar instancia EC2 (t3.medium recomendado)
# Ubuntu 22.04 LTS AMI

# Conectar via SSH
ssh -i key.pem ubuntu@<instance-ip>

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Desplegar aplicación
git clone <repository-url>
cd dashboard-clinica-bonsana
cp .env.example .env
# Editar .env con configuración de producción
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Configurar Security Groups para puertos 80, 443
```

#### Azure Container Instances
```bash
# Crear grupo de recursos
az group create --name dashboard-rg --location eastus

# Crear registro de contenedores
az acr create --resource-group dashboard-rg --name dashboardacr --sku Basic

# Construir y pushear imagen
az acr build --registry dashboardacr --image dashboard:latest .

# Desplegar container instance
az container create \
  --resource-group dashboard-rg \
  --name dashboard-container \
  --image dashboardacr.azurecr.io/dashboard:latest \
  --cpu 2 --memory 4 \
  --ports 80 \
  --environment-variables FLASK_ENV=production
```

#### Google Cloud Run
```bash
# Configurar proyecto
gcloud config set project YOUR_PROJECT_ID

# Construir imagen
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/dashboard

# Desplegar en Cloud Run
gcloud run deploy dashboard \
  --image gcr.io/YOUR_PROJECT_ID/dashboard \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

## 🔐 Configuración de Seguridad

### SSL/TLS (HTTPS)
```bash
# Obtener certificado con Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d dashboard.clinicabonsana.com

# Configurar renovación automática
sudo crontab -e
# Agregar: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Firewall
```bash
# Ubuntu UFW
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# CentOS firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### Variables de Entorno Seguras
```bash
# Crear archivo .env con valores seguros
cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
POSTGRES_PASSWORD=$(openssl rand -base64 32)
GRAFANA_PASSWORD=$(openssl rand -base64 16)
EOF

# Establecer permisos restrictivos
chmod 600 .env
chown dashboard:dashboard .env
```

## 📊 Monitoreo y Mantenimiento

### Health Checks
```bash
# Verificar estado de la aplicación
curl -f http://localhost:5000/api/metrics

# Con Docker
docker-compose exec dashboard python healthcheck.py
```

### Logs
```bash
# Ver logs en tiempo real
tail -f logs/dashboard.log

# Con Docker
docker-compose logs -f dashboard

# Con systemd
sudo journalctl -u dashboard-bonsana -f
```

### Backup Automático
```bash
# Crear script de backup
cat > /home/dashboard/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/dashboard/backups"
DATA_DIR="/home/dashboard/app/data"

# Crear backup
tar -czf "$BACKUP_DIR/data_backup_$DATE.tar.gz" -C "$DATA_DIR" .

# Limpiar backups antiguos (mantener 30 días)
find "$BACKUP_DIR" -name "data_backup_*.tar.gz" -mtime +30 -delete

echo "Backup completado: data_backup_$DATE.tar.gz"
EOF

chmod +x /home/dashboard/backup.sh

# Programar backup diario
crontab -e
# Agregar: 0 2 * * * /home/dashboard/backup.sh
```

### Actualizaciones
```bash
# Actualización con downtime mínimo
git pull origin main
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar servicio
sudo systemctl restart dashboard-bonsana

# Con Docker (rolling update)
docker-compose pull dashboard
docker-compose up -d dashboard
```

## 🔧 Resolución de Problemas

### Problemas Comunes

#### Error: "No se encontraron archivos CSV"
```bash
# Verificar permisos
ls -la data/
chmod 644 data/glpi.csv
chown dashboard:dashboard data/glpi.csv
```

#### Error: "Puerto 5000 en uso"
```bash
# Encontrar proceso usando el puerto
sudo lsof -i :5000
sudo kill -9 <PID>

# O cambiar puerto en config
export PORT=8000
```

#### Error de memoria insuficiente
```bash
# Aumentar memoria para Docker
# En docker-compose.yml:
services:
  dashboard:
    deploy:
      resources:
        limits:
          memory: 2G
```

#### Base de datos PostgreSQL no conecta
```bash
# Verificar estado del contenedor
docker-compose ps postgres

# Ver logs
docker-compose logs postgres

# Reiniciar servicio
docker-compose restart postgres
```

### Comandos de Diagnóstico
```bash
# Verificar servicios
systemctl status dashboard-bonsana
systemctl status nginx

# Verificar puertos
netstat -tlnp | grep :5000
netstat -tlnp | grep :80

# Verificar espacio en disco
df -h
du -sh data/ logs/ backups/

# Verificar memoria
free -h
htop

# Verificar conectividad
curl -I http://localhost:5000
ping dashboard.clinicabonsana.com
```

## 📈 Escalabilidad

### Load Balancing
```bash
# Múltiples instancias con Nginx
upstream dashboard_backend {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    location / {
        proxy_pass http://dashboard_backend;
    }
}
```

### Base de Datos Distribuida
```yaml
# docker-compose.yml para PostgreSQL con replica
services:
  postgres_master:
    image: postgres:15
    environment:
      POSTGRES_REPLICATION_MODE: master
      POSTGRES_REPLICATION_USER: replicator
      POSTGRES_REPLICATION_PASSWORD: replication_password
  
  postgres_slave:
    image: postgres:15
    environment:
      POSTGRES_REPLICATION_MODE: slave
      POSTGRES_MASTER_HOST: postgres_master
```

### Cache Distribuido
```yaml
# Redis Cluster
services:
  redis_1:
    image: redis:7-alpine
    command: redis-server --port 7001 --cluster-enabled yes
  
  redis_2:
    image: redis:7-alpine
    command: redis-server --port 7002 --cluster-enabled yes
```

## 📞 Soporte

### Contactos de Emergencia
- **IT Manager**: it-manager@clinicabonsana.com
- **DevOps Team**: devops@clinicabonsana.com
- **On-call**: +57 xxx xxx xxxx

### Documentación Adicional
- [README.md](README.md): Información general del proyecto
- [API Documentation](API.md): Documentación de endpoints
- [User Manual](USER_MANUAL.md): Manual de usuario

### Métricas de SLA
- **Uptime**: 99.9%
- **Response Time**: < 2 segundos
- **Recovery Time**: < 15 minutos

---

**Dashboard IT - Clínica Bonsana v1.0.0**  
*Desarrollado con ❤️ por el equipo de IT*