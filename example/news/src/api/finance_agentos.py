#!/usr/bin/env python3
"""
Finance News AgentOS - Production Deployment Version
Web-based interface for the Finance News Agent with configuration support
"""

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
from src.utils.config_loader import load_agentos_config, validate_agentos_config


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


def create_finance_agentos(config_file: str = None):
    """Create AgentOS with Finance News Agent using configuration"""

    # Load configuration
    try:
        config = load_agentos_config(config_file)
        print(f"📋 Loaded configuration - Primary model: {config.primary_model}")
    except Exception as e:
        print(f"⚠️  Configuration loading failed: {e}")
        print("🔄 Falling back to environment variables...")
        config = None

    # Create the finance agent with configured model
    if config:
        model_choice = config.primary_model
        interactive = config.agent.interactive
        model_config = config.models.get(model_choice)
        if model_config:
            print(f"🤖 Using {model_config.display_name}")
    else:
        # Fallback to environment variables
        model_choice = os.getenv("FINANCE_AGENT_MODEL", "openai")
        interactive = False
        print(f"🤖 Using model from environment: {model_choice.upper()}")

    # Get debug mode
    if config:
        debug_mode = config.agent.debug_mode
    else:
        debug_mode = os.getenv("DEBUG_MODE", "false").lower() in ("true", "1", "yes")

    if debug_mode:
        print(f"🐛 Debug mode: ENABLED")

    finance_agent = create_finance_news_agent(model_choice=model_choice, interactive=interactive)

    # Set agent name and session handling from config
    if config:
        finance_agent.name = config.agent.name
        finance_agent.description = config.agent.description
        finance_agent.markdown = config.agent.markdown
        finance_agent.debug_mode = config.agent.debug_mode
        if debug_mode:
            finance_agent.show_tool_calls = True
    else:
        finance_agent.name = "finance-news-agent"
        finance_agent.description = (
            "Specialized Financial News and Market Analysis Agent with real-time data capabilities"
        )
        finance_agent.debug_mode = debug_mode
        if debug_mode:
            finance_agent.show_tool_calls = True

    # Configure database
    if config and config.database.type == "postgres":
        # Use PostgreSQL URL from config or fall back to environment variable
        db_url = config.database.postgresql_url or os.getenv("DATABASE_URL")
        if not db_url:
            print("❌ PostgreSQL selected but no URL configured in config file or DATABASE_URL environment variable")
            print("💡 Add 'url' under database.postgresql in config file or set DATABASE_URL environment variable")
            raise ValueError("PostgreSQL URL not configured")
        db = PostgresDb(db_url=db_url, db_schema=config.database.postgresql_schema)
        finance_agent.db = db
        print(f"💾 Using PostgreSQL database: {config.database.postgresql_schema}")
    elif config and config.database.type == "sqlite":
        # Use SQLite from config
        db_file = config.database.sqlite_db_file
        db = SqliteDb(db_file=db_file)
        finance_agent.db = db
        finance_agent.add_history_to_context = config.database.sqlite_enable_history
        print(f"💾 Using SQLite database: {db_file}")
    else:
        # Fallback to environment variables
        if os.getenv("DATABASE_URL"):
            db = PostgresDb(db_url=os.getenv("DATABASE_URL"), db_schema="finance_agent")
            finance_agent.db = db
            print(f"💾 Using PostgreSQL from DATABASE_URL")
        else:
            db_file = os.getenv("SQLITE_DB_FILE", "finance_agent.db")
            db = SqliteDb(db_file=db_file)
            finance_agent.db = db
            finance_agent.add_history_to_context = True
            print(f"💾 Using SQLite: {db_file}")

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

    # Create AgentOS with our finance agent
    agentos = AgentOS(
        agents=[finance_agent],
    )

    # Add our custom endpoints to the AgentOS app
    app = agentos.get_app()

    # Add custom home page with interactive chat (moved from root to avoid conflicts)
    @app.get("/finance", response_class=HTMLResponse)
    @app.get("/finance/home", response_class=HTMLResponse)
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
                .status { text-align: center; padding: 15px; background: #d4edda; border-radius: 8px; color: #155724; margin: 20px 0; }
                .chat-section { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #dee2e6; }
                .chat-input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; resize: vertical; }
                .chat-button { background: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; margin-top: 10px; }
                .chat-button:hover { background: #2980b9; }
                .chat-response { background: white; padding: 15px; border-radius: 4px; margin-top: 15px; border: 1px solid #ddd; white-space: pre-wrap; max-height: 400px; overflow-y: auto; }
                .loading { display: none; color: #666; font-style: italic; }
                .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin: 30px 0; }
                .feature { background: #ecf0f1; padding: 15px; border-radius: 8px; border-left: 4px solid #3498db; }
                .feature h3 { color: #2c3e50; margin-top: 0; font-size: 16px; }
                .feature p { margin: 5px 0 0 0; font-size: 14px; color: #555; }
                .endpoints { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .endpoint { background: white; margin: 10px 0; padding: 12px; border-radius: 5px; border: 1px solid #dee2e6; }
                .method { display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; margin-right: 10px; font-size: 12px; }
                .get { background: #28a745; }
                .post { background: #007bff; }
                a { color: #3498db; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💰 Finance News AgentOS</h1>
                    <p>AI-Powered Financial Analysis & Market Intelligence</p>
                </div>

                <div class="status">
                    <strong>🟢 Agent Status: Online and Ready</strong><br>
                    Real-time market data • Multi-source news • Advanced AI analysis
                </div>

                <h2>💬 Interactive Agent Chat</h2>
                <div class="chat-section">
                    <h3>Chat with Finance News Agent</h3>
                    <textarea id="messageInput" class="chat-input" rows="3" placeholder="Ask about stocks, market analysis, or financial news... (e.g., 'What is the current price and analysis for AAPL?')"></textarea>
                    <button class="chat-button" onclick="sendMessage()">Send Message</button>
                    <div class="loading" id="loading">Analyzing your request...</div>
                    <div id="response" class="chat-response" style="display: none;"></div>
                </div>

                <div class="features">
                    <div class="feature">
                        <h3>🏦 Market Analysis</h3>
                        <p>Real-time quotes, indices, sector performance</p>
                    </div>
                    <div class="feature">
                        <h3>🔍 Enhanced Search</h3>
                        <p>Tavily & Brave AI-powered news search</p>
                    </div>
                    <div class="feature">
                        <h3>📈 Stock Research</h3>
                        <p>Fundamentals & technical indicators</p>
                    </div>
                    <div class="feature">
                        <h3>🪙 Cryptocurrency</h3>
                        <p>Crypto market overview & analysis</p>
                    </div>
                    <div class="feature">
                        <h3>📅 Economic Calendar</h3>
                        <p>Key events & market indicators</p>
                    </div>
                    <div class="feature">
                        <h3>💾 Session History</h3>
                        <p>Persistent conversations & analytics</p>
                    </div>
                </div>

                <div class="endpoints">
                    <h3>🔗 API Endpoints</h3>

                    <div class="endpoint">
                        <span class="method post">POST</span>
                        <strong>/agents/finance-news-agent/runs</strong> - Run financial analysis
                        <br><small>Send multipart/form-data: message="Your question"</small>
                    </div>

                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong><a href="/finance/quick-analysis?symbol=AAPL">/finance/quick-analysis?symbol=AAPL</a></strong> - Quick stock analysis
                    </div>

                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong><a href="/finance/market-overview">/finance/market-overview</a></strong> - Comprehensive market overview
                    </div>

                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong><a href="/cache/stats">/cache/stats</a></strong> - Cache performance stats
                    </div>

                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong><a href="/scheduler/status">/scheduler/status</a></strong> - Background tasks status
                    </div>

                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong><a href="/docs">/docs</a></strong> - Interactive API documentation
                    </div>
                </div>

                <div style="text-align: center; margin-top: 30px;">
                    <p><a href="/docs" style="background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">📖 View Full API Documentation</a></p>
                    <p style="color: #7f8c8d; margin-top: 20px;"><strong>Powered by Agno AgentOS</strong> | Multi-Model AI | Real-Time Financial Data</p>
                </div>
            </div>

            <script>
            async function sendMessage() {
                const messageInput = document.getElementById('messageInput');
                const loading = document.getElementById('loading');
                const responseDiv = document.getElementById('response');

                const message = messageInput.value.trim();
                if (!message) {
                    alert('Please enter a message');
                    return;
                }

                // Show loading
                loading.style.display = 'block';
                responseDiv.style.display = 'none';

                try {
                    // Create FormData for multipart/form-data request
                    const formData = new FormData();
                    formData.append('message', message);

                    const response = await fetch('/agents/finance-news-agent/runs', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    const data = await response.json();

                    // Display response
                    responseDiv.textContent = data.content || JSON.stringify(data, null, 2);
                    responseDiv.style.display = 'block';

                } catch (error) {
                    responseDiv.textContent = `Error: ${error.message}`;
                    responseDiv.style.display = 'block';
                } finally {
                    loading.style.display = 'none';
                }
            }

            // Allow Enter key to send message (Shift+Enter for new line)
            document.getElementById('messageInput').addEventListener('keydown', function(event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    sendMessage();
                }
            });
            </script>
        </body>
        </html>
        """

    @app.get("/finance/quick-analysis")
    async def quick_analysis(symbol: str = "AAPL"):
        """Quick financial analysis for a symbol"""
        try:
            cache_manager = get_cache_manager()
            cache_key = None

            # Try to get from cache first
            if cache_manager:
                cache_key = cache_key_for("quick_analysis", symbol=symbol)
                cached_result = cache_manager.get(cache_key)
                if cached_result:
                    cached_result["cached"] = True
                    return cached_result

            # Run analysis if not cached
            prompt = f"Provide a quick financial analysis and current market sentiment for {symbol}. Include key metrics, recent price movement, and analyst sentiment."
            result = finance_agent.run(prompt)

            response = {
                "symbol": symbol,
                "analysis": str(result.content),
                "timestamp": safe_timestamp(result.created_at),
                "model_used": result.model if hasattr(result, "model") else "Unknown",
                "agent": finance_agent.name,
                "cached": False,
            }

            # Cache the result
            if cache_manager and cache_key:
                ttl_value = CACHE_CONFIGS["quick_analysis"]["ttl"]
                cache_manager.set(cache_key, response, ttl_value if isinstance(ttl_value, int) else 1800)

            return response
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    @app.get("/finance/market-overview")
    async def market_overview():
        """Get comprehensive market overview with AI analysis"""
        try:
            cache_manager = get_cache_manager()
            cache_key = None

            # Try to get from cache first
            if cache_manager:
                cache_key = cache_key_for("market_overview")
                cached_result = cache_manager.get(cache_key)
                if cached_result:
                    cached_result["cached"] = True
                    return cached_result

            from datetime import datetime

            # Let the agent use its tools to get market data and analyze
            prompt = "Provide comprehensive market overview with current data and sector performance analysis. Include trending stocks and key market movers."

            result = finance_agent.run(prompt)

            response = {
                "analysis": str(result.content),
                "timestamp": datetime.now().isoformat(),
                "model_used": result.model if hasattr(result, "model") else "Unknown",
                "agent": finance_agent.name,
                "cached": False,
            }

            # Cache the result
            if cache_manager and cache_key:
                ttl_value = CACHE_CONFIGS["market_overview"]["ttl"]
                cache_manager.set(cache_key, response, ttl_value if isinstance(ttl_value, int) else 1800)

            return response
        except Exception as e:
            return {"error": str(e)}

    @app.get("/cache/stats")
    async def cache_stats():
        """Get cache statistics"""
        try:
            cache_manager = get_cache_manager()
            if cache_manager:
                return cache_manager.get_cache_stats()
            return {"error": "Cache manager not initialized"}
        except Exception as e:
            return {"error": str(e)}

    @app.get("/cache/clear")
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

    @app.get("/scheduler/status")
    async def scheduler_status():
        """Get scheduler status"""
        try:
            scheduler = get_scheduler()
            if scheduler:
                return scheduler.get_task_status()
            return {"error": "Scheduler not initialized"}
        except Exception as e:
            return {"error": str(e)}

    return agentos, app


def main(config_file: str = None):
    """Main function to run the AgentOS"""
    print("🏦 Starting Finance News AgentOS...")

    # Validate configuration first
    print("🔧 Validating configuration...")
    if not validate_agentos_config(config_file):
        print("❌ Configuration validation failed. Please check your config and API keys.")
        return

    # Create AgentOS with configuration
    agentos, app = create_finance_agentos(config_file)

    # Load server configuration
    try:
        from src.utils.config_loader import load_agentos_config
        config = load_agentos_config(config_file)
        host = config.server.host
        port = config.server.port
        reload = config.server.reload
        log_level = config.server.log_level
        configured_model = config.primary_model
    except:
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 7777))
        reload = False
        log_level = "info"
        configured_model = os.getenv("FINANCE_AGENT_MODEL", "openai")

    # Print startup information
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() in ("true", "1", "yes")

    print("\n" + "=" * 60)
    print("🏦 Finance News AgentOS Ready!")
    print("=" * 60)
    print(f"🤖 Active Model: {configured_model.upper()}")
    if debug_mode:
        print(f"🐛 Debug Mode: ENABLED")
    print(f"🌐 Finance UI: http://localhost:{port}/finance")
    print(f"🏠 AgentOS UI: http://localhost:{port}/")
    print(f"📖 API Docs: http://localhost:{port}/docs")
    print(f"🔍 Quick Analysis: http://localhost:{port}/finance/quick-analysis?symbol=AAPL")
    print(f"📊 Market Overview: http://localhost:{port}/finance/market-overview")
    print("=" * 60)

    # Check database configuration
    if os.getenv("DATABASE_URL"):
        print("💾 Database: PostgreSQL")
    else:
        db_file = os.getenv("SQLITE_DB_FILE", "finance_agent.db")
        print(f"💾 Database: SQLite ({db_file})")

    # Check API keys
    api_keys = []
    if os.getenv("ANTHROPIC_API_KEY"):
        api_keys.append("Claude ✅")
    if os.getenv("OPENAI_API_KEY"):
        api_keys.append("OpenAI ✅")
    if os.getenv("TAVILY_API_KEY"):
        api_keys.append("Tavily ✅")
    if os.getenv("BRAVE_API_KEY"):
        api_keys.append("Brave ✅")

    print(f"🔑 Available services: {' | '.join(api_keys) if api_keys else 'Basic (no enhanced services)'}")

    print(f"\n🚀 Starting server on http://{host}:{port}")

    # Run the server
    import uvicorn

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Default config file path (relative to this script)
    default_config = Path(__file__).parent.parent.parent / "config" / "agentos_config.yaml"

    # Allow override from command line: python finance_agentos.py path/to/config.yaml
    config_file = sys.argv[1] if len(sys.argv) > 1 else str(default_config)

    main(config_file)
