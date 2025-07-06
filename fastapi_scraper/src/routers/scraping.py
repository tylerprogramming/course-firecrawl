from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import List
import logging

from ..models import (
    ScrapeRequest, ScrapeResult, ApiResponse,
    BatchScrapeRequest, BatchScrapeStatus,
    CrawlRequest, CrawlStatus,
    SearchRequest, SearchResponse,
    ErrorResponse
)
from ..dependencies import FireCrawlServiceDep
from ..exceptions import ScraperException

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/scraping",
    tags=["scraping"],
    responses={
        404: {"model": ErrorResponse, "description": "Resource not found"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
    }
)


@router.post(
    "/scrape",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Scrape a single URL",
    description="Scrape content from a single URL with customizable output formats",
    response_description="Scraped content and metadata"
)
async def scrape_url(
    request: ScrapeRequest,
    firecrawl_service: FireCrawlServiceDep
) -> ApiResponse:
    """
    Scrape content from a single URL.
    
    - **url**: The URL to scrape
    - **formats**: List of output formats (markdown, html, links, screenshot)
    - **only_main_content**: Whether to extract only main content (default: true)
    - **timeout**: Timeout in milliseconds (default: 30000)
    """
    try:
        logger.info(f"Received scrape request for URL: {request.url}")
        
        result = await firecrawl_service.scrape_single_url(request)
        
        return ApiResponse(
            success=True,
            message="URL scraped successfully",
            data=result
        )
        
    except ScraperException:
        # Re-raise custom exceptions to be handled by exception handlers
        raise
    except Exception as e:
        logger.error(f"Unexpected error scraping URL {request.url}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post(
    "/batch-scrape",
    response_model=ApiResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start batch scraping job",
    description="Start an asynchronous batch scraping job for multiple URLs",
    response_description="Job information and status"
)
async def start_batch_scrape(
    request: BatchScrapeRequest,
    firecrawl_service: FireCrawlServiceDep
) -> ApiResponse:
    """
    Start a batch scraping job for multiple URLs.
    
    - **urls**: List of URLs to scrape (max 100)
    - **formats**: List of output formats
    - **only_main_content**: Whether to extract only main content
    - **timeout**: Timeout in milliseconds per URL
    
    Returns a job ID that can be used to check status.
    """
    try:
        logger.info(f"Received batch scrape request for {len(request.urls)} URLs")
        
        if len(request.urls) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 100 URLs allowed per batch"
            )
        
        batch_status = await firecrawl_service.batch_scrape_urls(request)
        
        return ApiResponse(
            success=True,
            message="Batch scraping job started successfully",
            data=batch_status
        )
        
    except ScraperException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error starting batch scrape: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get(
    "/batch-scrape/{job_id}/status",
    response_model=ApiResponse,
    summary="Get batch scraping job status",
    description="Get the current status and results of a batch scraping job",
    response_description="Job status and results if completed"
)
async def get_batch_scrape_status(
    job_id: str,
    firecrawl_service: FireCrawlServiceDep
) -> ApiResponse:
    """
    Get the status of a batch scraping job.
    
    - **job_id**: The ID of the batch scraping job
    
    Returns job status and results if completed.
    """
    try:
        logger.info(f"Getting batch scrape status for job: {job_id}")
        
        batch_status = await firecrawl_service.get_batch_scrape_status(job_id)
        
        message = f"Job status: {batch_status.job.status}"
        if batch_status.job.status == "completed":
            message += f" - {len(batch_status.data or [])} URLs processed"
        
        return ApiResponse(
            success=True,
            message=message,
            data=batch_status
        )
        
    except ScraperException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting batch scrape status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post(
    "/crawl",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Crawl a website",
    description="Crawl a website starting from a given URL with configurable depth and limits",
    response_description="Crawled pages and metadata"
)
async def crawl_website(
    request: CrawlRequest,
    firecrawl_service: FireCrawlServiceDep
) -> ApiResponse:
    """
    Crawl a website starting from the given URL.
    
    - **url**: The starting URL for crawling
    - **limit**: Maximum number of pages to crawl (default: 10, max: 1000)
    - **formats**: List of output formats
    - **only_main_content**: Whether to extract only main content
    - **max_depth**: Maximum crawling depth (default: 2, max: 10)
    - **exclude_paths**: List of URL paths to exclude from crawling
    - **include_paths**: List of URL paths to include in crawling
    """
    try:
        logger.info(f"Received crawl request for URL: {request.url}")
        
        if request.limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 1000 pages allowed per crawl"
            )
        
        crawl_status = await firecrawl_service.crawl_website(request)
        
        return ApiResponse(
            success=True,
            message=f"Website crawled successfully - {len(crawl_status.data or [])} pages found",
            data=crawl_status
        )
        
    except ScraperException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error crawling website: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post(
    "/search",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Search the web",
    description="Search the web and optionally scrape the results",
    response_description="Search results with optional scraped content"
)
async def search_web(
    request: SearchRequest,
    firecrawl_service: FireCrawlServiceDep
) -> ApiResponse:
    """
    Search the web and optionally scrape results.
    
    - **query**: The search query (1-500 characters)
    - **limit**: Number of results to return (default: 5, max: 20)
    - **tbs**: Time-based search filter (e.g., "qdr:d" for past day)
    - **formats**: List of output formats for scraped content
    """
    try:
        logger.info(f"Received search request for query: {request.query}")
        
        if request.limit > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 20 results allowed per search"
            )
        
        search_response = await firecrawl_service.search_web(request)
        
        return ApiResponse(
            success=True,
            message=f"Search completed - {len(search_response.results)} results found",
            data=search_response
        )
        
    except ScraperException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error searching web: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get(
    "/formats",
    response_model=ApiResponse,
    summary="Get supported formats",
    description="Get list of supported output formats",
    response_description="List of supported formats"
)
async def get_supported_formats() -> ApiResponse:
    """Get list of supported output formats."""
    formats = [
        {
            "name": "markdown",
            "description": "Markdown formatted content"
        },
        {
            "name": "html",
            "description": "Raw HTML content"
        },
        {
            "name": "links",
            "description": "Extracted links from the page"
        },
        {
            "name": "screenshot",
            "description": "Screenshot of the page"
        }
    ]
    
    return ApiResponse(
        success=True,
        message="Supported formats retrieved successfully",
        data={"formats": formats}
    ) 