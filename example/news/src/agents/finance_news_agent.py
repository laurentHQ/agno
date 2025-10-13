#!/usr/bin/env python3
"""
Finance News Agent
Specialized agent for financial markets, stocks, crypto, and economic news
"""

# Standard library imports
from datetime import datetime
import os
from pathlib import Path
import re
import sys

# Add paths for imports from organized structure - must be before third-party imports
current_dir = Path(__file__).parent
news_root = current_dir.parent
sys.path.insert(0, str(news_root))
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(news_root / "utils"))

# Third-party imports
from agno.tools import Toolkit  # noqa: E402
from agno.tools.duckduckgo import DuckDuckGoTools  # noqa: E402
from agno.tools.hackernews import HackerNewsTools  # noqa: E402
from agno.tools.reddit import RedditTools  # noqa: E402
from agno.tools.tavily import TavilyTools  # noqa: E402
from agno.tools.yfinance import YFinanceTools  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

# Local imports - require path setup above
from market_data_utils import (  # noqa: E402
    get_crypto_overview_report,
    get_index_futures_overview,
    get_market_overview_with_periods,
    get_sector_performance_report,
    get_stock_analysis_report,
)
from model_selector import AgentBuilder  # noqa: E402
from report_utils import save_agent_response_to_md  # noqa: E402

# Load environment variables
load_dotenv()


class AdvancedFinanceTools(Toolkit):
    """Enhanced financial toolkit with market data, analysis, and news capabilities"""

    def __init__(self):
        super().__init__(name="advanced_finance_tools", auto_register=False)

        # Explicitly register toolkit functions so AgentOS exposes them reliably.
        self.register(self.get_market_overview)
        self.register(self.get_stock_analysis)
        self.register(self.get_crypto_overview)
        self.register(self.get_sector_performance)
        self.register(self.get_index_futures_preview)

    def get_market_overview(
        self,
        include_daily: bool = True,
        include_wtd: bool = True,
        include_mtd: bool = True,
        include_ytd: bool = True,
        compact: bool = True,
        include_futures_preview: bool = True,
    ) -> str:
        """
        Get comprehensive market overview including major indices with multiple time periods

        Args:
            include_daily: Include daily changes (default: True)
            include_wtd: Include week-to-date changes (default: True)
            include_mtd: Include month-to-date changes (default: True)
            include_ytd: Include year-to-date changes (default: True)
            compact: Output format - False for JSON (default), True for markdown table
            include_futures_preview: Append index futures table when markets are closed or pre-market

        Returns:
            Market overview in JSON format (compact=False) or markdown table (compact=True)
            - JSON: Structured data with full details for programmatic access
            - Markdown table: Compact visual display with emoji indicators (📈📉)
        """
        try:
            # Major indices to track
            indices = {
                # US Indices
                "S&P 500": "^GSPC",
                "Dow Jones": "^DJI",
                "NASDAQ": "^IXIC",
                "Russell 2000": "^RUT",
                "VIX": "^VIX",
                # Global Indices
                "Hang Seng (HSI)": "^HSI",
                "EURO STOXX 50": "^STOXX50E",
                # Currencies
                "EUR/USD": "EURUSD=X",
                "US Dollar Index": "DX-Y.NYB",
                # Commodities
                "Gold": "GC=F",
                "Crude Oil (WTI)": "CL=F",
            }

            return get_market_overview_with_periods(
                indices=indices,
                include_daily=include_daily,
                include_wtd=include_wtd,
                include_mtd=include_mtd,
                include_ytd=include_ytd,
                compact=compact,
                include_futures_preview=include_futures_preview,
            )

        except Exception as e:
            return f"Error fetching market overview: {e!s}"

    def get_index_futures_preview(
        self,
        include_daily: bool = True,
        include_wtd: bool = False,
        include_mtd: bool = False,
        include_ytd: bool = False,
        compact: bool = True,
    ) -> str:
        """
        Get pre-market index futures snapshot for gauging the pending cash-session open.

        Args:
            include_daily: Include daily percentage change (default: True)
            include_wtd: Include week-to-date change (default: False)
            include_mtd: Include month-to-date change (default: False)
            include_ytd: Include year-to-date change (default: False)
            compact: Output format - False for JSON payload, True for markdown table

        Returns:
            Index futures overview focused on overnight direction
        """
        try:
            return get_index_futures_overview(
                include_daily=include_daily,
                include_wtd=include_wtd,
                include_mtd=include_mtd,
                include_ytd=include_ytd,
                compact=compact,
            )
        except Exception as e:
            return f"Error fetching index futures data: {e!s}"

    def get_stock_analysis(self, symbol: str) -> str:
        """
        Get detailed stock analysis including fundamentals and recent performance

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            Comprehensive stock analysis
        """
        return get_stock_analysis_report(symbol)

    def get_crypto_overview(self) -> str:
        """
        Get cryptocurrency market overview using public APIs

        Returns:
            Formatted crypto market overview
        """
        return get_crypto_overview_report()

    def get_sector_performance(self) -> str:
        """
        Get sector performance overview using sector ETFs

        Returns:
            Sector performance analysis
        """
        return get_sector_performance_report()


