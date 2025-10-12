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
from model_selector import AgentBuilder  # noqa: E402
from report_utils import save_agent_response_to_md  # noqa: E402
import requests  # noqa: E402
import yfinance as yf  # noqa: E402

# Load environment variables
load_dotenv()


class AdvancedFinanceTools(Toolkit):
    """Enhanced financial toolkit with market data, analysis, and news capabilities"""

    def __init__(self):
        super().__init__()

    def get_market_overview(self) -> str:
        """
        Get comprehensive market overview including major indices and sectors

        Returns:
            Formatted market overview with key indices and metrics
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

            result = f"## Market Overview - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            for name, symbol in indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="2d")

                    if not hist.empty:
                        current_price = hist["Close"].iloc[-1]
                        prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else current_price
                        change = current_price - prev_close
                        change_pct = (change / prev_close) * 100 if prev_close != 0 else 0

                        # Color indicators based on movement
                        if change >= 0:
                            direction = "📈"
                            color = "🟢"
                        else:
                            direction = "📉"
                            color = "🔴"

                        result += f"### {name} ({symbol})\n"
                        result += f"{color} {direction} **${current_price:.2f}** "
                        result += f"({change:+.2f}, {change_pct:+.2f}%)\n\n"
                    else:
                        return f"Error: No data available for {name} ({symbol}). Please try again later."

                except Exception as e:
                    return f"Error fetching data for {name} ({symbol}): {e!s}. Please try again later."

            return result

        except Exception as e:
            return f"Error fetching market overview: {e!s}"

    def get_stock_analysis(self, symbol: str) -> str:
        """
        Get detailed stock analysis including fundamentals and recent performance

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            Comprehensive stock analysis
        """
        try:
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info
            hist = ticker.history(period="1mo")

            if hist.empty:
                return f"No data available for symbol: {symbol}"

            # Basic info
            result = f"## Stock Analysis: {info.get('longName', symbol)} ({symbol.upper()})\n\n"

            # Current price and change
            current_price = hist["Close"].iloc[-1]
            prev_close = info.get("previousClose", current_price)
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close != 0 else 0

            direction = "📈" if change >= 0 else "📉"
            result += "### Current Price\n"
            result += (
                f"{direction} **${current_price:.2f}** ({change:+.2f}, {change_pct:+.2f}%)\n\n"
            )

            # Key metrics
            result += "### Key Metrics\n"
            result += (
                f"- **Market Cap**: ${info.get('marketCap', 'N/A'):,}\n"
                if info.get("marketCap")
                else ""
            )
            result += (
                f"- **P/E Ratio**: {info.get('trailingPE', 'N/A')}\n"
                if info.get("trailingPE")
                else ""
            )
            result += (
                f"- **52 Week High**: ${info.get('fiftyTwoWeekHigh', 'N/A')}\n"
                if info.get("fiftyTwoWeekHigh")
                else ""
            )
            result += (
                f"- **52 Week Low**: ${info.get('fiftyTwoWeekLow', 'N/A')}\n"
                if info.get("fiftyTwoWeekLow")
                else ""
            )
            result += f"- **Volume**: {info.get('volume', 'N/A'):,}\n" if info.get("volume") else ""
            result += (
                f"- **Dividend Yield**: {info.get('dividendYield', 'N/A'):.2%}\n"
                if info.get("dividendYield")
                else ""
            )

            # Analyst recommendations
            if info.get("recommendationKey"):
                result += f"- **Analyst Rating**: {info.get('recommendationKey', 'N/A').title()}\n"

            # Business summary
            if info.get("longBusinessSummary"):
                summary = (
                    info["longBusinessSummary"][:300] + "..."
                    if len(info["longBusinessSummary"]) > 300
                    else info["longBusinessSummary"]
                )
                result += f"\n### Business Overview\n{summary}\n"

            # Performance over different periods
            periods = {"1d": "1 day", "5d": "5 days", "1mo": "1 month", "3mo": "3 months"}
            result += "\n### Performance\n"

            for period, name in periods.items():
                try:
                    period_hist = ticker.history(period=period)
                    if not period_hist.empty and len(period_hist) > 1:
                        period_change = (
                            period_hist["Close"].iloc[-1] / period_hist["Close"].iloc[0] - 1
                        ) * 100
                        result += f"- **{name}**: {period_change:+.2f}%\n"
                except Exception as e:
                    return f"Error fetching {name} performance for {symbol}: {e!s}. Please try again later."

            return result

        except Exception as e:
            return f"Error analyzing stock {symbol}: {e!s}"

    def get_crypto_overview(self) -> str:
        """
        Get cryptocurrency market overview using public APIs

        Returns:
            Formatted crypto market overview
        """
        try:
            # Using CoinGecko API (free, no API key required)
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": "10",
                "page": "1",
                "sparkline": "False",
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            result = (
                f"## Cryptocurrency Overview - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
            result += "### Top 10 Cryptocurrencies by Market Cap\n\n"

            for i, coin in enumerate(data, 1):
                name = coin["name"]
                symbol = coin["symbol"].upper()
                price = coin["current_price"]
                change_24h = coin["price_change_percentage_24h"] or 0
                market_cap = coin["market_cap"]

                direction = "📈" if change_24h >= 0 else "📉"
                result += f"**{i}. {name} ({symbol})**\n"
                result += f"{direction} ${price:,.4f} ({change_24h:+.2f}%)\n"
                result += f"Market Cap: ${market_cap:,.0f}\n\n"

            return result

        except Exception as e:
            return f"Error fetching crypto data: {e!s}"

    def get_economic_calendar(self) -> str:
        """
        Get upcoming economic events and indicators

        Returns:
            Economic calendar information
        """
        try:
            # This is a simplified version - in production you'd use a proper economic calendar API
            result = f"## Economic Calendar - Week of {datetime.now().strftime('%Y-%m-%d')}\n\n"
            result += "### Key Economic Events This Week\n\n"
            result += "⚠️ **Note**: For real-time economic calendar data, please check:\n"
            result += "- [Economic Calendar - Investing.com](https://www.investing.com/economic-calendar/)\n"
            result += "- [Fed Economic Data (FRED)](https://fred.stlouisfed.org/)\n"
            result += "- [Yahoo Finance Economic Calendar](https://finance.yahoo.com/calendar/economic)\n\n"

            # Add some common recurring events
            result += "### Common Weekly/Monthly Events to Watch:\n"
            result += "- **Employment Reports**: First Friday of each month\n"
            result += "- **CPI/Inflation Data**: Mid-month\n"
            result += "- **Fed Meetings**: 8 times per year\n"
            result += "- **GDP Reports**: Quarterly\n"
            result += "- **Weekly Jobless Claims**: Every Thursday\n\n"

            return result

        except Exception as e:
            return f"Error fetching economic calendar: {e!s}"

    def search_financial_news(self, query: str, symbol: str | None = None) -> str:
        """
        Search for specific financial news

        Args:
            query: News search query
            symbol: Optional stock symbol to include in search

        Returns:
            Search query for financial news
        """
        if symbol:
            return f"{query} {symbol} stock market financial news"
        return f"{query} stock market financial news economy"

    def get_sector_performance(self) -> str:
        """
        Get sector performance overview using sector ETFs

        Returns:
            Sector performance analysis
        """
        try:
            # Major sector ETFs
            sectors = {
                "Technology": "XLK",
                "Healthcare": "XLV",
                "Financials": "XLF",
                "Energy": "XLE",
                "Consumer Discretionary": "XLY",
                "Industrials": "XLI",
                "Consumer Staples": "XLP",
                "Materials": "XLB",
                "Real Estate": "XLRE",
                "Utilities": "XLU",
                "Communications": "XLC",
            }

            result = f"## Sector Performance - {datetime.now().strftime('%Y-%m-%d')}\n\n"

            sector_data = []

            for sector, etf in sectors.items():
                try:
                    ticker = yf.Ticker(etf)
                    hist = ticker.history(period="5d")

                    if not hist.empty and len(hist) > 1:
                        current_price = hist["Close"].iloc[-1]
                        prev_price = hist["Close"].iloc[0]
                        change_pct = (current_price / prev_price - 1) * 100

                        sector_data.append((sector, etf, change_pct))
                    else:
                        return f"Error: Insufficient data for {sector} sector ({etf}). Please try again later."

                except Exception as e:
                    return f"Error fetching {sector} sector performance ({etf}): {e!s}. Please try again later."

            # Sort by performance
            sector_data.sort(key=lambda x: x[2], reverse=True)

            result += "### 5-Day Sector Performance (Best to Worst)\n\n"
            for sector, etf, change in sector_data:
                direction = "📈" if change >= 0 else "📉"
                result += f"{direction} **{sector}** ({etf}): {change:+.2f}%\n"

            return result

        except Exception as e:
            return f"Error fetching sector performance: {e!s}"


def create_finance_news_agent(model_choice="claude", interactive=False):
    """
    Create a specialized finance news agent with comprehensive market coverage

    Args:
        model_choice: AI model to use ("claude", "openai", "gemini") or "interactive" for selection
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
    6. **Economic Calendar**: Key economic events and indicators
    7. **Sector Analysis**: Performance across different market sectors

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
    7. **FORMAT**: ALWAYS respond in proper markdown format with headers (#, ##, ###), bullet points (-), and **bold** text for emphasis

    **For stock analysis:**
    - Include company fundamentals (P/E, market cap, dividend yield)
    - Recent earnings and analyst recommendations
    - Technical indicators and chart patterns
    - News catalysts affecting the stock
    - Sector and peer comparisons

    **For market overview:**
    - Major indices performance (S&P 500, Dow, NASDAQ)
    - Sector rotation and leadership
    - VIX and market sentiment indicators
    - Economic events driving markets

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
    print("📅 Economic Calendar - Upcoming economic events and indicators")
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
