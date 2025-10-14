# DeepKnowledge Quick Start Guide

Get started with DeepKnowledge in 5 minutes!

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
cd example/knowledge
pip install -r requirements.txt
```

### 2. Set API Key

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Choose Your Version

## Option A: Interactive CLI (Recommended for First Run)

Perfect for testing and exploring the agent interactively.

```bash
python deep_knowledge.py
```

**What you'll see:**
```
📥 Loading knowledge base (first run only)...
✅ Knowledge base loaded successfully!

🤔 Welcome to DeepKnowledge - Your Advanced Research Assistant! 📚
Started New Session: abc123

Select a topic or ask a different question:
1. What are AI agents and how do they work in Agno?
2. What chunking strategies does Agno support for text processing?
3. How can I implement custom tools in Agno?
...
```

First run will take 1-2 minutes to load the knowledge base. Subsequent runs are instant!

## Option B: Production API (AgentOS)

Deploy as a REST API with web UI for production use.

```bash
python deep_knowledge_os.py
```

**What you'll see:**
```
✅ Using existing knowledge base from disk
🗄️  Using SQLite database

===============================================================
🤔 DeepKnowledge AgentOS
===============================================================

📚 Advanced Research Assistant with Knowledge Base

🌐 Endpoints:
   - API Documentation: http://localhost:7777/docs
   - Web Interface: http://localhost:7777/ui
   - Health Check: http://localhost:7777/health

===============================================================

INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:7777
```

### Test the API

Open another terminal and try:

```bash
# Test the API
curl -X POST "http://localhost:7777/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deep-knowledge",
    "messages": [
      {"role": "user", "content": "What are AI agents in Agno?"}
    ]
  }'
```

Or visit the web UI at: **http://localhost:7777/ui**

## 📊 What's Happening Behind the Scenes?

### First Run (1-2 minutes)
1. Downloads Agno documentation from https://docs.agno.com/llms-full.txt
2. Creates embeddings using OpenAI's text-embedding-3-small model
3. Stores vectors in LanceDB at `tmp/lancedb/`
4. Ready to answer questions!

### Subsequent Runs (instant)
1. Loads existing embeddings from `tmp/lancedb/`
2. Ready to answer questions immediately!

## 💡 Try These Queries

### Basic Questions
```
What are AI agents and how do they work in Agno?
What chunking strategies does Agno support?
How can I implement custom tools in Agno?
```

### Advanced Questions
```
How does knowledge retrieval work in Agno?
What types of embeddings does Agno support?
Explain the difference between Teams and Workflows
```

### Deep Dive Questions
```
How can I implement custom knowledge sources in Agno?
What are the best practices for agent memory management?
How do I optimize performance for large knowledge bases?
```

## 🔧 Troubleshooting

### "Module not found" errors

```bash
# Install from the agno repo root
cd /path/to/agno
pip install -e "libs/agno[dev]"
```

### Knowledge base won't load

```bash
# Check your OpenAI API key
echo $OPENAI_API_KEY

# Remove and reload
rm -rf tmp/lancedb
python deep_knowledge.py
```

### Port 7777 already in use

```bash
# Find and kill the process
lsof -ti:7777 | xargs kill -9

# Or change the port in deep_knowledge_os.py
# agent_os = AgentOS(..., port=8888)
```

## 📖 Next Steps

### Production Deployment

For production, use PostgreSQL instead of SQLite:

```bash
# Set database URL
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"

# Run with production settings
python deep_knowledge_os.py
```

### Custom Knowledge Base

Replace the Agno docs with your own content:

```python
# In deep_knowledge_os.py, modify initialize_knowledge_base():
agent_knowledge.add_content(url="https://your-docs.com/content.txt")
# or
agent_knowledge.add_content(path="./your-docs-folder/")
```

### API Integration

Use the OpenAI SDK for easy integration:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:7777/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="deep-knowledge",
    messages=[{"role": "user", "content": "Your question here"}]
)

print(response.choices[0].message.content)
```

## 📚 More Information

- **[README.md](README.md)** - Full documentation with API examples
- **[Agno Documentation](https://docs.agno.com)** - Framework documentation
- **GitHub Issues** - Report bugs or request features

## 🎉 You're Ready!

You now have a production-ready knowledge-based AI agent. The agent will:
- ✅ Search the knowledge base thoroughly (3+ searches per query)
- ✅ Cite all sources
- ✅ Provide comprehensive, well-researched answers
- ✅ Maintain conversation context across sessions
- ✅ Work in both CLI and API modes

Happy researching! 🤔📚
