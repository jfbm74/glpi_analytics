# Guía de Configuración Completa
## Dashboard IT con IA - Clínica Bonsana

Esta es la guía definitiva para implementar el sistema completo de Dashboard IT con análisis de IA para Clínica Bonsana.

## 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación Automática](#instalación-automática)
3. [Instalación Manual](#instalación-manual)
4. [Configuración de Entornos](#configuración-de-entornos)
5. [Deployment con Docker](#deployment-con-docker)
6. [Configuración de Producción](#configuración-de-producción)
7. [Verificación y Tests](#verificación-y-tests)
8. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
9. [Troubleshooting](#troubleshooting)
10. [Próximos Pasos](#próximos-pasos)

## 🖥️ Requisitos del Sistema

### Mínimos
- **OS**: Ubuntu 20.04+, CentOS 8+, Windows 10+, macOS 11+
- **Python**: 3.8 o superior
- **RAM**: 4 GB mínimo
- **Disco**: 10 GB espacio libre
- **Red**: Conexión a internet para API de Google AI

### Recomendados para Producción
- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.11+
- **RAM**: 16 GB
- **Disco**: 50 GB SSD
- **CPU**: 4 cores
- **Red**: Conexión estable 100 Mbps

### Dependencias del Sistema
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl wget nginx postgresql redis-server

# CentOS/RHEL
sudo yum install -y python3 python3-pip git curl wget nginx postgresql redis

# macOS (con Homebrew)
brew install python@3.11 git nginx postgresql redis
```

## 🚀 Instalación Automática

### Opción 1: Instalador Completo

```bash
# Descargar e instalar automáticamente
curl -fsSL https://github.com/clinica-bonsana/dashboard-it/install.sh | bash

# O manualmente:
git clone https://github.com/clinica-bonsana/dashboard-it.git
cd dashboard-it
python3 install_ai_module.py
```

### Opción 2: Con Docker (Recomendado)

```bash
# Clonar repositorio
git clone https://github.com/clinica-bonsana/dashboard-it.git
cd dashboard-it

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu API key de Google AI

# Levantar todos los servicios
docker-compose up -d

# Verificar que todo esté funcionando
docker-compose ps
```

## 🔧 Instalación Manual

### Paso 1: Preparar Entorno

```bash
# Crear directorio del proyecto
mkdir dashboard-it-bonsana
cd dashboard-it-bonsana

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Actualizar pip
pip install --upgrade pip setuptools wheel
```

### Paso 2: Instalar Dependencias

```bash
# Crear requirements.txt
cat > requirements.txt << 'EOF'
# Dashboard IT - Clínica Bonsana
Flask>=2.3.0
pandas>=2.0.0
python-dotenv>=1.0.0
google-generativeai>=0.3.0
markdown>=3.5.0
beautifulsoup4>=4.12.0
requests>=2.31.0
jinja2>=3.1.0
werkzeug>=2.3.0
psutil>=5.9.0
gunicorn>=20.1.0
reportlab>=4.0.0
python-docx>=0.8.11
redis>=4.5.0
EOF

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements_ai.txt
```

### Paso 3: Crear Estructura de Archivos

```bash
# Crear estructura de directorios
mkdir -p {ai,data/{cache,reports,backups,metrics},logs,templates,static,nginx,scripts}

# Crear archivos principales usando los artifacts proporcionados
# (Copiar contenido de los artifacts anteriores)
```

### Paso 4: Configuración Inicial

```bash
# Crear archivo .env
cat > .env << 'EOF'
# Configuración Dashboard IT - Clínica Bonsana
FLASK_ENV=development
SECRET_KEY=change-this-secret-key-in-production

# Google AI Configuration
GOOGLE_AI_API_KEY=AIzaSyALkC-uoOfpS3cB-vnaj8Zor3ccp5MVOBQ
GOOGLE_AI_MODEL=gemini-2.0-flash-exp
AI_ANALYSIS_ENABLED=True

# Database
DATABASE_URL=sqlite:///dashboard.db

# Application Settings
DATA_DIRECTORY=data
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=5000

# IA Settings
AI_MAX_CSV_ROWS=1000
AI_CACHE_TIMEOUT=3600
AI_REQUEST_TIMEOUT=300
EOF

# Configurar permisos
chmod 600 .env
```

## 🌍 Configuración de Entornos

### Desarrollo Local

```bash
# Configurar para desarrollo
python deploy.py development

# Iniciar aplicación
python app.py
# O usar Flask directamente
flask run --host=0.0.0.0 --port=5000 --debug
```

### Staging

```bash
# Configurar para staging
python deploy.py staging

# Usar Gunicorn
gunicorn --config gunicorn.conf.py app:app
```

### Producción

```bash
# Configurar para producción
python deploy.py production --force

# Configurar systemd service
sudo cat > /etc/systemd/system/dashboard-bonsana.service << 'EOF'
[Unit]
Description=Dashboard IT Clínica Bonsana
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/dashboard-it
Environment=PATH=/var/www/dashboard-it/venv/bin
ExecStart=/var/www/dashboard-it/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
EOF

# Habilitar y iniciar servicio
sudo systemctl enable dashboard-bonsana
sudo systemctl start dashboard-bonsana
sudo systemctl status dashboard-bonsana
```

## 🐳 Deployment con Docker

### Configuración Básica

```bash
# Crear archivo docker-compose.override.yml para desarrollo
cat > docker-compose.override.yml << 'EOF'
version: '3.8'
services:
  dashboard:
    volumes:
      - .:/app
    environment:
      - FLASK_ENV=development
      - DEBUG=true
    ports:
      - "5000:5000"
    command: python app.py
EOF

# Desarrollo
docker-compose up

# Producción
docker-compose -f docker-compose.yml up -d
```

### Configuración Avanzada con Orquestador

```bash
# Para Kubernetes
kubectl apply -f k8s/

# Para Docker Swarm
docker stack deploy -c docker-compose.prod.yml dashboard-bonsana
```

## 🔒 Configuración de Producción

### 1. Nginx como Reverse Proxy

```bash
# Copiar configuración de nginx
sudo cp nginx/nginx.conf /etc/nginx/nginx.conf
sudo cp nginx/sites-available/dashboard-bonsana /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/dashboard-bonsana /etc/nginx/sites-enabled/

# Probar configuración
sudo nginx -t

# Recargar nginx
sudo systemctl reload nginx
```

### 2. SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d dashboard.clinicabonsana.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

### 3. Configuración de Base de Datos

```bash
# PostgreSQL para producción
sudo -u postgres createdb dashboard_bonsana
sudo -u postgres createuser dashboard_user
sudo -u postgres psql -c "ALTER USER dashboard_user PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dashboard_bonsana TO dashboard_user;"

# Actualizar .env
echo "DATABASE_URL=postgresql://dashboard_user:secure_password@localhost/dashboard_bonsana" >> .env
```

### 4. Redis para Cache

```bash
# Configurar Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Configurar autenticación
echo "requirepass secure_redis_password" | sudo tee -a /etc/redis/redis.conf
sudo systemctl restart redis-server

# Actualizar .env
echo "REDIS_URL=redis://:secure_redis_password@localhost:6379/0" >> .env
```

### 5. Firewall y Seguridad

```bash
# Configurar UFW
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Configurar fail2ban
sudo apt install fail2ban
sudo cp scripts/jail.local /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## ✅ Verificación y Tests

### Tests Automáticos

```bash
# Ejecutar suite completa de tests
python test_ai.py

# Tests específicos
python -m pytest tests/ -v

# Tests de integración
python scripts/integration_tests.py

# Tests de carga
python scripts/load_tests.py
```

### Verificación Manual

```bash
# Verificar endpoints principales
curl -f http://localhost:5000/health
curl -f http://localhost:5000/
curl -f http://localhost:5000/ai-analysis

# Verificar API de IA
curl -X POST http://localhost:5000/ai/api/ai/test-connection

# Verificar métricas
curl http://localhost:5000/api/metrics
```

### Monitoreo de Logs

```bash
# Logs de la aplicación
tail -f logs/dashboard.log

# Logs de Gunicorn
tail -f logs/gunicorn_error.log

# Logs de sistema
sudo journalctl -u dashboard-bonsana -f

# Logs de nginx
sudo tail -f /var/log/nginx/access.log
```

## 📊 Monitoreo y Mantenimiento

### Configurar Monitoreo

```bash
# Prometheus y Grafana (con Docker)
docker-compose --profile monitoring up -d

# Acceder a Grafana: http://localhost:3000
# Usuario: admin, Contraseña: admin_password_change_this
```

### Scripts de Mantenimiento

```bash
# Ejecutar mantenimiento diario
python maintenance.py --full

# Backup automático
python backup.py

# Limpiar cache y logs antiguos
python maintenance.py --cleanup

# Verificar salud del sistema
python scripts/health_check.py
```

### Cron Jobs

```bash
# Configurar tareas automáticas
crontab -e

# Agregar estas líneas:
# Backup diario a las 2 AM
0 2 * * * /path/to/dashboard-it/venv/bin/python /path/to/dashboard-it/backup.py

# Mantenimiento semanal los domingos a las 3 AM
0 3 * * 0 /path/to/dashboard-it/venv/bin/python /path/to/dashboard-it/maintenance.py --full

# Verificación de salud cada 5 minutos
*/5 * * * * /path/to/dashboard-it/venv/bin/python /path/to/dashboard-it/scripts/health_check.py
```

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Error de API Key de Google AI

```bash
# Verificar API key
python -c "
import google.generativeai as genai
genai.configure(api_key='TU_API_KEY')
try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content('Test')
    print('✅ API Key válida')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

#### 2. Problemas de Memoria

```bash
# Verificar uso de memoria
free -h
ps aux | grep python | head -10

# Configurar swap si es necesario
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 3. Base de Datos Bloqueada (SQLite)

```bash
# Verificar procesos que usan la DB
lsof data/dashboard.db

# Reiniciar aplicación si es necesario
sudo systemctl restart dashboard-bonsana
```

#### 4. Nginx 502 Bad Gateway

```bash
# Verificar que Gunicorn esté corriendo
sudo systemctl status dashboard-bonsana

# Verificar logs
sudo journalctl -u dashboard-bonsana -n 50

# Reiniciar servicios
sudo systemctl restart dashboard-bonsana
sudo systemctl restart nginx
```

### Logs de Diagnóstico

```bash
# Generar reporte de diagnóstico completo
python scripts/diagnostic.py > diagnostic_report.txt

# El reporte incluye:
# - Estado de servicios
# - Uso de recursos
# - Logs recientes
# - Configuración actual
# - Tests básicos
```

### Comandos de Emergencia

```bash
# Parar todos los servicios
sudo systemctl stop dashboard-bonsana nginx postgresql redis-server

# Restaurar desde backup
python scripts/restore_backup.py --backup-file data/backups/latest.tar.gz

# Reiniciar sistema completo
sudo systemctl start postgresql redis-server
sudo systemctl start dashboard-bonsana
sudo systemctl start nginx
```

## 🚀 Próximos Pasos

### Después de la Instalación

1. **Configurar Datos Reales**:
   ```bash
   # Reemplazar datos de muestra con datos reales de GLPI
   cp /path/to/real/glpi_export.csv data/glpi.csv
   ```

2. **Personalizar Análisis**:
   - Editar `ai/prompts.py` para adaptar prompts a necesidades específicas
   - Configurar tipos de análisis personalizados

3. **Configurar Alertas**:
   ```bash
   # Configurar notificaciones por email/Slack
   pip install flask-mail slack-webhook
   # Editar scripts/alerts.py
   ```

4. **Integración con GLPI**:
   ```bash
   # Configurar sincronización automática
   # Editar scripts/glpi_sync.py
   ```

### Mejoras Futuras

- **Dashboard en tiempo real** con WebSockets
- **Análisis predictivo** con Machine Learning
- **Integración con sistemas externos** (Active Directory, etc.)
- **Mobile app** para análisis móvil
- **Multi-tenant** para múltiples clínicas

### Capacitación del Equipo

1. **Documentación de Usuario**: Crear guías para usuarios finales
2. **Training Sessions**: Organizar sesiones de capacitación
3. **Videos Tutoriales**: Crear contenido audiovisual
4. **Manuales de Procedimientos**: Documentar workflows

## 📞 Soporte

### Recursos de Ayuda

- **Documentación Técnica**: `docs/`
- **API Documentation**: `API_DOCUMENTATION.md`
- **Troubleshooting Guide**: `TROUBLESHOOTING.md`
- **FAQ**: `FAQ.md`

### Contacto

- **Email Técnico**: it-support@clinicabonsana.com
- **Slack**: #dashboard-it-support
- **Issues**: GitHub Issues en el repositorio
- **Emergencias**: +57 (2) 555-0123

### Contribuciones

Si deseas contribuir al proyecto:

1. Fork el repositorio
2. Crear branch para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

---

## 🎉 ¡Felicidades!

Tu sistema Dashboard IT con IA para Clínica Bonsana está ahora completamente configurado y listo para usar. El sistema incluye:

✅ **Dashboard completo** con métricas en tiempo real  
✅ **Análisis de IA avanzado** con 6 tipos diferentes  
✅ **Sistema de monitoreo** y alertas  
✅ **Exportación de reportes** en múltiples formatos  
✅ **API REST completa** para integraciones  
✅ **Deployment de producción** con Docker y nginx  
✅ **Sistema de backups** automático  
✅ **Documentación completa** y soporte  

**¡El futuro del análisis IT en sector salud está aquí! 🏥🤖**