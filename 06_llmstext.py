from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os

load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Scrape a website:
scrape_result = app.generate_llms_text(
    url='https://docs.crewai.com/en', 
    show_full_text=True,
)

while True:
    if scrape_result.status == 'completed':
        print(scrape_result)
        break
    else:
        print(scrape_result.status)