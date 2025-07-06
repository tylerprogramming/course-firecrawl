from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
from time import sleep
from firecrawl import FirecrawlApp

load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Scrape a website:
# Or, you can use the asynchronous method:
batch_scrape_job = app.async_batch_scrape_urls(
    ['https://docs.firecrawl.dev'], 
    formats=['markdown', 'html']
)
print(batch_scrape_job)

# (async) You can then use the job ID to check the status of the batch scrape:
while True:
    batch_scrape_status = app.check_batch_scrape_status(batch_scrape_job.id)
    print(batch_scrape_status)
    if batch_scrape_status.status == 'completed':
        break
    sleep(10)

# Access the markdown directly
if batch_scrape_status.data and len(batch_scrape_status.data) > 0:
    markdown_content = batch_scrape_status.data[0].markdown
    print(markdown_content)