# DeepKnowledge Agent Examples

Two implementations of the DeepKnowledge agent - an interactive CLI version and a production AgentOS deployment.

## Overview

DeepKnowledge is an advanced research assistant that performs iterative searches through a knowledge base to provide comprehensive, well-researched answers. It uses the Agno documentation as its knowledge base.

### Key Features
- **Iterative Search**: Breaks down complex queries into sub-questions
- **Source Attribution**: Cites all sources from the knowledge base
- **Persistent Knowledge Base**: Embeddings are cached and reused across runs
- **Session Management**: Maintains conversation history
- **Production Ready**: AgentOS version with REST API and Web UI

## Files

- **[deep_knowledge.py](deep_knowledge.py)** - Interactive CLI version with inquirer-based UI
- **[deep_knowledge_os.py](deep_knowledge_os.py)** - Production AgentOS deployment with REST API

## Setup

### 1. Install Dependencies

```bash
# Core dependencies
pip install agno openai lancedb tantivy

# For CLI version
pip install inquirer typer rich

# For production (PostgreSQL support)
pip install sqlalchemy psycopg2-binary
```

### 2. Configure Environment

```bash
# Required
export OPENAI_API_KEY="your-openai-api-key"

# Optional: Use PostgreSQL for production (defaults to SQLite)
export DATABASE_URL="postgresql://user:pass@host:port/dbname"
```

## Usage

### Interactive CLI Version

Run the interactive CLI with example questions:

```bash
python deep_knowledge.py
```

**Features:**
- Choose from example topics or enter custom questions
- Session management (create new or continue existing)
- Streaming responses with markdown formatting
- Interactive menu-driven interface

**Example Session:**
```
🤔 Welcome to DeepKnowledge - Your Advanced Research Assistant! 📚
Started New Session: abc123

Select a topic or ask a different question:
1. What are AI agents and how do they work in Agno?
2. What chunking strategies does Agno support for text processing?
3. How can I implement custom tools in Agno?
4. How does knowledge retrieval work in Agno?
5. What types of embeddings does Agno support?
> Enter custom question...
> Exit
```

### Production AgentOS Version

Start the production server:

```bash
python deep_knowledge_os.py
```

**Access Points:**
- API Documentation: http://localhost:7777/docs
- Web Interface: http://localhost:7777/ui
- Health Check: http://localhost:7777/health

## API Usage Examples

### 1. Using curl

```bash
# Send a question
curl -X POST "http://localhost:7777/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deep-knowledge",
    "messages": [
      {"role": "user", "content": "What are AI agents in Agno?"}
    ],
    "stream": false
  }'
```

### 2. Using Python requests

```python
import requests

response = requests.post(
    "http://localhost:7777/v1/chat/completions",
    json={
        "model": "deep-knowledge",
        "messages": [
            {"role": "user", "content": "What chunking strategies does Agno support?"}
        ],
        "stream": False,
    }
)

answer = response.json()["choices"][0]["message"]["content"]
print(answer)
```

### 3. Using OpenAI SDK (Compatible)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:7777/v1",
    api_key="not-required"  # Local deployment
)

response = client.chat.completions.create(
    model="deep-knowledge",
    messages=[
        {"role": "user", "content": "How does knowledge retrieval work?"}
    ],
    stream=False
)

print(response.choices[0].message.content)
```

### 4. Streaming Responses

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:7777/v1", api_key="not-required")

stream = client.chat.completions.create(
    model="deep-knowledge",
    messages=[{"role": "user", "content": "Explain embeddings in detail"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### 5. Session Continuity

```python
import requests

# First message - creates a session
response1 = requests.post(
    "http://localhost:7777/v1/chat/completions",
    json={
        "model": "deep-knowledge",
        "messages": [{"role": "user", "content": "What are AI agents?"}],
    }
)

# Extract session_id from response headers or use a custom session_id
session_id = response1.json().get("session_id")

