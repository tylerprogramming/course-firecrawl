from firecrawl import JsonConfig, FirecrawlApp
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

class ExtractSchema(BaseModel):
    company_name: str
    is_open_source: bool
    supports_sso: bool
    has_enterprise_plan: bool
    supports_edge_functions: bool
    supports_static_sites: bool
    contact_email: str
    has_github_integration: bool
    documentation_url: str
    pricing_url: str
    popular_frameworks: list[str]

json_config = JsonConfig(schema=ExtractSchema)

llm_extraction_result = app.scrape_url(
    url="https://vercel.com/docs",
    formats=["json"],
    json_options=json_config,
    only_main_content=False,
    timeout=120000
)

print(llm_extraction_result.json)
