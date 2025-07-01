"""
Pydantic models for FireCrawl Flow
"""

from pydantic import BaseModel
from typing import List


class Summary(BaseModel):
    key_action_items: list[str]
    dramatic_news_points: list[str]
    key_takeaways: list[str]
    summary: str


class SearchResult(BaseModel):
    title: str
    url: str
    description: str
    markdown: str
    links: list[str]


class FireCrawlState(BaseModel):
    query: str = ""
    limit: int = 3
    search_result: list[SearchResult] = []
    summaries: list[Summary] = [] 