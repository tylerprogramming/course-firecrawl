from firecrawl import FirecrawlApp
import os
from dotenv import load_dotenv
import time
load_dotenv()

app = FirecrawlApp(
    api_key=os.getenv("FIRECRAWL_API_KEY")
)

# Start an extraction job first
extract_job = app.async_extract([
    'https://docs.firecrawl.dev/*', 
    'https://firecrawl.dev/'
], prompt="Extract the company mission and features from these pages.")

# Get the status of the extraction job
job_status = app.get_extract_status(extract_job.id)

while True:
    job_status = app.get_extract_status(extract_job.id)
    if app.get_extract_status(extract_job.id) and app.get_extract_status(extract_job.id).status == 'completed':
        print("Extraction completed")
        print(app.get_extract_status(extract_job.id))
        break
    print(job_status.status)
    time.sleep(5)
    
print(job_status.data)