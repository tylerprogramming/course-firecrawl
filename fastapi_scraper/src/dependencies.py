from functools import lru_cache
from typing import Annotated
from fastapi import Depends, HTTPException, status
import logging

from .services.firecrawl_service import FireCrawlService, create_firecrawl_service
from .config import settings
from .exceptions import ConfigurationException

logger = logging.getLogger(__name__)

# Cache the service instance to reuse across requests
@lru_cache()
def get_firecrawl_service() -> FireCrawlService:
    """
    Dependency to get FireCrawl service instance.
    Uses LRU cache to ensure single instance across requests.
    """
    try:
        return create_firecrawl_service()
    except ConfigurationException as e:
        logger.error(f"Failed to create FireCrawl service: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service configuration error"
        )

# Type alias for dependency injection
FireCrawlServiceDep = Annotated[FireCrawlService, Depends(get_firecrawl_service)]


async def validate_api_health(
    firecrawl_service: FireCrawlServiceDep
) -> FireCrawlService:
    """
    Dependency to validate that the API and external services are healthy.
    This can be used on critical endpoints that require external service availability.
    """
    try:
        is_healthy = await firecrawl_service.health_check()
        if not is_healthy:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="External service unavailable"
            )
        return firecrawl_service
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service health check failed"
        )


def get_settings() -> type[settings]:
    """Dependency to get application settings."""
    return settings


# Type alias for settings dependency
SettingsDep = Annotated[type[settings], Depends(get_settings)] 