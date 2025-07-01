from firecrawl import FirecrawlApp, ScrapeOptions
from dotenv import load_dotenv
import os

load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Crawl a website:
crawl_result = app.crawl_url(
  'https://docs.crewai.com/', 
  limit=10, 
  scrape_options=ScrapeOptions(formats=['markdown', 'html']),
)

with open('crawl_result.json', 'w') as f:
    f.write(crawl_result.model_dump_json())

# print(crawl_result)