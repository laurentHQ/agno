# Agno News Agent Tools

Based on my exploration of the Agno framework, here are various tools you can use to fetch news feeds from different sources, inspired by your `hackernews_agent.py`:

## 1. Web Search Tools for News

### DuckDuckGo (with news search)
```python
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
    model=Claude(id="claude-sonnet-4-5"),
    tools=[DuckDuckGoTools(enable_news=True)],
    markdown=True,
)
agent.print_response("Find latest tech startup news", stream=True)
```

### Google Search
```python
from agno.agent import Agent
from agno.tools.googlesearch import GoogleSearchTools

agent = Agent(
    model=Claude(id="claude-sonnet-4-5"),
    tools=[GoogleSearchTools()],
    markdown=True,
)
agent.print_response("Search for latest AI news", stream=True)
```

### Brave Search
```python
from agno.agent import Agent
from agno.tools.bravesearch import BraveSearchTools

agent = Agent(
    model=Claude(id="claude-sonnet-4-5"),
    tools=[BraveSearchTools()],
    markdown=True,
)
```

### Tavily (AI-powered search)
```python
from agno.agent import Agent
from agno.tools.tavily import TavilyTools

agent = Agent(
    model=Claude(id="claude-sonnet-4-5"),
    tools=[TavilyTools()],
    markdown=True,
)
agent.print_response("Get latest cryptocurrency news", stream=True)
```

## 2. Social Media & Discussion Platforms

### Reddit
```python
from agno.agent import Agent
from agno.tools.reddit import RedditTools

agent = Agent(
    model=Claude(id="claude-sonnet-4-5"),
    tools=[RedditTools()],
    markdown=True,
)
agent.print_response("Get trending posts from r/technology", stream=True)
```

## 3. Web Scraping Tools

### Newspaper (Article extraction)
```python
from agno.agent import Agent
from agno.tools.newspaper import NewspaperTools

agent = Agent(
    model=Claude(id="claude-sonnet-4-5"),
    tools=[NewspaperTools()],
    markdown=True,
)
agent.print_response("Summarize articles from https://techcrunch.com", stream=True)
```

### Crawl4AI
```python
from agno.agent import Agent
from agno.tools.crawl4ai import Crawl4aiTools

agent = Agent(
    model=Claude(id="claude-sonnet-4-5"),
    tools=[Crawl4aiTools()],
    markdown=True,
)
```

### Firecrawl
```python
from agno.agent import Agent
from agno.tools.firecrawl import FirecrawlTools

agent = Agent(
    model=Claude(id="claude-sonnet-4-5"),
    tools=[FirecrawlTools()],
    markdown=True,
)
```

## 4. Academic & Research Sources

### ArXiv
```python
from agno.agent import Agent
from agno.tools.arxiv import ArxivTools

agent = Agent(
    model=Claude(id="claude-sonnet-4-5"),
    tools=[ArxivTools()],
    markdown=True,
)
agent.print_response("Find latest AI research papers", stream=True)
```

## 5. Financial News

### YFinance
```python
from agno.agent import Agent
from agno.tools.yfinance import YFinanceTools

agent = Agent(
    model=Claude(id="claude-sonnet-4-5"),
    tools=[YFinanceTools()],
    markdown=True,
)
agent.print_response("Get latest market news and stock updates", stream=True)
```

## 6. Multi-Source News Agent Example

Here's a comprehensive example combining multiple sources:

```python
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.hackernews import HackerNewsTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reddit import RedditTools
from agno.tools.tavily import TavilyTools

# Multi-source news aggregator agent
news_agent = Agent(
    model=Claude(id="claude-sonnet-4-5"),
    tools=[
        HackerNewsTools(),
        DuckDuckGoTools(enable_news=True),
        RedditTools(),
        TavilyTools(),
    ],
    instructions="""
    You are a comprehensive news aggregator. When asked about news:
    1. Check HackerNews for tech/startup news
    2. Use DuckDuckGo for general news search
    3. Look at relevant Reddit communities
    4. Use Tavily for AI-powered news analysis

    Provide a balanced summary from multiple sources.
    """,
    markdown=True,
)

news_agent.print_response(
    "Give me a comprehensive report on today's major tech news",
    stream=True
)
```

## Required Environment Variables

- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` for Reddit
- `TAVILY_API_KEY` for Tavily
- `GOOGLE_API_KEY` for Google Search
- `BRAVE_API_KEY` for Brave Search

Each tool has different strengths - HackerNews for tech, Reddit for community discussions, Tavily for AI-enhanced search, and DuckDuckGo for general news without API requirements.