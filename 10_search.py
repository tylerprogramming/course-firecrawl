import os
from firecrawl import FirecrawlApp, ScrapeOptions
from dotenv import load_dotenv

load_dotenv()

# Initialize the client with your API key
app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

search_result = app.search(
    query="context engineering",
    limit=5,
    tbs="qdr:d",
    scrape_options=ScrapeOptions(formats=["markdown", "links"])
)

# Print the search results
for result in search_result.data:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Description: {result['description']}")
    print(f"Content: {result['markdown'][:150]}...")  # first 150 chars
    print(f"Links: {', '.join(result['links'][:3])}...")  # first 3 links
    print("-"*100)