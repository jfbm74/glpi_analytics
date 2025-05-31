@echo off
echo 🏥 Dashboard IT - Clínica Bonsana
echo Iniciando aplicación...

cd /d "%~dp0"

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Verificar configuración
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('⚠️  Configura GOOGLE_AI_API_KEY en .env' if not os.getenv('GOOGLE_AI_API_KEY') else '✅ Configuración OK')"

REM Iniciar aplicación
echo Dashboard disponible en: http://localhost:5000
python app.py

pause
