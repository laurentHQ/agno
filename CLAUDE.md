# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Development Commands

### Setup and Installation
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Agno framework
pip install -U agno

# For development, install with dev dependencies
pip install -e "libs/agno[dev]"
```

### Validation and Testing
```bash
# Validate entire codebase (linting and type checking)
./scripts/validate.sh

# Validate just the Agno library
./libs/agno/scripts/validate.sh

# Run specific validation tools
ruff check libs/agno
mypy libs/agno --config-file libs/agno/pyproject.toml
```

### Running Examples
```bash
# Run cookbook examples
python cookbook/path/to/example.py

# Run the sample HackerNews agent
python hackernews_agent.py
```

## Architecture Overview

### Monorepo Structure
- `libs/agno/` - Core Agno framework library with agent, team, and workflow abstractions
- `libs/agno_infra/` - Infrastructure and deployment components
- `cookbook/` - Comprehensive examples organized by feature and complexity
- `scripts/` - Build, validation, and utility scripts

### Core Abstractions (in order of complexity)

1. **Agent** - Single autonomous AI agent with tools, instructions, and optional knowledge
2. **Team** - Collection of specialized agents that coordinate autonomously via LLM
3. **Workflow** - Programmatic step-based orchestration with conditional logic
4. **AgentOS** - Production runtime with FastAPI backend and UI for serving agents

### Key Design Principles

**Performance-Critical Rules:**
- NEVER create agents in loops - instantiate once and reuse (3μs instantiation vs significant overhead)
- Always use `output_schema` for structured responses with Pydantic models
- PostgreSQL for production, SQLite for development only
- Start with single agent, scale to teams/workflows only when needed

**Agent Patterns:**
- Single Agent (90% use cases): One clear task domain with tools + instructions
- Team: Multiple specialized agents, autonomous coordination, complex multi-perspective tasks
- Workflow: Sequential steps, conditional logic, full programmatic control

### Essential Components

**Models**: Brain of agents - supports OpenAI, Anthropic, Google, AWS Bedrock, and 20+ others

**Tools**: Enable agents to perform actions - web search, SQL, APIs, file operations, etc.

**Knowledge**: RAG capability with vector databases for runtime information retrieval

**Memory**: Persistent user insights and personalization across conversations

**Storage**: Database backends (Postgres, SQLite, MongoDB, etc.) for session/state persistence

## Development Guidelines

### Agent Creation Patterns
```python
# Basic agent
from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    instructions="You are a helpful assistant",
    markdown=True,
)

# Agent with tools and knowledge
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    knowledge=knowledge_base,
    search_knowledge=True,  # Critical for agentic RAG
    output_schema=StructuredOutput,  # Always use for structured responses
)
```

### Common Anti-Patterns to Avoid
- Creating agents in loops (massive performance penalty)
- Using Team when single agent suffices
- Forgetting `search_knowledge=True` with knowledge bases
- Using SQLite in production environments
- Missing `output_schema` for structured data
- Not adding chat history when context matters

### Performance Considerations
- Agent instantiation: ~3μs average, ~6.5KB memory footprint
- Reuse agent instances across multiple queries
- Use structured output schemas for validation
- Enable appropriate debugging levels for environment

### Environment Configuration
```bash
# Required API keys for models
export OPENAI_API_KEY=***
export ANTHROPIC_API_KEY=***
export GOOGLE_API_KEY=***

# Optional: Disable telemetry
export AGNO_TELEMETRY=false
```

## Production Deployment

Use AgentOS for production serving:
```python
from agno.os import AgentOS
from agno.db.postgres import PostgresDb

agent_os = AgentOS(
    agents=[agent],
    db=PostgresDb(db_url=os.getenv("DATABASE_URL")),
)
app = agent_os.get_app()  # Returns FastAPI app
```

Configure production settings:
- Use PostgresDb, not SqliteDb
- Set `show_tool_calls=False`, `debug_mode=False`
- Wrap `agent.run()` in try-except blocks
- Implement proper logging and monitoring