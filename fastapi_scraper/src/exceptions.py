from fastapi import HTTPException, status
from typing import Optional, Any, Dict


class ScraperException(HTTPException):
    """Base exception class for scraper-related errors."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class FireCrawlException(ScraperException):
    """Exception for FireCrawl API errors."""
    
    def __init__(
        self,
        detail: str,
        error_code: str = "FIRECRAWL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
            error_code=error_code,
            headers={"X-Error-Code": error_code}
        )


class InvalidURLException(ScraperException):
    """Exception for invalid URL errors."""
    
    def __init__(self, url: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid URL provided: {url}",
            error_code="INVALID_URL",
            headers={"X-Error-Code": "INVALID_URL"}
        )


class RateLimitExceededException(ScraperException):
    """Exception for rate limit exceeded errors."""
    
    def __init__(self, retry_after: Optional[int] = None):
        headers = {"X-Error-Code": "RATE_LIMIT_EXCEEDED"}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
            
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            error_code="RATE_LIMIT_EXCEEDED",
            headers=headers
        )


class JobNotFoundException(ScraperException):
    """Exception for job not found errors."""
    
    def __init__(self, job_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
            error_code="JOB_NOT_FOUND",
            headers={"X-Error-Code": "JOB_NOT_FOUND"}
        )


class JobTimeoutException(ScraperException):
    """Exception for job timeout errors."""
    
    def __init__(self, job_id: str, timeout: int):
        super().__init__(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=f"Job {job_id} timed out after {timeout} seconds",
            error_code="JOB_TIMEOUT",
            headers={"X-Error-Code": "JOB_TIMEOUT"}
        )


class TooManyURLsException(ScraperException):
    """Exception for too many URLs in batch request."""
    
    def __init__(self, count: int, max_count: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many URLs provided: {count}. Maximum allowed: {max_count}",
            error_code="TOO_MANY_URLS",
            headers={"X-Error-Code": "TOO_MANY_URLS"}
        )


class InvalidFormatException(ScraperException):
    """Exception for invalid format errors."""
    
    def __init__(self, format_type: str, valid_formats: list):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid format '{format_type}'. Valid formats: {', '.join(valid_formats)}",
            error_code="INVALID_FORMAT",
            headers={"X-Error-Code": "INVALID_FORMAT"}
        )


class ConfigurationException(ScraperException):
    """Exception for configuration errors."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {detail}",
            error_code="CONFIGURATION_ERROR",
            headers={"X-Error-Code": "CONFIGURATION_ERROR"}
        )


class ServiceUnavailableException(ScraperException):
    """Exception for service unavailable errors."""
    
    def __init__(self, service_name: str = "External service"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service_name} is currently unavailable",
            error_code="SERVICE_UNAVAILABLE",
            headers={"X-Error-Code": "SERVICE_UNAVAILABLE"}
        )


class ValidationException(ScraperException):
    """Exception for validation errors."""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        error_code = "VALIDATION_ERROR"
        if field:
            error_code = f"VALIDATION_ERROR_{field.upper()}"
            
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code,
            headers={"X-Error-Code": error_code}
        ) 