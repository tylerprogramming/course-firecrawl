from firecrawl import FirecrawlApp, ScrapeOptions
import os
from dotenv import load_dotenv
import time

load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Crawl a website:
crawl_status = app.async_crawl_url(
  'https://docs.crewai.com/', 
  limit=5, 
  scrape_options=ScrapeOptions(formats=['markdown', 'html'], onlyMainContent=True)
)

print(crawl_status.id)

while True:
    if crawl_status.id and app.check_crawl_status(crawl_status.id).status == 'completed':
        print(app.check_crawl_status(crawl_status.id))
        break
    else:
        print(app.check_crawl_status(crawl_status.id).status)
    time.sleep(5)

# Get the crawl results
results = crawl_status.model_dump_json()

print(results)
