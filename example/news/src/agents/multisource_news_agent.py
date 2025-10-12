from datetime import datetime
import os

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.arxiv import ArxivTools
from agno.tools.bravesearch import BraveSearchTools
from agno.tools.crawl4ai import Crawl4aiTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.newspaper import NewspaperTools
from agno.tools.reddit import RedditTools
from agno.tools.tavily import TavilyTools
from agno.tools.yfinance import YFinanceTools
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required API key
if not os.getenv("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY is not set")


def create_basic_news_agent():
    """Create a basic news agent with core tools that don't require API keys"""
    current_date = datetime.now().strftime("%B %d, %Y")
    current_year = datetime.now().year

    return Agent(
        model=Claude(id="claude-sonnet-4-5"),
        tools=[
            HackerNewsTools(),
            DuckDuckGoTools(enable_news=True, enable_search=True),
            NewspaperTools(),
        ],
        instructions=f"""
        You are a focused news aggregator using reliable sources.

        **IMPORTANT CONTEXT:**
        - Today's date: {current_date}
        - Current year: {current_year}
        - When searching for "latest" or "recent" news, focus on {current_year} content
        - Use current date context in your searches and responses

        When asked about news:
        1. Check HackerNews for tech/startup news and discussions
        2. Use DuckDuckGo for general news search (no API key required)
        3. Use Newspaper tools to extract and summarize articles from URLs

        Provide concise, factual summaries with sources cited.
        """,
        markdown=True,
    )


def create_enhanced_news_agent():
    """Create an enhanced news agent with additional tools (requires API keys)"""
    tools = [
        HackerNewsTools(),
        DuckDuckGoTools(enable_news=True, enable_search=True),
        NewspaperTools(),
        ArxivTools(),  # Academic research
        YFinanceTools(),  # Financial news
    ]

    # Add tools that require API keys if available
    if os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET"):
        tools.append(RedditTools())

    if os.getenv("TAVILY_API_KEY"):
        tools.append(TavilyTools())

    if os.getenv("GOOGLE_API_KEY"):
        tools.append(GoogleSearchTools())

    if os.getenv("BRAVE_API_KEY"):
        tools.append(BraveSearchTools())

    # Add web scraping tools
    try:
        tools.append(Crawl4aiTools())
    except:
        print("Crawl4AI not available")

    try:
        tools.append(FirecrawlTools())
    except:
        print("Firecrawl not available")

    current_date = datetime.now().strftime("%B %d, %Y")
    current_year = datetime.now().year

    return Agent(
        model=Claude(id="claude-sonnet-4-5"),
        tools=tools,
        instructions=f"""
        You are a comprehensive multi-source news aggregator.

        **IMPORTANT CONTEXT:**
        - Today's date: {current_date}
        - Current year: {current_year}
        - When searching for "latest", "recent", or "today's" news, focus on {current_year} content
        - Use current date context in all your searches and responses
        - Avoid referencing outdated years (like 2024) when looking for current news

        When asked about news:

        **Tech/Startup News:**
        - Check HackerNews for trending tech stories and community discussions
        - Use ArXiv for latest research papers and academic developments

        **General News:**
        - Use DuckDuckGo for broad news search (reliable, no API limits)
        - Use Google Search if available for comprehensive results
        - Use Brave Search for privacy-focused search results
        - Use Tavily for AI-enhanced news analysis and insights

        **Social & Community:**
        - Check Reddit for community discussions and trending topics
        - Focus on relevant subreddits like r/technology, r/worldnews, r/science

        **Financial News:**
        - Use YFinance for market news, stock updates, and financial trends

        **Content Analysis:**
        - Use Newspaper tools to extract and summarize articles from URLs
        - Use Crawl4AI and Firecrawl for advanced web scraping when needed

        **Response Guidelines:**
        1. Provide balanced summaries from multiple sources
        2. Cite sources and include links when possible
        3. Organize information by category (Tech, Finance, General, etc.)
        4. Highlight trending topics and breaking news
        5. Include community sentiment from Reddit when relevant
        6. Cross-reference information across sources for accuracy
        7. Always use {current_year} as the current year context
        """,
        markdown=True,
    )


def create_specialized_agents():
    """Create specialized agents for different news categories"""
    current_date = datetime.now().strftime("%B %d, %Y")
    current_year = datetime.now().year

    # Tech News Agent
    tech_agent = Agent(
        model=Claude(id="claude-sonnet-4-5"),
        tools=[
            HackerNewsTools(),
            ArxivTools(),
            DuckDuckGoTools(enable_news=True),
            RedditTools() if os.getenv("REDDIT_CLIENT_ID") else None,
        ],
        instructions=f"""
        You are a specialized tech news agent.

        **CURRENT CONTEXT:**
        - Today's date: {current_date}
        - Current year: {current_year}
        - Focus on {current_year} developments and news

        Focus on:
        - Startup news and funding announcements
        - Technology breakthroughs and research
        - Developer community discussions
        - AI/ML developments
        - Open source projects and releases
        """,
        markdown=True,
    )

    # Financial News Agent
    finance_agent = Agent(
        model=Claude(id="claude-sonnet-4-5"),
        tools=[
            YFinanceTools(),
            DuckDuckGoTools(enable_news=True),
            NewspaperTools(),
        ],
        instructions=f"""
        You are a financial news specialist.

        **CURRENT CONTEXT:**
        - Today's date: {current_date}
        - Current year: {current_year}
        - Focus on {current_year} market data and financial news

        Focus on:
        - Market movements and trends
        - Economic indicators
        - Corporate earnings and announcements
        - Cryptocurrency developments
        - Investment opportunities and risks
        """,
        markdown=True,
    )

    return {"tech": tech_agent, "finance": finance_agent}


if __name__ == "__main__":
    print("🔧 Creating Multi-Source News Agents...")

    # Check available tools
    available_tools = []
    if os.getenv("REDDIT_CLIENT_ID"):
        available_tools.append("Reddit")
    if os.getenv("TAVILY_API_KEY"):
        available_tools.append("Tavily")
    if os.getenv("GOOGLE_API_KEY"):
        available_tools.append("Google Search")
    if os.getenv("BRAVE_API_KEY"):
        available_tools.append("Brave Search")

    print(
        f"📡 Available API-based tools: {', '.join(available_tools) if available_tools else 'None (using free tools only)'}"
    )

    # Create the enhanced news agent
    news_agent = create_enhanced_news_agent()

    print("\n🚀 Multi-Source News Agent Ready!")
    print("=" * 50)

    # Example queries
    example_queries = [
        "What are the top tech news stories today?",
        "Give me a summary of recent AI developments",
        "What's happening in the cryptocurrency market?",
        "Find trending discussions on Reddit about technology",
        "Summarize the latest startup funding news",
    ]

    print("💡 Example queries:")
    for i, query in enumerate(example_queries, 1):
        print(f"   {i}. {query}")

    print("\n" + "=" * 50)

    # Interactive mode
    while True:
        try:
            user_query = input("\n📰 Enter your news query (or 'quit' to exit): ").strip()

            if user_query.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break

            if not user_query:
                continue

            print(f"\n🔍 Searching for: {user_query}")
            print("-" * 50)

            response = news_agent.run(user_query)
            print(response.content)

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
