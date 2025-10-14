"""🚀 DeepKnowledge AgentOS - Production-ready deployment with FastAPI backend

This is the production version of the DeepKnowledge agent, deployed using AgentOS.
It provides a REST API and web UI for interacting with the knowledge base agent.

Key Features:
- FastAPI backend with REST API endpoints
- Web UI for interactive chat
- PostgreSQL support for production
- Session management and persistence
- Streaming responses
- Health checks and monitoring

Setup:
1. Install dependencies: pip install agno openai lancedb tantivy sqlalchemy psycopg2-binary
2. Set environment variables:
   - OPENAI_API_KEY=your_key
   - DATABASE_URL=postgresql://user:pass@host:port/db (optional, uses SQLite if not set)
3. Run: python deep_knowledge_agentos.py

API will be available at: http://localhost:7777
UI will be available at: http://localhost:7777/ui
"""

import os
from textwrap import dedent
from typing import Optional

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.db.sqlite import SqliteDb
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.vectordb.lancedb import LanceDb, SearchType

OPENAI_MODEL_ID = "gpt-4o-mini"
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL for production, SQLite for dev


def initialize_knowledge_base() -> Knowledge:
    """Initialize the knowledge base with Agno documentation.

    The knowledge base persists to disk in 'tmp/lancedb' and only loads content
    on the first run. Subsequent runs reuse the existing embeddings.
    """
    agent_knowledge = Knowledge(
        vector_db=LanceDb(
            uri="tmp/lancedb",
            table_name="deep_knowledge_knowledge",
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
    )

    # Only load content if the knowledge base is empty
    if not agent_knowledge.vector_db.exists():
        print("📥 Loading knowledge base (first run only)...")
        agent_knowledge.add_content(
            url="https://docs.agno.com/llms-full.txt",
        )
        print("✅ Knowledge base loaded successfully!")
    else:
        print("✅ Using existing knowledge base from disk")

    return agent_knowledge


def get_database():
    """Return the appropriate database based on environment configuration.

    Uses PostgreSQL in production (when DATABASE_URL is set) or SQLite for development.
    """
    if DATABASE_URL:
        print(f"🗄️  Using PostgreSQL database")
        return PostgresDb(db_url=DATABASE_URL, table_name="deep_knowledge_sessions")
    else:
        print(f"🗄️  Using SQLite database (set DATABASE_URL for production PostgreSQL)")
        return SqliteDb(session_table="deep_knowledge_sessions", db_file="tmp/agents.db")


def create_deep_knowledge_agent(
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Agent:
    """Create and return a configured DeepKnowledge agent for production use.

    Args:
        session_id: Optional session ID for conversation continuity
        user_id: Optional user ID for personalization and tracking

    Returns:
        Configured Agent instance ready for production use
    """
    agent_knowledge = initialize_knowledge_base()
    agent_db = get_database()

    return Agent(
        name="DeepKnowledge",
        agent_id="deep-knowledge-agent",
        session_id=session_id,
        user_id=user_id,
        model=OpenAIChat(id=OPENAI_MODEL_ID),
        description=dedent("""\
        You are DeepKnowledge, an advanced reasoning agent designed to provide thorough,
        well-researched answers to any query by searching your knowledge base.

        Your strengths include:
        - Breaking down complex topics into manageable components
        - Connecting information across multiple domains
        - Providing nuanced, well-researched answers
        - Maintaining intellectual honesty and citing sources
        - Explaining complex concepts in clear, accessible terms"""),
        instructions=dedent("""\
        Your mission is to leave no stone unturned in your pursuit of the correct answer.

        To achieve this, follow these steps:
        1. **Analyze the input and break it down into key components**.
        2. **Search terms**: You must identify at least 3-5 key search terms to search for.
        3. **Initial Search:** Searching your knowledge base for relevant information. You must make atleast 3 searches to get all relevant information.
        4. **Evaluation:** If the answer from the knowledge base is incomplete, ambiguous, or insufficient - Ask the user for clarification. Do not make informed guesses.
        5. **Iterative Process:**
            - Continue searching your knowledge base till you have a comprehensive answer.
            - Reevaluate the completeness of your answer after each search iteration.
            - Repeat the search process until you are confident that every aspect of the question is addressed.
        4. **Reasoning Documentation:** Clearly document your reasoning process:
            - Note when additional searches were triggered.
            - Indicate which pieces of information came from the knowledge base and where it was sourced from.
            - Explain how you reconciled any conflicting or ambiguous information.
        5. **Final Synthesis:** Only finalize and present your answer once you have verified it through multiple search passes.
            Include all pertinent details and provide proper references.
        6. **Continuous Improvement:** If new, relevant information emerges even after presenting your answer,
            be prepared to update or expand upon your response.

        **Communication Style:**
        - Use clear and concise language.
        - Organize your response with numbered steps, bullet points, or short paragraphs as needed.
        - Be transparent about your search process and cite your sources.
        - Ensure that your final answer is comprehensive and leaves no part of the query unaddressed.

        Remember: **Do not finalize your answer until every angle of the question has been explored.**"""),
        additional_context=dedent("""\
        You should only respond with the final answer and the reasoning process.
        No need to include irrelevant information.

        - User ID: {user_id}
        - Memory: You have access to your previous search results and reasoning process.
        """),
        knowledge=agent_knowledge,
        search_knowledge=True,  # Critical for agentic RAG
        db=agent_db,
        add_history_to_context=True,
        num_history_runs=3,
        read_chat_history=True,
        markdown=True,
        # Production settings
        show_tool_calls=False,  # Hide internal tool calls from users
        debug_mode=False,  # Disable debug output in production
    )


def create_agent_os() -> AgentOS:
    """Create and configure the AgentOS instance for production deployment.

    Returns:
        Configured AgentOS instance with the DeepKnowledge agent
    """
    agent_os = AgentOS(
        name="DeepKnowledge AgentOS",
        agents=[create_deep_knowledge_agent],  # Pass factory function
        db=get_database(),
        # Additional AgentOS configuration
        host="0.0.0.0",  # Listen on all interfaces
        port=7777,
    )

    return agent_os


def main():
    """Main entry point for the AgentOS application."""
    print("\n" + "=" * 80)
    print("🤔 DeepKnowledge AgentOS - Production Deployment")
    print("=" * 80)
    print("\n📚 Advanced Research Assistant with Knowledge Base")
    print("\n🌐 API Endpoints:")
    print("   - REST API: http://localhost:7777/docs")
    print("   - Web UI: http://localhost:7777/ui")
    print("   - Health Check: http://localhost:7777/health")
    print("\n" + "=" * 80 + "\n")

    # Create AgentOS instance
    agent_os = create_agent_os()

    # Get FastAPI app
    app = agent_os.get_app()

    # Run the application
    agent_os.run(reload=False)  # Set reload=True for development


if __name__ == "__main__":
    main()


# API Usage Examples:
"""
# 1. Create a new session and send a message (curl):
curl -X POST "http://localhost:7777/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deep-knowledge-agent",
    "messages": [
      {"role": "user", "content": "What are AI agents and how do they work in Agno?"}
    ],
    "stream": false
  }'

# 2. Continue a conversation with session_id (curl):
curl -X POST "http://localhost:7777/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deep-knowledge-agent",
    "messages": [
      {"role": "user", "content": "Can you give me more details about Teams?"}
    ],
    "session_id": "your-session-id-here",
    "stream": false
  }'

# 3. Streaming responses (curl):
curl -X POST "http://localhost:7777/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deep-knowledge-agent",
    "messages": [
      {"role": "user", "content": "Explain chunking strategies in detail"}
    ],
    "stream": true
  }'

# 4. Python client example:
import requests

response = requests.post(
    "http://localhost:7777/v1/chat/completions",
    json={
        "model": "deep-knowledge-agent",
        "messages": [
            {"role": "user", "content": "What types of embeddings does Agno support?"}
        ],
        "stream": False,
    }
)

print(response.json()["choices"][0]["message"]["content"])

# 5. OpenAI SDK compatibility:
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:7777/v1",
    api_key="dummy-key"  # Not required for local deployment
)

response = client.chat.completions.create(
    model="deep-knowledge-agent",
    messages=[
        {"role": "user", "content": "How does knowledge retrieval work in Agno?"}
    ],
    stream=False
)

print(response.choices[0].message.content)
"""
