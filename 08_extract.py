from firecrawl import FirecrawlApp
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from openai import OpenAI

load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

class ExtractSchema(BaseModel):
    information: str
    code_example: str
    
class ExtractList(BaseModel):
    extracted: list[ExtractSchema]
    
results = app.extract(
    urls=[
        'https://docs.crewai.com/en/tools/database-data/weaviatevectorsearchtool', 
        'https://docs.crewai.com/en/tools/database-data/qdrantvectorsearchtool'
    ],
    prompt='I need to get information from the websites and any code examples.  Only from the urls provided.',
    schema=ExtractList.model_json_schema()
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

completion = client.chat.completions.create(
  model="gpt-4.1",
  messages=[
    {"role": "developer", "content": "You are a helpful assistant."},
    {"role": "user", "content": f"I need you to extract the information and give this into an ordered summary of that information as markdown.  It should find coding examples and all information.  Here is the information: {results}"}
  ]
)

with open('summary.md', 'w') as f:
    f.write(completion.choices[0].message.content)