"""🚀 DeepKnowledge AgentOS - Production deployment with FastAPI + UI

Production-ready deployment of the DeepKnowledge agent using AgentOS.
Provides REST API endpoints and web UI for knowledge-based Q&A.

Setup:
1. Install: pip install agno openai lancedb tantivy sqlalchemy psycopg2-binary
2. Set OPENAI_API_KEY environment variable
3. (Optional) Set DATABASE_URL for PostgreSQL in production
4. Run: python deep_knowledge_os.py

Access:
- API docs: http://localhost:7777/docs
- Web UI: http://localhost:7777/ui
- Health: http://localhost:7777/health
"""

import os
from textwrap import dedent

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.db.sqlite import SqliteDb
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.vectordb.lancedb import LanceDb, SearchType

# Configuration
OPENAI_MODEL_ID = "gpt-5-mini"
DATABASE_URL = os.getenv("DATABASE_URL")


def initialize_knowledge_base() -> Knowledge:
    """Initialize persistent knowledge base with Agno documentation.

    Checks if the database exists and has content. If empty, loads the documentation.
    """
    agent_knowledge = Knowledge(
        vector_db=LanceDb(
            uri="tmp/lancedb",
            table_name="deep_knowledge_kb",
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
    )

    # Check if knowledge base exists and has content
    db_exists = agent_knowledge.vector_db.exists()

    if not db_exists:
        print("📥 Knowledge base not found. Loading documentation...")
        agent_knowledge.add_content(url="https://docs.agno.com/llms-full.txt")
        print("✅ Knowledge base loaded successfully!")
    else:
        # Database exists, but check if it's empty
        try:
            # Try to get document count
            import lancedb
            db = lancedb.connect(agent_knowledge.vector_db.uri)
            table = db.open_table(agent_knowledge.vector_db.table_name)
            doc_count = table.count_rows()

            if doc_count == 0:
                print("⚠️  Knowledge base exists but is empty. Loading documentation...")
                agent_knowledge.add_content(url="https://docs.agno.com/llms-full.txt")
                print("✅ Knowledge base loaded successfully!")
            else:
                print(f"✅ Using existing knowledge base ({doc_count:,} chunks)")
        except Exception as e:
            print(f"⚠️  Could not verify database content: {e}")
            print("📥 Reloading knowledge base to be safe...")
            agent_knowledge.add_content(url="https://docs.agno.com/llms-full.txt")
            print("✅ Knowledge base loaded successfully!")

    return agent_knowledge


# Initialize knowledge base once at module level
knowledge_base = initialize_knowledge_base()

# Database configuration
if DATABASE_URL:
    print("🗄️  Using PostgreSQL database")
    agent_db = PostgresDb(db_url=DATABASE_URL, table_name="deep_knowledge_sessions")
else:
    print("🗄️  Using SQLite database")
    agent_db = SqliteDb(session_table="deep_knowledge_sessions", db_file="tmp/agents.db")


# Create the DeepKnowledge agent
deep_knowledge = Agent(
    name="DeepKnowledge",
    id="deep-knowledge",
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
    knowledge=knowledge_base,
    search_knowledge=True,  # Enable agentic RAG
    db=agent_db,
    add_history_to_context=True,
    num_history_runs=3,
    read_chat_history=True,
    markdown=True,
    debug_mode=False,  # Production mode
)


# Create AgentOS instance
agent_os = AgentOS(
    id="deep-knowledge-os",
    description="Production deployment of DeepKnowledge research assistant",
    agents=[deep_knowledge],
)

# Get FastAPI app
app = agent_os.get_app()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🤔 DeepKnowledge AgentOS")
    print("=" * 80)
    print("\n📚 Advanced Research Assistant with Knowledge Base")
    print("\n🌐 Endpoints:")
    print("   - API Documentation: http://localhost:7777/docs")
    print("   - Web Interface: http://localhost:7777/ui")
    print("   - Health Check: http://localhost:7777/health")
    print("\n💡 Example queries:")
    print("   - What are AI agents and how do they work in Agno?")
    print("   - What chunking strategies does Agno support?")
    print("   - How does knowledge retrieval work in Agno?")
    print("\n" + "=" * 80 + "\n")

    # Start the server with hot reload for development
    agent_os.serve(app="deep_knowledge_os:app", reload=True)
