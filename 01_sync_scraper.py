from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os

load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Scrape a website:
scrape_result = app.scrape_url(
    url='firecrawl.dev', 
    formats=['markdown', 'html']
)

# print(scrape_result)

# Print extracted information
print("Title:", scrape_result.metadata.get('title'))
print("Description:", scrape_result.metadata.get('description'))
print("Credits Used:", scrape_result.metadata.get('creditsUsed'))
print("First 500 characters of Markdown:", scrape_result.markdown[:500])