#!/usr/bin/env python3
"""
Finance News AgentOS
Web-based interface for the Finance News Agent using agno's AgentOS
"""

from contextlib import asynccontextmanager
import os
from pathlib import Path
import sys

# Add paths for imports from organized structure
current_dir = Path(__file__).parent.parent  # Go up to /src/
project_root = current_dir.parent  # Go up to project root
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "agents"))
sys.path.insert(0, str(current_dir / "utils"))
sys.path.insert(0, str(current_dir / "core"))

from agno.db.postgres import PostgresDb
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# Load environment variables
load_dotenv()

# Import our finance agent and config system
from src.agents.finance_news_agent import create_finance_news_agent
from src.core.cache_manager import (
    CACHE_CONFIGS,
    cache_key_for,
    get_cache_manager,
    init_cache_manager,
)
from src.core.scheduler import get_scheduler, init_scheduler


def safe_timestamp(timestamp_value):
    """Safely convert timestamp to ISO format string"""
    if not timestamp_value:
        return None

    if hasattr(timestamp_value, "isoformat"):
        return timestamp_value.isoformat()
    # Handle integer timestamp
    from datetime import datetime

    try:
        return datetime.fromtimestamp(timestamp_value).isoformat()
    except (ValueError, TypeError):
        return str(timestamp_value)


