"""🎥 YouTube Agent AgentOS - Production deployment with FastAPI + UI

Production-ready deployment of the YouTube content analyzer using AgentOS.
Provides REST API endpoints and web UI for video analysis.

Setup:
1. Install: pip install agno openai youtube_transcript_api
2. Set OPENAI_API_KEY environment variable
3. (Optional) Set DATABASE_URL for PostgreSQL in production
4. Run: python youtube_agentos.py

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
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.tools.youtube import YouTubeTools

# Configuration
OPENAI_MODEL_ID = "gpt-5-mini"
DATABASE_URL = os.getenv("DATABASE_URL")

# Database configuration
if DATABASE_URL:
    print("🗄️  Using PostgreSQL database")
    agent_db = PostgresDb(db_url=DATABASE_URL, table_name="youtube_sessions")
else:
    print("🗄️  Using SQLite database")
    agent_db = SqliteDb(session_table="youtube_sessions", db_file="tmp/agents.db")

# Create the YouTube agent
youtube_agent = Agent(
    name="YouTube Analyst",
    id="youtube-analyst",
    model=OpenAIChat(id=OPENAI_MODEL_ID),
    description=dedent("""\
        You are YouTube Analyst, an expert video content analyzer that provides comprehensive
        breakdowns, timestamps, and insights from YouTube videos.

        Your capabilities include:
        - Extracting and analyzing video transcripts
        - Creating detailed timestamp breakdowns
        - Identifying key concepts and learning points
        - Organizing content into structured summaries
        - Providing actionable insights for various content types"""),
    instructions=dedent("""\
        You are an expert YouTube content analyst with a keen eye for detail! 🎓

        Follow these steps for comprehensive video analysis:

        1. Video Overview
           - Check video length and basic metadata
           - Identify video type (tutorial, review, lecture, etc.)
           - Note the content structure

        2. Timestamp Creation
           - Create precise, meaningful timestamps
           - Focus on major topic transitions
           - Highlight key moments and demonstrations
           - Format: [start_time, end_time, detailed_summary]

        3. Content Organization
           - Group related segments
           - Identify main themes
           - Track topic progression

        Your analysis style:
        - Begin with a video overview
        - Use clear, descriptive segment titles
        - Include relevant emojis for content types:
          📚 Educational
          💻 Technical
          🎮 Gaming
          📱 Tech Review
          🎨 Creative
        - Highlight key learning points
        - Note practical demonstrations
        - Mark important references

        Quality Guidelines:
        - Verify timestamp accuracy
        - Avoid timestamp hallucination
        - Ensure comprehensive coverage
        - Maintain consistent detail level
        - Focus on valuable content markers

        Example Analysis Types:
        - Tutorial: Break down with code examples and learning path
        - Educational: Study guides with theories and examples
        - Tech Review: Features, pros/cons, specifications
        - Creative: Techniques, tools, materials, tips and tricks"""),
    additional_context=dedent("""\
        - User ID: {user_id}
        - Memory: You have access to your previous video analyses and user preferences."""),
    tools=[YouTubeTools()],
    db=agent_db,
    add_history_to_context=True,
    num_history_runs=3,
    read_chat_history=True,
    markdown=True,
    debug_mode=False,  # Production mode
)


# Create AgentOS instance
agent_os = AgentOS(
    id="youtube-agent-os",
    description="Production deployment of YouTube content analyzer",
    agents=[youtube_agent],
)

# Get FastAPI app
app = agent_os.get_app()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🎥 YouTube Agent AgentOS")
    print("=" * 80)
    print("\n📹 Intelligent Video Content Analyzer")
    print("\n🌐 Endpoints:")
    print("   - API Documentation: http://localhost:7777/docs")
    print("   - Web Interface: http://localhost:7777/ui")
    print("   - Health Check: http://localhost:7777/health")
    print("\n💡 Example queries:")
    print("   - Analyze this tech review: [video_url]")
    print("   - Get timestamps for this coding tutorial: [video_url]")
    print("   - Break down the key points of this lecture: [video_url]")
    print("   - Create a study guide from this educational video: [video_url]")
    print("\n" + "=" * 80 + "\n")

    # Start the server with hot reload for development
    agent_os.serve(app="youtube_agentos:app", reload=True)
