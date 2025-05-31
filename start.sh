#!/bin/bash
# Script de inicio para Dashboard IT - Clínica Bonsana

cd "$(dirname "$0")"

# Activar entorno virtual
source venv/bin/activate

# Verificar configuración
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('🔍 Verificando configuración...')
if not os.getenv('GOOGLE_AI_API_KEY'):
    print('⚠️  GOOGLE_AI_API_KEY no configurada')
    print('   Edita el archivo .env para agregar tu API Key')
else:
    print('✅ API Key configurada')

print('🚀 Iniciando Dashboard IT...')
"

# Iniciar aplicación
echo "Dashboard disponible en: http://localhost:5000"
python app.py