def create_finance_agentos():
    """Create AgentOS with Finance News Agent"""

    # Create the finance agent with default model
    finance_agent = create_finance_news_agent(model_choice="claude", interactive=False)

    # Set agent name and session handling
    finance_agent.name = "finance-news-agent"
    finance_agent.description = (
        "Specialized Financial News and Market Analysis Agent with real-time data capabilities"
    )

    # Configure database (SQLite by default, PostgreSQL optional)
    if os.getenv("DATABASE_URL"):
        # Use PostgreSQL if configured
        db = PostgresDb(url=os.getenv("DATABASE_URL"), db_schema="finance_agent")
        finance_agent.db = db
    else:
        # Use SQLite as default for lightweight deployment
        db_file = os.getenv("SQLITE_DB_FILE", "finance_agent.db")
        db = SqliteDb(db_file=db_file)
        finance_agent.db = db
        finance_agent.add_history_to_context = True

    # Initialize cache manager
    cache_manager = init_cache_manager(
        redis_host=os.getenv("REDIS_HOST", "localhost"),
        redis_port=int(os.getenv("REDIS_PORT", 6379)),
        cache_db_path=os.getenv("CACHE_DB_PATH", "cache.db"),
        default_ttl=int(os.getenv("CACHE_DEFAULT_TTL", 1800)),
    )

    # Initialize scheduler for daily reports
    scheduler = init_scheduler(finance_agent)
    scheduler.start()

    # Create custom FastAPI app with finance-specific endpoints
    custom_app = FastAPI(
        title="Finance News AgentOS",
        description="Interactive web interface for Financial News and Market Analysis",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @custom_app.get("/", response_class=HTMLResponse)
    async def finance_home():
        """Custom home page for Finance Agent"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Finance News AgentOS</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; margin-bottom: 30px; }
                .header h1 { color: #2c3e50; margin-bottom: 10px; }
                .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0; }
                .feature { background: #ecf0f1; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db; }
                .feature h3 { color: #2c3e50; margin-top: 0; }
                .endpoints { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .endpoint { background: white; margin: 10px 0; padding: 15px; border-radius: 5px; border: 1px solid #dee2e6; }
                .method { display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; margin-right: 10px; }
                .get { background: #28a745; }
                .post { background: #007bff; }
                .status { text-align: center; padding: 20px; background: #d4edda; border-radius: 8px; color: #155724; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💰 Finance News AgentOS</h1>
                    <p>Interactive web interface for Financial News and Market Analysis</p>
                </div>

                <div class="status">
                    <strong>🟢 Agent Status: Online and Ready</strong><br>
                    Advanced financial analysis with real-time market data
                </div>

                <div class="features">
                    <div class="feature">
                        <h3>🏦 Market Analysis</h3>
                        <p>Real-time stock quotes, market indices, and sector performance tracking</p>
                    </div>
                    <div class="feature">
                        <h3>🔍 Enhanced Search</h3>
                        <p>Multi-source financial news with Tavily AI-enhanced search capabilities</p>
                    </div>
                    <div class="feature">
                        <h3>📈 Stock Research</h3>
                        <p>Detailed company analysis with fundamentals and technical indicators</p>
                    </div>
                    <div class="feature">
                        <h3>🪙 Cryptocurrency</h3>
                        <p>Crypto market overview and trending digital asset analysis</p>
                    </div>
                    <div class="feature">
                        <h3>📅 Economic Calendar</h3>
                        <p>Key economic events, indicators, and market-moving announcements</p>
                    </div>
                    <div class="feature">
                        <h3>💾 Persistent Storage</h3>
                        <p>SQLite database for session persistence and conversation history</p>
                    </div>
                </div>

                <div class="endpoints">
                    <h3>🔗 Available Endpoints</h3>

                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/health</strong> - System health check
                    </div>

                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/agents</strong> - List all available agents
                    </div>

                    <div class="endpoint">
                        <span class="method post">POST</span>
                        <strong>/agents/finance-news-agent/runs</strong> - Run financial analysis
                        <br><small>Send multipart/form-data: message="Analyze AAPL stock performance"</small>
                    </div>

                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/sessions</strong> - View chat sessions
                    </div>

                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/docs</strong> - Interactive API documentation
                    </div>

                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/finance/quick-analysis</strong> - Quick market analysis endpoint
                    </div>
                </div>

                <div style="text-align: center; margin-top: 30px;">
                    <p><a href="/docs" style="background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📖 View API Documentation</a></p>
                    <p><strong>Powered by agno AgentOS</strong> | Multi-model AI Support | Real-time Financial Data</p>
                </div>
            </div>
        </body>
        </html>
        """

    @custom_app.get("/finance/quick-analysis")
    async def quick_analysis(symbol: str = "SPY"):
        """Quick market analysis endpoint with caching"""
        try:
            cache_manager = get_cache_manager()
            cache_key = None

            # Try to get from cache first
            if cache_manager:
                cache_key = cache_key_for("quick_analysis", symbol=symbol)
                cached_result = cache_manager.get(cache_key)
                if cached_result:
                    return cached_result

            # Run analysis if not cached
            result = finance_agent.run(f"Provide a brief analysis of {symbol}")

            response = {
                "symbol": symbol,
                "analysis": str(result.content),
                "timestamp": safe_timestamp(result.created_at),
                "cached": False,
            }

            # Cache the result
            if cache_manager and cache_key:
                ttl_value = CACHE_CONFIGS["quick_analysis"]["ttl"]
                cache_manager.set(cache_key, response, ttl_value if isinstance(ttl_value, int) else 1800)

            return response
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    @custom_app.get("/finance/market-overview")
    async def market_overview():
        """Market overview endpoint with caching"""
        try:
            cache_manager = get_cache_manager()
            cache_key = None

            # Try to get from cache first
            if cache_manager:
                cache_key = cache_key_for("market_overview")
                cached_result = cache_manager.get(cache_key)
                if cached_result:
                    return cached_result

            # Run analysis if not cached
            result = finance_agent.run(
                "Provide a comprehensive market overview including major indices, sectors, and economic indicators"
            )

            response = {
                "overview": str(result.content),
                "timestamp": safe_timestamp(result.created_at),
                "cached": False,
            }

            # Cache the result
            if cache_manager and cache_key:
                cache_manager.set(cache_key, response, CACHE_CONFIGS["market_overview"]["ttl"])

            return response
        except Exception as e:
            return {"error": str(e)}

    @custom_app.get("/cache/stats")
    async def cache_stats():
        """Get cache statistics"""
        try:
            cache_manager = get_cache_manager()
            if cache_manager:
                stats = cache_manager.get_cache_stats()
                return {"cache_stats": stats}
            return {"error": "Cache manager not initialized"}
        except Exception as e:
            return {"error": str(e)}

    @custom_app.get("/cache/clear")
    async def clear_cache():
        """Clear expired cache entries"""
        try:
            cache_manager = get_cache_manager()
            if cache_manager:
                cache_manager.clear_expired()
                return {"message": "Expired cache entries cleared"}
            return {"error": "Cache manager not initialized"}
        except Exception as e:
            return {"error": str(e)}

    @custom_app.get("/scheduler/status")
    async def scheduler_status():
        """Get scheduler status"""
        try:
            scheduler = get_scheduler()
            if scheduler:
                status = scheduler.get_task_status()
                return {"scheduler": status}
            return {"error": "Scheduler not initialized"}
        except Exception as e:
            return {"error": str(e)}

    # Create AgentOS with our finance agent and custom app
    agentos = AgentOS(
        agents=[finance_agent],
        base_app=custom_app,
        on_route_conflict="preserve_base_app",  # Preserve our custom endpoints
    )

    return agentos


@asynccontextmanager
async def lifespan(app):
    """Custom lifespan manager for startup/shutdown"""
    print("🚀 Finance News AgentOS starting up...")
    print("💰 Finance agent initialized with multi-model support")

    # Check API keys
    api_keys = []
    if os.getenv("ANTHROPIC_API_KEY"):
        api_keys.append("Claude")
    if os.getenv("OPENAI_API_KEY"):
        api_keys.append("OpenAI")
    if os.getenv("TAVILY_API_KEY"):
        api_keys.append("Tavily")

    print(f"🔑 Available AI models: {', '.join(api_keys) if api_keys else 'Claude (default)'}")

    yield

    print("🛑 Finance News AgentOS shutting down...")


def main():
    """Main function to run the AgentOS"""
    print("🏦 Starting Finance News AgentOS...")

    # Check required environment variables
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not found. Please set it in your .env file.")
        print("💡 The agent will not work without an API key.")
        return

    # Create AgentOS
    agentos = create_finance_agentos()

    # Get the FastAPI app
    app = agentos.get_app()
    app.router.lifespan_context = lifespan

    # Print startup information
    print("\n" + "=" * 60)
    print("🏦 Finance News AgentOS Ready!")
    print("=" * 60)
    print("🌐 Web Interface: http://localhost:8080")
    print("📖 API Docs: http://localhost:8080/docs")
    print("🔍 Quick Analysis: http://localhost:8080/finance/quick-analysis?symbol=AAPL")
    print("📊 Market Overview: http://localhost:8080/finance/market-overview")
    print("=" * 60)

    # Check database configuration
    if os.getenv("DATABASE_URL"):
        print("💾 Database: PostgreSQL (configured)")
    else:
        db_file = os.getenv("SQLITE_DB_FILE", "finance_agent.db")
        print(f"💾 Database: SQLite ({db_file})")
        print("💡 Set DATABASE_URL for PostgreSQL or SQLITE_DB_FILE for custom SQLite location")

    print("\n🚀 Starting server on http://localhost:8080")

    # Run the server
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        reload=False,  # Set to True for development
        log_level="info",
    )


if __name__ == "__main__":
    main()