def create_finance_news_agent(model_choice="openai", interactive=False):
    """
    Create a specialized finance news agent with comprehensive market coverage

    Args:
        model_choice: AI model to use ("openai", "claude", "gemini") or "interactive" for selection
        interactive: If True, show interactive model selection

    Returns:
        Configured Agno agent for financial news and analysis
    """
    current_date = datetime.now().strftime("%B %d, %Y")
    current_year = datetime.now().year

    # Core financial tools
    tools = [
        AdvancedFinanceTools(),
        YFinanceTools(),
        DuckDuckGoTools(enable_search=True, enable_news=True),
        HackerNewsTools(),
    ]

    # Add Tavily for enhanced financial search if API key available
    if os.getenv("TAVILY_API_KEY"):
        tools.append(
            TavilyTools(
                enable_search=True,
                search_depth="advanced",
                max_tokens=6000,
                include_answer=True,
                format="markdown",
            )
        )

    # Add Reddit if API keys available
    if os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET"):
        tools.append(RedditTools())

    instructions = f"""
    You are a specialized Financial News and Market Analysis Agent.

    **CURRENT CONTEXT:**
    - Today's date: {current_date}
    - Current year: {current_year}
    - Focus on {current_year} market developments and financial news

    **Your Capabilities:**
    1. **Market Analysis**: Real-time stock quotes, market indices, sector performance
    2. **Enhanced Financial Search**: Advanced web search using Tavily for real-time financial news and analysis
    3. **Financial News**: Latest financial news from multiple sources including DuckDuckGo and Tavily
    4. **Stock Research**: Detailed company analysis with fundamentals and technical data
    5. **Cryptocurrency**: Crypto market overview and trending digital assets
    6. **Sector Analysis**: Performance across different market sectors
    7. **Index Futures Preview**: Overnight sentiment for S&P 500, Dow, Nasdaq 100, and Russell 2000 futures

    **When responding to financial queries:**
    1. Always provide current market data when relevant
    2. Include specific numbers, percentages, and price movements
    3. Explain market context and potential implications
    4. Cite recent news that might be affecting prices
    5. Consider both technical and fundamental factors
    6. Mention risk factors and market volatility when appropriate

    **Response Guidelines:**
    1. **Market Data**: Always include current prices, changes, and percentages
    2. **Context**: Explain WHY markets are moving, not just HOW
    3. **Sources**: Reference specific news sources and data providers
    4. **Timeframes**: Specify whether data is real-time, delayed, or historical
    5. **Risk Disclosure**: Include appropriate risk warnings for investment information
    6. **Trends**: Identify and explain current market trends and patterns
    7. **Futures Context**: Mention index futures direction before the open and connect it to likely cash-session moves
    8. **FORMAT**: ALWAYS respond in proper markdown format with headers (#, ##, ###), bullet points (-), and **bold** text for emphasis

    **IMPORTANT: Tool Output Formatting:**
    - The get_market_overview() tool supports TWO OUTPUT FORMATS:

      1. **JSON Format** (compact=False):
         * Structured JSON data with full details
         * Best for programmatic access and data processing
         * Parse the JSON and present key insights to users
         * Example: For quick updates, extract and display just the key changes

      2. **Markdown Table Format** (compact=True, default):
         * Clean, visual table with emoji indicators (📈📉)
         * Best for human-readable reports and summaries
         * Present the table as-is, then add your analysis below
         * Includes market status indicators (🔔 OPEN, 🔕 CLOSED, 🌅 PRE_MARKET, 🌙 AFTER_HOURS)

    - Tool parameters to customize output:
      * include_daily, include_wtd, include_mtd, include_ytd (bool) - control which periods to show
      * compact (bool) - False for JSON, True for markdown table (default)

    - When to use each format:
      * Use compact=True for visual market summaries and reports
      * Use compact=False (JSON) when you need to extract specific data or perform calculations

    - After presenting the tool output, ADD YOUR ANALYSIS:
      * Explain trends and provide context
      * Identify key insights and market drivers
      * Highlight notable movements and patterns

    **For stock analysis:**
    - Include company fundamentals (P/E, market cap, dividend yield)
    - Recent earnings and analyst recommendations
    - Technical indicators and chart patterns
    - News catalysts affecting the stock
    - Sector and peer comparisons

    **For market overview:**
    The get_market_overview() tool provides data on:
    - Market status (OPEN/CLOSED/PRE_MARKET/AFTER_HOURS) with timestamp
    - US indices (S&P 500, Dow Jones, NASDAQ, Russell 2000)
    - Market volatility indicator (VIX)
    - Global indices (Hang Seng, EURO STOXX 50)
    - Currency markets (EUR/USD, US Dollar Index)
    - Commodities (Gold, Crude Oil WTI)
    - Multi-period changes (Daily, WTD, MTD, YTD) with directional indicators
    - Automatic index futures preview (S&P 500, Dow, Nasdaq 100, Russell 2000) when the market is CLOSED or in PRE_MARKET status

    After presenting the tool output, provide analysis on:
    - Market trends and patterns across different periods
    - Sector rotation and leadership
    - Risk sentiment (VIX levels, safe haven flows)
    - Index futures direction and how it may influence the opening session or after-hours price action
    - Economic events and news driving market movements
    - Key support/resistance levels being tested

    **CRITICAL: Always format your responses using proper markdown:**
    - Use # for main headers, ## for sub-headers
    - Use - for bullet points and lists
    - Use **bold** for important numbers and key metrics
    - Use tables when presenting data comparisons
    - Structure your response with clear sections and hierarchy

    **Risk Disclaimer:**
    Always remind users that this is for informational purposes only and not financial advice.
    Past performance does not guarantee future results.
    """

    # Use modular AgentBuilder for model selection
    builder = AgentBuilder(tools=tools, instructions=instructions, markdown=True)

    if interactive or model_choice.lower() == "interactive":
        # Interactive model selection
        return builder.build_with_model_selection(
            title="Choose AI Model for Finance Agent", show_descriptions=True
        )
    # Use specific model choice
    return builder.build_with_model_name(model_choice)


