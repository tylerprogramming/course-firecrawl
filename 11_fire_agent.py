from firecrawl import FirecrawlApp
from firecrawl.firecrawl import AgentOptions

import os
from dotenv import load_dotenv

load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Scrape a website:
scrape_result = app.batch_scrape_urls([
    'https://docs.crewai.com/en',
    'https://crewai.dev/',
    'https://www.ycombinator.com/companies/'
],
  formats=['markdown', 'html'],
  agent=AgentOptions(
    model='FIRE-1',
    prompt='Navigate through the product listings by clicking the button until disabled. Scrape each page.'
  )
)

print(scrape_result)