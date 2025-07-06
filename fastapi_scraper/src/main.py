import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings
from .exceptions import ScraperException
from .models import ErrorResponse, ApiResponse
from .routers import scraping, health

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API prefix: {settings.api_prefix}")
    
    # Test FireCrawl connectivity on startup
    try:
        from .dependencies import get_firecrawl_service
        service = get_firecrawl_service()
        is_healthy = await service.health_check()
        if is_healthy:
            logger.info("FireCrawl service connectivity verified")
        else:
            logger.warning("FireCrawl service connectivity check failed")
    except Exception as e:
        logger.error(f"Failed to verify FireCrawl connectivity: {e}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A robust FastAPI server for web scraping using FireCrawl with best practices",
    version=settings.app_version,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Add trusted host middleware for security
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", settings.host]
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing and basic info."""
    start_time = time.time()
    
    # Generate correlation ID for request tracking
    correlation_id = f"req_{int(time.time() * 1000000)}"
    request.state.correlation_id = correlation_id
    
    # Log request
    logger.info(
        f"[{correlation_id}] {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"[{correlation_id}] {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"[{correlation_id}] {request.method} {request.url.path} - "
            f"Error: {str(e)} - Time: {process_time:.3f}s"
        )
        raise


# Global exception handlers
@app.exception_handler(ScraperException)
async def scraper_exception_handler(request: Request, exc: ScraperException):
    """Handle custom scraper exceptions."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    logger.warning(
        f"[{correlation_id}] ScraperException: {exc.detail} - "
        f"Error Code: {getattr(exc, 'error_code', 'UNKNOWN')}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            error_code=getattr(exc, 'error_code', None),
            timestamp=datetime.utcnow()
        ).model_dump(),
        headers=getattr(exc, 'headers', None)
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    logger.warning(f"[{correlation_id}] Validation error: {exc}")
    
    # Format validation errors nicely
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(x) for x in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    error_detail = "Validation failed: " + "; ".join(errors)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error=error_detail,
            detail=exc.errors(),
            error_code="VALIDATION_ERROR",
            timestamp=datetime.utcnow()
        ).model_dump()
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    logger.warning(
        f"[{correlation_id}] HTTP {exc.status_code}: {exc.detail} - "
        f"Path: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            timestamp=datetime.utcnow()
        ).model_dump()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    logger.error(
        f"[{correlation_id}] Unexpected error: {str(exc)} - "
        f"Path: {request.url.path}",
        exc_info=True
    )
    
    # Don't expose internal error details in production
    detail = str(exc) if settings.debug else "An unexpected error occurred"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=detail,
            error_code="INTERNAL_ERROR",
            timestamp=datetime.utcnow()
        ).model_dump()
    )


# Include routers
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(scraping.router, prefix=settings.api_prefix)


# Root endpoint
@app.get("/", response_model=ApiResponse)
async def root() -> ApiResponse:
    """Root endpoint with API information."""
    return ApiResponse(
        success=True,
        message=f"Welcome to {settings.app_name} v{settings.app_version}",
        data={
            "name": settings.app_name,
            "version": settings.app_version,
            "docs_url": "/docs" if settings.debug else None,
            "health_url": f"{settings.api_prefix}/health",
            "scraping_url": f"{settings.api_prefix}/scraping"
        }
    )


# 404 handler for undefined routes
@app.get("/{path:path}")
async def catch_all(path: str):
    """Catch-all route for undefined endpoints."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Endpoint '/{path}' not found"
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 