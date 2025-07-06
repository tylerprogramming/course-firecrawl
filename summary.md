# Ordered Summary: WeaviateVectorSearchTool & QdrantVectorSearchTool

---

## 1. WeaviateVectorSearchTool

### 1.1 Description
- The WeaviateVectorSearchTool is crafted for conducting semantic searches on documents in a Weaviate vector database, leveraging vector embeddings for more accurate and contextually relevant search results.

### 1.2 Installation
```bash
uv add weaviate-client
```

### 1.3 Setup Steps

1. **Package Installation**: Ensure `crewai[tools]` and `weaviate-client` are installed.
2. **Weaviate Setup**: Set up a Weaviate cluster ([see documentation](https://weaviate.io/developers/wcs/manage-clusters/connect)).
3. **API Keys**: Obtain your Weaviate cluster URL and API key.
4. **OpenAI API Key**: Set `OPENAI_API_KEY` in your environment variables.

### 1.4 Basic Usage Example
```python
from crewai_tools import WeaviateVectorSearchTool

# Initialize the tool
tool = WeaviateVectorSearchTool(
    collection_name='example_collections',
    limit=3,
    weaviate_cluster_url="https://your-weaviate-cluster-url.com",
    weaviate_api_key="your-weaviate-api-key",
)

@agent
def search_agent(self) -> Agent:
    '''
    This agent uses the WeaviateVectorSearchTool to search for
    semantically similar documents in a Weaviate vector database.
    '''
    return Agent(
        config=self.agents_config["search_agent"],
        tools=[tool]
    )
```

### 1.5 Parameters

- `collection_name`: (Required) Name of collection to search.
- `weaviate_cluster_url`: (Required) URL of the Weaviate cluster.
- `weaviate_api_key`: (Required) API key for the cluster.
- `limit`: (Optional) Number of results (default: 3).
- `vectorizer`: (Optional) Vectorizer to use (default: `text2vec_openai` with `nomic-embed-text` model).
- `generative_model`: (Optional) Generative model (default: OpenAI’s `gpt-4o`).

### 1.6 Customizing Vectorizer & Model
```python
from crewai_tools import WeaviateVectorSearchTool
from weaviate.classes.config import Configure

# Setup custom model for vectorizer and generative model
tool = WeaviateVectorSearchTool(
    collection_name='example_collections',
    limit=3,
    vectorizer=Configure.Vectorizer.text2vec_openai(model="nomic-embed-text"),
    generative_model=Configure.Generative.openai(model="gpt-4o-mini"),
    weaviate_cluster_url="https://your-weaviate-cluster-url.com",
    weaviate_api_key="your-weaviate-api-key",
)
```

### 1.7 Preloading Documents Example
```python
import os
from crewai_tools import WeaviateVectorSearchTool
import weaviate
from weaviate.classes.init import Auth

# Connect to Weaviate
client = weaviate.connect_to_weaviate_cloud(
    cluster_url="https://your-weaviate-cluster-url.com",
    auth_credentials=Auth.api_key("your-weaviate-api-key"),
    headers={"X-OpenAI-Api-Key": "your-openai-api-key"}
)

# Get or create collection
test_docs = client.collections.get("example_collections")
if not test_docs:
    test_docs = client.collections.create(
        name="example_collections",
        vectorizer_config=Configure.Vectorizer.text2vec_openai(model="nomic-embed-text"),
        generative_config=Configure.Generative.openai(model="gpt-4o"),
    )

# Load documents
docs_to_load = os.listdir("knowledge")
with test_docs.batch.dynamic() as batch:
    for d in docs_to_load:
        with open(os.path.join("knowledge", d), "r") as f:
            content = f.read()
        batch.add_object(
            {
                "content": content,
                "year": d.split("_")[0],
            }
        )

# Initialize the tool
tool = WeaviateVectorSearchTool(
    collection_name='example_collections',
    limit=3,
    weaviate_cluster_url="https://your-weaviate-cluster-url.com",
    weaviate_api_key="your-weaviate-api-key",
)
```

### 1.8 CrewAI Integration Example
```python
from crewai import Agent
from crewai_tools import WeaviateVectorSearchTool

# Initialize the tool
weaviate_tool = WeaviateVectorSearchTool(
    collection_name='example_collections',
    limit=3,
    weaviate_cluster_url="https://your-weaviate-cluster-url.com",
    weaviate_api_key="your-weaviate-api-key",
)

# Create an agent with the tool
rag_agent = Agent(
    name="rag_agent",
    role="You are a helpful assistant that can answer questions with the help of the WeaviateVectorSearchTool.",
    llm="gpt-4o-mini",
    tools=[weaviate_tool],
)
```

### 1.9 Notes
- Ideal for finding information based on semantic meaning.
- Leverages vector embeddings for search rather than simple keyword matching.

---

## 2. QdrantVectorSearchTool

### 2.1 Description
- QdrantVectorSearchTool enables semantic search for CrewAI agents, using Qdrant (a vector similarity search engine).

### 2.2 Installation
```bash
uv add qdrant-client
```

### 2.3 Minimal Usage Example
```python
from crewai import Agent
from crewai_tools import QdrantVectorSearchTool

# Initialize the tool
qdrant_tool = QdrantVectorSearchTool(
    qdrant_url="your_qdrant_url",
    qdrant_api_key="your_qdrant_api_key",
    collection_name="your_collection"
)

# Create an agent that uses the tool
agent = Agent(
    role="Research Assistant",
    goal="Find relevant information in documents",
    tools=[qdrant_tool]
)

# The tool uses OpenAI embeddings and returns 3 most relevant results with scores > 0.35
```

### 2.4 Complete Agentic RAG Workflow Example
```python
import os
import uuid
import pdfplumber
from openai import OpenAI
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import QdrantVectorSearchTool
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text.strip())
    return text

# Generate OpenAI embeddings
def get_openai_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

# Store text and embeddings in Qdrant
def load_pdf_to_qdrant(pdf_path, qdrant, collection_name):
    # Extract text from PDF
    text_chunks = extract_text_from_pdf(pdf_path)

    # Create Qdrant collection
    if qdrant.collection_exists(collection_name):
        qdrant.delete_collection(collection_name)
    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )

    # Store embeddings
    points = []
    for chunk in text_chunks:
        embedding = get_openai_embedding(chunk)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": chunk}
        ))
    qdrant.upsert(collection_name=collection_name, points=points)

# Initialize Qdrant client and load data
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)
collection_name = "example_collection"
pdf_path = "path/to/your/document.pdf"
load_pdf_to_qdrant(pdf_path, qdrant, collection_name)

# Initialize Qdrant search tool
qdrant_tool = QdrantVectorSearchTool(
    qdrant_url=os.getenv("QDRANT_URL"),
    qdrant_api_key=os.getenv("QDRANT_API_KEY"),
    collection_name=collection_name,
    limit=3,
    score_threshold=0.35
)

# Create CrewAI agents
search_agent = Agent(
    role="Senior Semantic Search Agent",
    goal="Find and analyze documents based on semantic search",
    backstory="""You are an expert research assistant who can find relevant
    information using semantic search in a Qdrant database.""",
    tools=[qdrant_tool],
    verbose=True
)

answer_agent = Agent(
    role="Senior Answer Assistant",
    goal="Generate answers to questions based on the context provided",
    backstory="""You are an expert answer assistant who can generate
    answers to questions based on the context provided.""",
    tools=[qdrant_tool],
    verbose=True
)

# Define tasks
search_task = Task(
    description="""Search for relevant documents about the {query}.
    Your final answer should include:
    - The relevant information found
    - The similarity scores of the results
    - The metadata of the relevant documents""",
    agent=search_agent
)

answer_task = Task(
    description="""Given the context and metadata of relevant documents,
    generate a final answer based on the context.""",
    agent=answer_agent
)

# Run CrewAI workflow
crew = Crew(
    agents=[search_agent, answer_agent],
    tasks=[search_task, answer_task],
    process=Process.sequential,
    verbose=True
)

result = crew.kickoff(
    inputs={"query": "What is the role of X in the document?"}
)
print(result)
```

### 2.5 Tool Parameters

- `query` (str): The search query.
- `filter_by` (str, optional): Metadata field to filter on.
- `filter_value` (str, optional): Value to filter by.

### 2.6 Results Format
```json
[
  {
    "metadata": {
      // Any metadata stored with the document
    },
    "context": "The actual text content of the document",
    "distance": 0.95  // Similarity score
  }
]
```

### 2.7 Default Embedding Model

- Uses OpenAI’s `text-embedding-3-small`.
- Requires `OPENAI_API_KEY` in the environment.

### 2.8 Custom Embeddings Example
```python
from transformers import AutoTokenizer, AutoModel
import torch

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

def custom_embeddings(text: str) -> list[float]:
    # Tokenize and get model outputs
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)

    # Use mean pooling to get text embedding
    embeddings = outputs.last_hidden_state.mean(dim=1)

    # Convert to list of floats and return
    return embeddings[0].tolist()

# Use custom embeddings with the tool
tool = QdrantVectorSearchTool(
    qdrant_url="your_url",
    qdrant_api_key="your_key",
    collection_name="your_collection",
    custom_embedding_fn=custom_embeddings  # Pass your custom function
)
```

### 2.9 Error Handling

- Raises ImportError if qdrant-client is not installed (option to auto-install).
- Raises ValueError if `QDRANT_URL` is not set.
- If qdrant-client is missing, prompts for install: `uv add qdrant-client`.

### 2.10 Environment Variables
```bash
export QDRANT_URL="your_qdrant_url"        # If not provided in constructor
export QDRANT_API_KEY="your_api_key"       # If not provided in constructor
export OPENAI_API_KEY="your_openai_key"    # If using default embeddings
```

---

This summary compiles necessary installation, usage instructions, configuration options, and coding examples for both Weaviate and Qdrant vector search tools, making it easy to integrate semantic vector search into CrewAI workflows.