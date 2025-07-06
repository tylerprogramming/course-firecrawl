import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from firecrawl import FirecrawlApp, ScrapeOptions

from ..models import (
    ScrapeRequest, ScrapeResult, ScrapeMetadata,
    BatchScrapeRequest, BatchScrapeStatus, BatchScrapeJob,
    CrawlRequest, CrawlStatus, CrawlJob,
    SearchRequest, SearchResponse, SearchResult,
    ScrapeFormat
)
from ..exceptions import (
    FireCrawlException, InvalidURLException, JobNotFoundException,
    JobTimeoutException, ServiceUnavailableException, ConfigurationException
)
from ..config import settings

logger = logging.getLogger(__name__)


class FireCrawlService:
    """Service layer for FireCrawl operations."""
    
    def __init__(self, api_key: str):
        """Initialize FireCrawl service."""
        try:
            self.app = FirecrawlApp(api_key=api_key)
            self._job_storage: Dict[str, Any] = {}  # In-memory storage for jobs
            logger.info("FireCrawl service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize FireCrawl service: {e}")
            raise ConfigurationException(f"Failed to initialize FireCrawl: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check if FireCrawl service is healthy."""
        try:
            # Try a simple scrape to test connectivity
            await self.scrape_single_url(ScrapeRequest(url="https://example.com"))
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def scrape_single_url(self, request: ScrapeRequest) -> ScrapeResult:
        """Scrape a single URL."""
        try:
            logger.info(f"Scraping URL: {request.url}")
            
            # Convert request to FireCrawl format
            formats = [f.value for f in request.formats]
            
            # Perform scraping
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.app.scrape_url(
                    url=str(request.url),
                    formats=formats,
                    only_main_content=request.only_main_content,
                    timeout=request.timeout
                )
            )
            
            # Convert result to our format
            metadata = ScrapeMetadata(
                title=result.metadata.get('title') if result.metadata else None,
                description=result.metadata.get('description') if result.metadata else None,
                credits_used=result.metadata.get('creditsUsed') if result.metadata else None,
                url=str(request.url),
                status_code=result.metadata.get('statusCode') if result.metadata else None
            )
            
            scrape_result = ScrapeResult(
                url=str(request.url),
                markdown=getattr(result, 'markdown', None),
                html=getattr(result, 'html', None),
                links=getattr(result, 'links', None),
                screenshot=getattr(result, 'screenshot', None),
                metadata=metadata,
                success=True
            )
            
            logger.info(f"Successfully scraped URL: {request.url}")
            return scrape_result
            
        except Exception as e:
            logger.error(f"Failed to scrape URL {request.url}: {e}")
            error_result = ScrapeResult(
                url=str(request.url),
                metadata=ScrapeMetadata(url=str(request.url)),
                success=False,
                error=str(e)
            )
            
            # Re-raise as FireCrawlException for proper error handling
            raise FireCrawlException(f"Failed to scrape URL {request.url}: {str(e)}")
    
    async def batch_scrape_urls(self, request: BatchScrapeRequest) -> BatchScrapeStatus:
        """Start a batch scraping job."""
        try:
            logger.info(f"Starting batch scrape for {len(request.urls)} URLs")
            
            # Convert request to FireCrawl format
            formats = [f.value for f in request.formats]
            url_strings = [str(url) for url in request.urls]
            
            # Start batch scraping
            batch_job = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.app.async_batch_scrape_urls(
                    urls=url_strings,
                    formats=formats,
                    only_main_content=request.only_main_content,
                    timeout=request.timeout
                )
            )
            
            # Create our job representation
            job = BatchScrapeJob(
                id=batch_job.id,
                status="pending",
                total_urls=len(request.urls)
            )
            
            # Store job for tracking
            self._job_storage[job.id] = {
                "job": job,
                "type": "batch_scrape",
                "urls": url_strings
            }
            
            logger.info(f"Started batch scrape job: {job.id}")
            return BatchScrapeStatus(job=job)
            
        except Exception as e:
            logger.error(f"Failed to start batch scraping: {e}")
            raise FireCrawlException(f"Failed to start batch scraping: {str(e)}")
    
    async def get_batch_scrape_status(self, job_id: str) -> BatchScrapeStatus:
        """Get the status of a batch scraping job."""
        try:
            logger.info(f"Getting batch scrape status for job: {job_id}")
            
            if job_id not in self._job_storage:
                raise JobNotFoundException(job_id)
            
            # Get status from FireCrawl
            batch_status = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.app.check_batch_scrape_status(job_id)
            )
            
            # Update our job status
            stored_job = self._job_storage[job_id]
            job = stored_job["job"]
            job.status = batch_status.status
            job.completed_urls = len(batch_status.data) if batch_status.data else 0
            
            if batch_status.status == "completed":
                job.completed_at = datetime.utcnow()
                
                # Convert results to our format
                results = []
                if batch_status.data:
                    for result in batch_status.data:
                        metadata = ScrapeMetadata(
                            title=result.metadata.get('title') if result.metadata else None,
                            description=result.metadata.get('description') if result.metadata else None,
                            credits_used=result.metadata.get('creditsUsed') if result.metadata else None,
                            url=result.metadata.get('url') if result.metadata else None,
                            status_code=result.metadata.get('statusCode') if result.metadata else None
                        )
                        
                        scrape_result = ScrapeResult(
                            url=result.metadata.get('url', ''),
                            markdown=getattr(result, 'markdown', None),
                            html=getattr(result, 'html', None),
                            links=getattr(result, 'links', None),
                            screenshot=getattr(result, 'screenshot', None),
                            metadata=metadata,
                            success=True
                        )
                        results.append(scrape_result)
                
                return BatchScrapeStatus(job=job, data=results)
            
            return BatchScrapeStatus(job=job)
            
        except Exception as e:
            logger.error(f"Failed to get batch scrape status for job {job_id}: {e}")
            if "not found" in str(e).lower():
                raise JobNotFoundException(job_id)
            raise FireCrawlException(f"Failed to get batch scrape status: {str(e)}")
    
    async def crawl_website(self, request: CrawlRequest) -> CrawlStatus:
        """Start a website crawling job."""
        try:
            logger.info(f"Starting crawl for URL: {request.url}")
            
            # Convert request to FireCrawl format
            formats = [f.value for f in request.formats]
            scrape_options = ScrapeOptions(
                formats=formats,
                only_main_content=request.only_main_content
            )
            
            # Start crawling
            crawl_job = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.app.crawl_url(
                    url=str(request.url),
                    limit=request.limit,
                    scrape_options=scrape_options,
                    max_depth=request.max_depth,
                    exclude_paths=request.exclude_paths,
                    include_paths=request.include_paths
                )
            )
            
            # Create our job representation
            job = CrawlJob(
                id=str(uuid.uuid4()),  # Generate our own ID
                status="completed",  # FireCrawl crawl is synchronous
                total_pages=len(crawl_job.data) if crawl_job.data else 0,
                completed_pages=len(crawl_job.data) if crawl_job.data else 0,
                completed_at=datetime.utcnow()
            )
            
            # Convert results to our format
            results = []
            if crawl_job.data:
                for result in crawl_job.data:
                    metadata = ScrapeMetadata(
                        title=result.metadata.get('title') if result.metadata else None,
                        description=result.metadata.get('description') if result.metadata else None,
                        credits_used=result.metadata.get('creditsUsed') if result.metadata else None,
                        url=result.metadata.get('url') if result.metadata else None,
                        status_code=result.metadata.get('statusCode') if result.metadata else None
                    )
                    
                    scrape_result = ScrapeResult(
                        url=result.metadata.get('url', ''),
                        markdown=getattr(result, 'markdown', None),
                        html=getattr(result, 'html', None),
                        links=getattr(result, 'links', None),
                        screenshot=getattr(result, 'screenshot', None),
                        metadata=metadata,
                        success=True
                    )
                    results.append(scrape_result)
            
            logger.info(f"Completed crawl for URL: {request.url}, pages: {len(results)}")
            return CrawlStatus(job=job, data=results)
            
        except Exception as e:
            logger.error(f"Failed to crawl website {request.url}: {e}")
            raise FireCrawlException(f"Failed to crawl website: {str(e)}")
    
    async def search_web(self, request: SearchRequest) -> SearchResponse:
        """Search the web and optionally scrape results."""
        try:
            logger.info(f"Searching for: {request.query}")
            
            # Convert request to FireCrawl format
            formats = [f.value for f in request.formats]
            scrape_options = ScrapeOptions(formats=formats)
            
            # Perform search
            search_result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.app.search(
                    query=request.query,
                    limit=request.limit,
                    tbs=request.tbs,
                    scrape_options=scrape_options
                )
            )
            
            # Convert results to our format
            results = []
            if search_result.data:
                for result in search_result.data:
                    search_item = SearchResult(
                        title=result.get('title', ''),
                        url=result.get('url', ''),
                        description=result.get('description'),
                        markdown=result.get('markdown'),
                        links=result.get('links')
                    )
                    results.append(search_item)
            
            response = SearchResponse(
                query=request.query,
                results=results,
                total_results=len(results)
            )
            
            logger.info(f"Search completed for: {request.query}, results: {len(results)}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to search for '{request.query}': {e}")
            raise FireCrawlException(f"Failed to search: {str(e)}")


# Service factory function
def create_firecrawl_service() -> FireCrawlService:
    """Create and return a FireCrawl service instance."""
    if not settings.firecrawl_api_key:
        raise ConfigurationException("FireCrawl API key is required")
    
    return FireCrawlService(
        api_key=settings.firecrawl_api_key
    ) 