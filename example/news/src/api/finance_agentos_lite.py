#!/usr/bin/env python3
"""
Finance News AgentOS - Lightweight SQLite Version
Simplified web interface for the Finance News Agent using SQLite database
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


def create_finance_agentos_lite(config_file: str = None):
    """Create lightweight AgentOS with Finance News Agent using configuration"""

    # Load configuration
    try:
        config = load_agentos_config(config_file)
        print(f"📋 Loaded configuration - Primary model: {config.primary_model}")
    except Exception as e:
        print(f"⚠️  Configuration loading failed: {e}")
        print("🔄 Falling back to default configuration...")
        # Fallback to default settings
        config = None

    # Create the finance agent with configured model
    if config:
        model_choice = config.primary_model
        interactive = config.agent.interactive
        model_config = config.models.get(model_choice)
        if model_config:
            print(f"🤖 Using {model_config.display_name}")
    else:
        model_choice = "claude"
        interactive = False

    finance_agent = create_finance_news_agent(model_choice=model_choice, interactive=interactive)

    # Set agent name and session handling from config
    if config:
        finance_agent.name = config.agent.name
        finance_agent.description = config.agent.description
        finance_agent.markdown = config.agent.markdown
        finance_agent.debug_mode = config.agent.debug_mode
    else:
        finance_agent.name = "finance-news-agent"
        finance_agent.description = (
            "Specialized Financial News and Market Analysis Agent with SQLite persistence"
        )
        finance_agent.debug_mode = False

    # Configure database from config
    if config and config.database.type == "sqlite":
        db_file = config.database.sqlite_db_file
        enable_history = config.database.sqlite_enable_history
    else:
        db_file = os.getenv("SQLITE_DB_FILE", "finance_agent.db")
        enable_history = True

    db = SqliteDb(db_file=db_file)
    finance_agent.db = db
    finance_agent.add_history_to_context = enable_history

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

    # AgentOS will create its own FastAPI app with proper configuration

    # Create AgentOS with our finance agent
    # Don't use base_app to avoid route conflicts - let AgentOS handle routing
    agentos = AgentOS(
        agents=[finance_agent],
        # Remove base_app to let AgentOS create its own FastAPI instance
        # base_app=custom_app,
    )

    # Add our custom endpoints to the AgentOS app
    app = agentos.get_app()

    # Add custom home page
    @app.get("/", response_class=HTMLResponse)
    async def finance_home():
        """Custom home page for Finance Agent"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Finance News AgentOS Lite</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
                .endpoint code { background: #2c3e50; color: white; padding: 2px 6px; border-radius: 3px; }
                .agent-endpoint { border-left-color: #e74c3c; }
                .custom-endpoint { border-left-color: #27ae60; }
                .status { background: #d5f4e6; padding: 10px; border-radius: 5px; margin: 20px 0; }
                .chat-section { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #dee2e6; }
                .chat-input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; resize: vertical; }
                .chat-button { background: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; margin-top: 10px; }
                .chat-button:hover { background: #2980b9; }
                .chat-response { background: white; padding: 15px; border-radius: 4px; margin-top: 15px; border: 1px solid #ddd; white-space: pre-wrap; max-height: 400px; overflow-y: auto; }
                .loading { display: none; color: #666; font-style: italic; }
                a { color: #3498db; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏦 Finance News AgentOS Lite</h1>
                <div class="status">
                    <strong>Status:</strong> ✅ Running | <strong>Database:</strong> SQLite | <strong>Mode:</strong> Lightweight
                </div>

                <h2>💬 Interactive Agent Chat</h2>
                <div class="chat-section">
                    <h3>Chat with Finance News Agent</h3>
                    <textarea id="messageInput" class="chat-input" rows="3" placeholder="Ask about stocks, market analysis, or financial news... (e.g., 'What is the current price and analysis for AAPL?')"></textarea>
                    <button class="chat-button" onclick="sendMessage()">Send Message</button>
                    <div class="loading" id="loading">Sending message to agent...</div>
                    <div id="response" class="chat-response" style="display: none;"></div>
                </div>

                <h2>📡 AgentOS Standard Endpoints</h2>
                <div class="endpoint agent-endpoint">
                    <strong>Agent Chat:</strong> <code>POST /agents/finance-news-agent/runs</code><br>
                    <small>Send messages to the finance news agent via standard AgentOS API (multipart/form-data)</small>
                </div>

                <h2>💰 Custom Finance Endpoints</h2>
                <div class="endpoint custom-endpoint">
                    <strong>Quick Analysis:</strong> <a href="/finance/quick-analysis?symbol=AAPL"><code>GET /finance/quick-analysis?symbol=AAPL</code></a><br>
                    <small>Get quick financial analysis for any stock symbol</small>
                </div>
                <div class="endpoint custom-endpoint">
                    <strong>Market Overview:</strong> <a href="/finance/market-overview"><code>GET /finance/market-overview</code></a><br>
                    <small>Comprehensive market overview and trends</small>
                </div>

                <h2>🔧 System Endpoints</h2>
                <div class="endpoint">
                    <strong>Cache Stats:</strong> <a href="/cache/stats"><code>GET /cache/stats</code></a><br>
                    <small>View cache performance and statistics</small>
                </div>
                <div class="endpoint">
                    <strong>Scheduler Status:</strong> <a href="/scheduler/status"><code>GET /scheduler/status</code></a><br>
                    <small>View background task scheduler status</small>
                </div>

                <h2>📚 Documentation</h2>
                <div class="endpoint">
                    <strong>API Documentation:</strong> <a href="/docs"><code>GET /docs</code></a><br>
                    <small>Interactive Swagger/OpenAPI documentation</small>
                </div>

                <hr style="margin: 30px 0;">
                <p><em>Finance News AgentOS Lite - Powered by Claude & AgentOS</em></p>
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

            // Allow Enter key to send message
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

    # Add custom endpoints to the AgentOS app
    @app.get("/finance/quick-analysis")
    async def quick_analysis(symbol: str = "AAPL"):
        """Quick financial analysis for a symbol"""
        try:
            # Generate cache key
            cache_manager = get_cache_manager()
            cache_key = None
            if cache_manager:
                cache_key = cache_key_for("quick_analysis", symbol=symbol)
                cached_result = cache_manager.get(cache_key)
                if cached_result:
                    return cached_result

            # Run the agent
            prompt = f"Provide a quick financial analysis and current market sentiment for {symbol}. Include key metrics, recent price movement, and analyst sentiment."
            response = finance_agent.run(prompt)

            result = {
                "symbol": symbol,
                "analysis": str(response.content),
                "timestamp": safe_timestamp(response.created_at),
                "model_used": response.model if hasattr(response, "model") else "Unknown",
                "agent": finance_agent.name,
            }

            # Cache the result
            if cache_manager and cache_key:
                ttl_value = CACHE_CONFIGS["quick_analysis"]["ttl"]
                cache_manager.set(cache_key, result, ttl_value if isinstance(ttl_value, int) else 1800)

            return result
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    @app.get("/finance/market-overview")
    async def market_overview():
        """Get comprehensive market overview with AI reasoning and analysis"""
        try:
            # Generate cache key
            cache_manager = get_cache_manager()
            cache_key = None
            if cache_manager:
                cache_key = cache_key_for("market_overview")
                cached_result = cache_manager.get(cache_key)
                if cached_result:
                    return cached_result

            from datetime import datetime

            # Let the agent use its tools to get market data and analyze
            prompt = "Provide comprehensive market overview with current data and sector performance analysis. And give me a brief analysis of which high volume trending stock values to watch in the market."

            # Agent will call get_market_overview() and get_sector_performance() tools as needed
            response = finance_agent.run(prompt)

            result = {
                "analysis": str(response.content),
                "timestamp": datetime.now().isoformat(),
                "model_used": response.model if hasattr(response, "model") else "Unknown",
                "agent": finance_agent.name,
            }

            # Cache the result
            if cache_manager and cache_key:
                ttl_value = CACHE_CONFIGS["market_overview"]["ttl"]
                cache_manager.set(cache_key, result, ttl_value if isinstance(ttl_value, int) else 1800)

            return result
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

    # Return both agentos and app to ensure routes are preserved
    return agentos, app


def main(config_file: str = None):
    """Main function to run the lightweight AgentOS"""
    print("🏦 Starting Finance News AgentOS Lite...")

    # Validate configuration first
    print("🔧 Validating configuration...")
    if not validate_agentos_config(config_file):
        print("❌ Configuration validation failed. Please check your config and API keys.")
        return

    # Create AgentOS with configuration - returns both agentos and app with custom routes
    agentos, app = create_finance_agentos_lite(config_file)

    # Print startup information
    print("\n" + "=" * 60)
    print("🏦 Finance News AgentOS Lite Ready!")
    print("=" * 60)
    print("🌐 Web Interface: http://localhost:8080")
    print("📖 API Docs: http://localhost:8080/docs")
    print("🔍 Quick Analysis: http://localhost:8080/finance/quick-analysis?symbol=AAPL")
    print("📊 Market Overview: http://localhost:8080/finance/market-overview")
    print("=" * 60)

    # Check database configuration
    db_file = os.getenv("SQLITE_DB_FILE", "finance_agent.db")
    print(f"💾 Database: SQLite ({db_file})")
    print("💡 Lightweight deployment - no Docker or PostgreSQL required!")

    # Check API keys
    api_keys = []
    if os.getenv("ANTHROPIC_API_KEY"):
        api_keys.append("Claude")
    if os.getenv("OPENAI_API_KEY"):
        api_keys.append("OpenAI")
    if os.getenv("TAVILY_API_KEY"):
        api_keys.append("Tavily")

    print(f"🔑 Available AI models: {', '.join(api_keys) if api_keys else 'Claude (default)'}")

    print("\n🚀 Starting server on http://localhost:8080")

    # Load server configuration
    try:
        config = load_agentos_config(config_file)
        host = config.server.host
        port = config.server.port
        reload = config.server.reload
        log_level = config.server.log_level
    except:
        host = "0.0.0.0"
        port = 8080
        reload = False
        log_level = "info"

    # Run the server
    import uvicorn

    uvicorn.run(app, host=host, port=port, reload=reload, log_level=log_level)


if __name__ == "__main__":
    main()
