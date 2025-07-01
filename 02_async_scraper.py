from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
from time import sleep
import asyncio
from firecrawl import AsyncFirecrawlApp

load_dotenv()

# app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# # Scrape a website:
# # Or, you can use the asynchronous method:
# batch_scrape_job = app.async_batch_scrape_urls(
#     ['firecrawl.dev'], 
#     formats=['markdown', 'html']
# )
# print(batch_scrape_job)

# # (async) You can then use the job ID to check the status of the batch scrape:
# while True:
#     batch_scrape_status = app.check_batch_scrape_status(batch_scrape_job.id)
#     print(batch_scrape_status)
#     if batch_scrape_status.status == 'completed':
#         break
#     sleep(10)

# print(batch_scrape_status)
# print(batch_scrape_job.model_dump_json())



async def main():
    app = AsyncFirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    response = await app.async_batch_scrape_urls(
        urls=['firecrawl.dev'],		
        formats= [ 'markdown' ]
    )
    print(response)

asyncio.run(main())