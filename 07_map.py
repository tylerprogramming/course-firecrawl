from firecrawl import FirecrawlApp
import os
from dotenv import load_dotenv

load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Map a website:
map_result = app.map_url(
    url='https://docs.crewai.com/en',
    include_subdomains=True,
)

print(map_result)
print("Found", len(map_result.links), "pages")