# Continue conversation with session context
response2 = requests.post(
    "http://localhost:7777/v1/chat/completions",
    json={
        "model": "deep-knowledge",
        "messages": [{"role": "user", "content": "Tell me more about Teams"}],
        "session_id": session_id,  # Maintains conversation history
    }
)
```

## Knowledge Base Management

### Persistence

The knowledge base is stored in `tmp/lancedb/` and persists across runs:

- **First run**: Downloads and embeds documentation (~1-2 minutes)
- **Subsequent runs**: Reuses cached embeddings (instant startup)

### Resetting the Knowledge Base

To reload the knowledge base from scratch:

```bash
rm -rf tmp/lancedb
python deep_knowledge.py  # or deep_knowledge_os.py
```

### Adding Custom Content

Modify the `initialize_knowledge_base()` function:

```python
def initialize_knowledge_base() -> Knowledge:
    agent_knowledge = Knowledge(
        vector_db=LanceDb(
            uri="tmp/lancedb",
            table_name="deep_knowledge_kb",
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
    )

    if not agent_knowledge.vector_db.exists():
        # Add multiple sources
        agent_knowledge.add_content(url="https://docs.agno.com/llms-full.txt")
        agent_knowledge.add_content(url="https://example.com/docs.txt")
        # Or add local files
        agent_knowledge.add_content(path="./docs/")

    return agent_knowledge
```

## Production Deployment

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY deep_knowledge_os.py .

# Expose port
EXPOSE 7777

# Run application
CMD ["python", "deep_knowledge_os.py"]
```

Build and run:

```bash
docker build -t deep-knowledge .
docker run -p 7777:7777 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e DATABASE_URL=$DATABASE_URL \
  -v $(pwd)/tmp:/app/tmp \
  deep-knowledge
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for embeddings and chat |
| `DATABASE_URL` | No | SQLite | PostgreSQL connection string for production |
| `AGNO_TELEMETRY` | No | true | Set to `false` to disable telemetry |

### Using PostgreSQL in Production

```bash
# Set PostgreSQL connection
export DATABASE_URL="postgresql://user:password@localhost:5432/agno_db"

# Run the agent
python deep_knowledge_os.py
```

The agent will automatically use PostgreSQL for session storage.

## Architecture

### Knowledge Base Flow

```
User Query → Agent → Knowledge Search (3-5 searches) → Synthesis → Response
                ↓
         LanceDB (persistent)
         └── Embeddings (cached)
```

### Session Management

```
User → AgentOS → Agent Instance → Database (PostgreSQL/SQLite)
                      ↓
                Session History (last 3 runs)
```

## Example Queries

Try these questions with the agent:

1. **Architecture**: "What are the different types of agents in Agno?"
2. **Knowledge**: "How does Agno handle knowledge base management?"
3. **Embeddings**: "What embedding models does Agno support?"
4. **Tools**: "How can I implement custom tools in Agno?"
5. **Workflows**: "What storage options are available for workflow caching?"
6. **Streaming**: "How does Agno handle streaming responses?"
7. **Providers**: "What types of LLM providers does Agno support?"
8. **Custom Sources**: "How can I implement custom knowledge sources?"

## Troubleshooting

### Knowledge Base Not Loading

If the knowledge base doesn't persist:

```bash
# Check if directory exists and has write permissions
ls -la tmp/lancedb/

# Verify embeddings are being created
python -c "from agno.vectordb.lancedb import LanceDb; print(LanceDb(uri='tmp/lancedb', table_name='deep_knowledge_kb').exists())"
```

### API Connection Issues

```bash
# Check if server is running
curl http://localhost:7777/health

# View logs
python deep_knowledge_os.py  # Check console output
```

### Database Issues

```bash
# For SQLite, check file
ls -la tmp/agents.db

# For PostgreSQL, verify connection
psql $DATABASE_URL -c "SELECT 1"
```

## Performance Optimization

### Knowledge Base
- Uses hybrid search (vector + keyword) for better accuracy
- Embeddings cached locally for instant startup
- LanceDB provides efficient vector storage

### Agent Configuration
- `num_history_runs=3` - Limits context window
- `show_tool_calls=False` - Cleaner output in production
- `search_knowledge=True` - Enables agentic RAG

### Production Settings
- Use PostgreSQL for production (better concurrency)
- Enable connection pooling for high traffic
- Set `debug_mode=False` in production

## License

See main Agno repository for license information.
