# FastAPI Scraper

A robust FastAPI server for web scraping using FireCrawl with best practices, following clean architecture principles and comprehensive error handling.

## Features

- 🚀 **FastAPI** with async/await support
- 🔥 **FireCrawl** integration for reliable web scraping
- 📊 **Comprehensive API** with scraping, crawling, and search capabilities
- 🛡️ **Robust error handling** with custom exceptions
- 📝 **Request/Response validation** using Pydantic models
- 🏗️ **Clean architecture** with separation of concerns
- 📋 **Health checks** and monitoring endpoints
- 🔒 **Security** middleware and CORS configuration
- 📖 **Auto-generated documentation** with OpenAPI/Swagger
- 🧪 **Structured logging** with correlation IDs

## Architecture

This project follows FastAPI best practices and clean architecture principles:

```
fastapi_scraper/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main FastAPI application
│   ├── config.py            # Application configuration
│   ├── models.py            # Pydantic models
│   ├── exceptions.py        # Custom exceptions
│   ├── dependencies.py      # Dependency injection
│   ├── routers/            # API route handlers
│   │   ├── __init__.py
│   │   ├── scraping.py     # Scraping endpoints
│   │   └── health.py       # Health check endpoints
│   └── services/           # Business logic layer
│       ├── __init__.py
│       └── firecrawl_service.py
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites

- Python 3.8+
- FireCrawl API key (get one at [firecrawl.dev](https://firecrawl.dev))

### Setup

1. **Clone or create the project structure**:
```bash
mkdir fastapi_scraper
cd fastapi_scraper
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Create environment file**:
```bash
# Create .env file with your configuration
cat > .env << EOF
# FireCrawl Configuration
SCRAPER_FIRECRAWL_API_KEY=your_firecrawl_api_key_here
SCRAPER_FIRECRAWL_BASE_URL=https://api.firecrawl.dev

# Application Settings
SCRAPER_APP_NAME=FastAPI Scraper
SCRAPER_APP_VERSION=1.0.0
SCRAPER_DEBUG=true

# Server Settings
SCRAPER_HOST=127.0.0.1
SCRAPER_PORT=8000

# API Settings
SCRAPER_API_PREFIX=/api/v1

# Rate Limiting
SCRAPER_RATE_LIMIT_REQUESTS=100
SCRAPER_RATE_LIMIT_WINDOW=60

# CORS Settings
SCRAPER_CORS_ORIGINS=*
SCRAPER_CORS_METHODS=GET,POST,PUT,DELETE
SCRAPER_CORS_HEADERS=*

# Logging
SCRAPER_LOG_LEVEL=INFO

# Job Settings
SCRAPER_JOB_TIMEOUT=300
SCRAPER_MAX_CONCURRENT_JOBS=10

# Storage Settings
SCRAPER_STORAGE_PATH=./storage
EOF
```

5. **Replace `your_firecrawl_api_key_here` with your actual FireCrawl API key**

## Usage

### Running the Server

```bash
# Development mode with auto-reload
python -m src.main

# Or using uvicorn directly
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Health Checks

- `GET /api/v1/health` - Complete health check
- `GET /api/v1/health/ready` - Readiness check
- `GET /api/v1/health/live` - Liveness check

### Scraping Operations

#### Single URL Scraping
```bash
POST /api/v1/scraping/scrape
Content-Type: application/json

{
  "url": "https://example.com",
  "formats": ["markdown", "html"],
  "only_main_content": true,
  "timeout": 30000
}
```

#### Batch Scraping
```bash
# Start batch job
POST /api/v1/scraping/batch-scrape
Content-Type: application/json

{
  "urls": [
    "https://example.com",
    "https://github.com"
  ],
  "formats": ["markdown"],
  "only_main_content": true
}

# Check job status
GET /api/v1/scraping/batch-scrape/{job_id}/status
```

#### Website Crawling
```bash
POST /api/v1/scraping/crawl
Content-Type: application/json

{
  "url": "https://docs.example.com",
  "limit": 10,
  "max_depth": 2,
  "formats": ["markdown"],
  "exclude_paths": ["/api/", "/private/"]
}
```

#### Web Search
```bash
POST /api/v1/scraping/search
Content-Type: application/json

{
  "query": "FastAPI best practices",
  "limit": 5,
  "tbs": "qdr:d",
  "formats": ["markdown"]
}
```

#### Supported Formats
```bash
GET /api/v1/scraping/formats
```

## Configuration

All configuration is managed through environment variables with the `SCRAPER_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `SCRAPER_FIRECRAWL_API_KEY` | - | **Required**: FireCrawl API key |
| `SCRAPER_DEBUG` | `false` | Enable debug mode |
| `SCRAPER_HOST` | `127.0.0.1` | Server host |
| `SCRAPER_PORT` | `8000` | Server port |
| `SCRAPER_LOG_LEVEL` | `INFO` | Logging level |

## Error Handling

The API provides structured error responses with correlation IDs for tracking:

```json
{
  "error": "Failed to scrape URL: Connection timeout",
  "error_code": "FIRECRAWL_ERROR",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Best Practices Implemented

- ✅ **Domain-based project structure**
- ✅ **Async/await throughout**
- ✅ **Proper dependency injection**
- ✅ **Custom exception handling**
- ✅ **Request/response validation**
- ✅ **Comprehensive logging**
- ✅ **Health checks**
- ✅ **CORS and security middleware**
- ✅ **Environment-based configuration**
- ✅ **Clean separation of concerns**

## Development

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking (if using mypy)
mypy src/
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Production Deployment

### Using Gunicorn

```bash
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY .env .

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Contributing

1. Follow the existing code structure
2. Add proper type hints
3. Include comprehensive error handling
4. Write tests for new features
5. Update documentation

## License

This project is open source and available under the [MIT License](LICENSE). 