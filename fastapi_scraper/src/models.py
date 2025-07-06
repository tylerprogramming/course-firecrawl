from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum

class ScrapeFormat(str, Enum):
    """Supported scraping formats."""
    MARKDOWN = "markdown"
    HTML = "html"
    LINKS = "links"
    SCREENSHOT = "screenshot"

class ScrapeRequest(BaseModel):
    """Request model for scraping a single URL."""
    url: HttpUrl = Field(..., description="URL to scrape")
    formats: List[ScrapeFormat] = Field(default=[ScrapeFormat.MARKDOWN], description="Output formats")
    only_main_content: bool = Field(default=True, description="Extract only main content")
    timeout: int = Field(default=30000, description="Timeout in milliseconds", ge=1000, le=300000)
    
    @validator('formats')
    def validate_formats(cls, v):
        if not v:
            return [ScrapeFormat.MARKDOWN]
        return v

class BatchScrapeRequest(BaseModel):
    """Request model for batch scraping multiple URLs."""
    urls: List[HttpUrl] = Field(..., description="List of URLs to scrape", min_items=1, max_items=100)
    formats: List[ScrapeFormat] = Field(default=[ScrapeFormat.MARKDOWN], description="Output formats")
    only_main_content: bool = Field(default=True, description="Extract only main content")
    timeout: int = Field(default=30000, description="Timeout in milliseconds", ge=1000, le=300000)

class CrawlRequest(BaseModel):
    """Request model for crawling a website."""
    url: HttpUrl = Field(..., description="URL to crawl")
    limit: int = Field(default=10, description="Maximum number of pages to crawl", ge=1, le=1000)
    formats: List[ScrapeFormat] = Field(default=[ScrapeFormat.MARKDOWN], description="Output formats")
    only_main_content: bool = Field(default=True, description="Extract only main content")
    max_depth: Optional[int] = Field(default=2, description="Maximum crawl depth", ge=1, le=10)
    exclude_paths: Optional[List[str]] = Field(default=None, description="Paths to exclude from crawling")
    include_paths: Optional[List[str]] = Field(default=None, description="Paths to include in crawling")

class SearchRequest(BaseModel):
    """Request model for web search."""
    query: str = Field(..., description="Search query", min_length=1, max_length=500)
    limit: int = Field(default=5, description="Number of results to return", ge=1, le=20)
    tbs: Optional[str] = Field(default=None, description="Time-based search filter")
    formats: List[ScrapeFormat] = Field(default=[ScrapeFormat.MARKDOWN], description="Output formats")

class ScrapeMetadata(BaseModel):
    """Metadata from scraping operation."""
    title: Optional[str] = None
    description: Optional[str] = None
    credits_used: Optional[int] = None
    url: Optional[str] = None
    status_code: Optional[int] = None
    
class ScrapeResult(BaseModel):
    """Result from scraping operation."""
    url: str
    markdown: Optional[str] = None
    html: Optional[str] = None
    links: Optional[List[str]] = None
    screenshot: Optional[str] = None
    metadata: ScrapeMetadata
    success: bool = True
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class BatchScrapeJob(BaseModel):
    """Batch scraping job information."""
    id: str
    status: Literal["pending", "running", "completed", "failed"]
    total_urls: int
    completed_urls: int = 0
    failed_urls: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
class BatchScrapeStatus(BaseModel):
    """Status of batch scraping operation."""
    job: BatchScrapeJob
    data: Optional[List[ScrapeResult]] = None
    
class CrawlJob(BaseModel):
    """Crawling job information."""
    id: str
    status: Literal["pending", "running", "completed", "failed"]
    total_pages: Optional[int] = None
    completed_pages: int = 0
    failed_pages: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class CrawlStatus(BaseModel):
    """Status of crawling operation."""
    job: CrawlJob
    data: Optional[List[ScrapeResult]] = None

class SearchResult(BaseModel):
    """Single search result."""
    title: str
    url: str
    description: Optional[str] = None
    markdown: Optional[str] = None
    links: Optional[List[str]] = None
    
class SearchResponse(BaseModel):
    """Response from search operation."""
    query: str
    results: List[SearchResult]
    total_results: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ApiResponse(BaseModel):
    """Generic API response wrapper."""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HealthCheck(BaseModel):
    """Health check response."""
    status: Literal["healthy", "unhealthy"] = "healthy"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    firecrawl_connected: bool = True
    
class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow) 