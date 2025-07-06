from fastapi import APIRouter, status
from datetime import datetime
import logging

from ..models import HealthCheck, ApiResponse
from ..dependencies import FireCrawlServiceDep
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={
        200: {"model": HealthCheck, "description": "Service is healthy"},
        503: {"model": HealthCheck, "description": "Service is unhealthy"},
    }
)


@router.get(
    "",
    response_model=HealthCheck,
    summary="Health check",
    description="Check the health status of the API and external services",
    response_description="Health status information"
)
async def health_check(
    firecrawl_service: FireCrawlServiceDep
) -> HealthCheck:
    """
    Perform a health check of the API and external services.
    
    Returns:
    - API status
    - Version information
    - FireCrawl service connectivity status
    - Timestamp of the check
    """
    try:
        # Check FireCrawl service connectivity
        firecrawl_connected = await firecrawl_service.health_check()
        
        # Determine overall health status
        overall_status = "healthy" if firecrawl_connected else "unhealthy"
        
        logger.info(f"Health check completed - Status: {overall_status}")
        
        return HealthCheck(
            status=overall_status,
            version=settings.app_version,
            timestamp=datetime.utcnow(),
            firecrawl_connected=firecrawl_connected
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheck(
            status="unhealthy",
            version=settings.app_version,
            timestamp=datetime.utcnow(),
            firecrawl_connected=False
        )


@router.get(
    "/ready",
    response_model=ApiResponse,
    summary="Readiness check",
    description="Check if the API is ready to serve requests",
    response_description="Readiness status"
)
async def readiness_check() -> ApiResponse:
    """
    Simple readiness check endpoint.
    
    This endpoint can be used by load balancers and orchestration systems
    to determine if the service is ready to accept traffic.
    """
    return ApiResponse(
        success=True,
        message="Service is ready",
        data={"ready": True, "timestamp": datetime.utcnow()}
    )


@router.get(
    "/live",
    response_model=ApiResponse,
    summary="Liveness check",
    description="Check if the API is alive and responding",
    response_description="Liveness status"
)
async def liveness_check() -> ApiResponse:
    """
    Simple liveness check endpoint.
    
    This endpoint can be used by orchestration systems to determine
    if the service is alive and should be kept running.
    """
    return ApiResponse(
        success=True,
        message="Service is alive",
        data={"alive": True, "timestamp": datetime.utcnow()}
    ) 