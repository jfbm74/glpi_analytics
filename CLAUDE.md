# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive IT Dashboard for Clínica Bonsana that combines traditional IT metrics analysis with advanced AI-powered insights. The system analyzes GLPI ticketing data and provides intelligent recommendations for IT operations in a healthcare environment.

### Core Architecture

- **Backend**: Flask application with modular design
- **AI Module**: Google Gemini 2.0 Flash integration for intelligent analysis
- **Data Layer**: CSV-based data ingestion from GLPI systems
- **Frontend**: Bootstrap 5 with Chart.js for visualizations
- **Infrastructure**: Docker-ready with Nginx, PostgreSQL, Redis support

## Key Commands

### Development

```bash
# Install dependencies and setup
python install_ai_module.py

# Start development server
python run_dashboard.py
# Alternative: python app.py

# Run tests
python test_ai.py
python test_dashboard.py
python test_api_routes.py
python test_google_ai.py
```

### Docker Deployment

```bash
# Development
docker-compose up -d

# Production with monitoring
docker-compose --profile monitoring up -d

# Backup
docker-compose --profile backup run backup
```

### Environment Setup

```bash
# Setup complete environment
python install.py

# AI module specific setup
python setup_ai.py
python install_ai_module.py
```

## Architecture Overview

### Main Application Structure

- **`app.py`**: Main Flask application factory with all routes and business logic
- **`ai_routes.py`**: Flask blueprint for AI-specific endpoints (`/api/ai/*`)
- **`run_dashboard.py`**: Development server launcher
- **`utils.py`**: Utility functions for data validation and CSV operations

### AI Module (`ai/` directory)

- **`analyzer.py`**: Main AI analyzer class that orchestrates analysis
- **`gemini_client.py`**: Google Gemini API client wrapper
- **`prompts.py`**: Prompt templates for different analysis types
- **`export.py`**: Report generation and export functionality
- **`monitoring.py`**: AI system monitoring and metrics
- **`config.py`**: AI module configuration

### Analysis Types Available

1. **Comprehensive Analysis**: Complete IT department strategic evaluation
2. **Quick KPI Analysis**: Immediate insights on key metrics
3. **Technician Analysis**: Individual performance evaluation
4. **SLA Analysis**: Service level agreement compliance
5. **Trend Analysis**: Temporal patterns and predictions
6. **Cost Optimization**: Efficiency and ROI analysis

## Data Structure

### Input Data

The system expects GLPI CSV exports with Spanish column names:
- **Ticket ID**, **Estado** (Status), **Tipo** (Type)
- **Asignado a: - Técnico** (Assigned Technician)
- **Prioridad** (Priority), **Categoría** (Category)
- **Solicitante - Solicitante** (Requester)
- **Fecha de Apertura** (Open Date), **Fecha de solución** (Solution Date)
- **Se superó el tiempo de resolución** (SLA Exceeded)
- **Encuesta de satisfacción - Satisfacción** (CSAT Score)

### Key Classes

- **`TicketAnalyzer`**: Core data analysis class in `app.py`
- **`AIAnalyzer`**: AI-powered analysis orchestrator in `ai/analyzer.py`
- **`GeminiClient`**: Google AI API interface in `ai/gemini_client.py`

## API Endpoints

### Dashboard APIs (`/api/`)

- `GET /api/metrics` - Overall dashboard metrics
- `GET /api/distributions` - Ticket distributions by type/status/priority
- `GET /api/technicians` - Technician workload data
- `GET /api/sla` - SLA compliance analysis
- `GET /api/csat` - Customer satisfaction metrics

### AI APIs (`/api/ai/`)

- `POST /api/ai/analyze` - Run AI analysis
- `GET /api/ai/test-connection` - Test AI connectivity
- `GET /api/ai/history` - Analysis history
- `POST /api/ai/custom-analysis` - Custom analysis with specific focus

## Configuration

### Environment Variables

Required:
- `GOOGLE_AI_API_KEY` - Google Gemini API key

Optional:
- `FLASK_ENV` - Environment (development/production)
- `DATA_DIRECTORY` - Data files location (default: "data")
- `HOST` - Server host (default: "0.0.0.0")
- `PORT` - Server port (default: 5000)
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

### File Structure

```
data/
├── glpi.csv              # Input data file
├── cache/                # Analysis cache
├── reports/              # Generated reports
├── backups/              # Data backups
└── metrics/              # System metrics

templates/
├── index.html            # Main dashboard
├── ai_analysis.html      # AI analysis interface
├── ai_dashboard.html     # AI monitoring
└── error.html            # Error pages
```

## Development Guidelines

### Error Handling

The system uses comprehensive error handling with logging. Key areas:
- CSV data loading and validation in `TicketAnalyzer._load_data()`
- AI API calls in `GeminiClient.analyze_with_ai()`
- Route handlers return appropriate HTTP status codes

### Data Validation

- Missing technician assignments are handled as "SIN ASIGNAR"
- CSV structure validation via `validate_csv_structure()` in `utils.py`
- Data quality insights available via `/api/validation`

### Testing

Individual test files for each component:
- `test_ai.py` - AI connectivity and analysis
- `test_dashboard.py` - Dashboard functionality
- `test_api_routes.py` - API endpoint validation
- `test_google_ai.py` - Google AI integration

### Deployment Notes

- Production uses Gunicorn with Nginx reverse proxy
- Docker Compose includes PostgreSQL, Redis, and monitoring stack
- Health checks available at `/health` endpoint
- SSL/TLS configuration in `nginx/` directory

## Healthcare Context

This system is specifically designed for healthcare IT operations:
- SLA compliance is critical for patient care continuity
- Technician analysis considers medical equipment specialization
- Priority handling reflects healthcare urgency levels
- CSAT scores relate to medical staff satisfaction with IT services

## Troubleshooting

### Common Issues

1. **AI Analysis Fails**: Check `GOOGLE_AI_API_KEY` configuration
2. **CSV Loading Errors**: Verify file encoding (UTF-8) and delimiter (semicolon)
3. **Missing Data**: Check column name mappings in `TicketAnalyzer` methods
4. **Performance Issues**: Enable Redis caching for better response times

### Debug Mode

Enable debug logging by setting `FLASK_ENV=development` and `LOG_LEVEL=DEBUG`