def main():
    """Interactive finance news agent with report saving capabilities"""
    print("💰 Finance News & Market Analysis Agent")
    print("=" * 50)

    # Ensure reports directory exists
    reports_dir = news_root / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Create finance agent with interactive model selection
    print("🔧 Creating specialized finance agent...")
    try:
        agent = create_finance_news_agent(interactive=True)
        print("✅ Finance agent created successfully!")
    except Exception as e:
        print(f"❌ Failed to create finance agent: {e}")
        return

    print("\n💡 Finance Agent Capabilities:")
    print("📊 Market Overview - Get real-time market indices and performance")
    print("📈 Stock Analysis - Detailed company analysis with fundamentals")
    print("🪙 Crypto Markets - Cryptocurrency overview and trends")
    print("🏭 Sector Performance - Industry sector analysis and rotation")
    print("📰 Financial News - Latest market news and analysis")

    print("\n🎯 Example queries:")
    queries = [
        "What's the current market overview?",
        "Analyze AAPL stock with recent news",
        "Show me cryptocurrency market trends",
        "What are the best performing sectors today?",
        "Find news about Federal Reserve policy",
        "How are tech stocks performing this week?",
        "Get analysis on SPY and QQQ trends",
    ]

    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")

    # Interactive mode
    print("\n" + "=" * 50)
    print("💡 Ask about stocks, markets, crypto, economic news, or sector analysis!")
    print("Examples:")
    print("  - 'market overview'")
    print("  - 'analyze TSLA with latest news'")
    print("  - 'crypto market trends'")
    print("  - 'technology sector performance'")
    print("\n💾 Options:")
    print("  - Type 'save' after any query to save the last response to markdown")
    print("  - Or use 'save <filename>' to specify a custom filename")

    last_response = None
    last_query = None

    while True:
        try:
            user_input = input("\n💰 Your financial query (or 'quit' to exit): ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("💰 Happy investing! (This is not financial advice)")
                break

            if not user_input:
                continue

            # Handle save commands
            if user_input.lower().startswith("save"):
                if not last_response or not last_query:
                    print("❌ No previous response to save. Run a query first.")
                    continue

                # Extract filename if provided
                parts = user_input.split(maxsplit=1)
                if len(parts) > 1:
                    filename = parts[1]
                else:
                    # Generate filename from query
                    safe_query = re.sub(r"[^\w\s-]", "", last_query).strip()
                    safe_query = re.sub(r"[-\s]+", "_", safe_query)
                    filename = f"finance_report_{safe_query[:30]}"

                try:
                    filepath = save_agent_response_to_md(
                        agent=agent,
                        query=last_query,
                        filename=filename,
                        title=f"Finance Report: {last_query}",
                        reports_dir=str(reports_dir),
                        response_content=last_response,
                    )
                    print(f"✅ Financial report saved: {filepath}")
                except Exception as e:
                    print(f"❌ Error saving report: {e}")
                continue

            # Process regular queries
            user_query = user_input
            print(f"\n📊 Analyzing: {user_query}")
            print("-" * 40)

            response = agent.run(user_query)
            print(response.content)

            # Store for potential saving
            last_response = response.content
            last_query = user_query

            print("\n💡 Type 'save' to save this financial analysis to reports/")

        except KeyboardInterrupt:
            print("\n💰 Happy investing! (This is not financial advice)")
            break
        except EOFError:
            print("\n💰 Happy investing! (This is not financial advice)")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


if __name__ == "__main__":
    main()
