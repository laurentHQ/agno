# Multi-Source News Agent

A comprehensive news aggregation system built with the Agno framework that integrates multiple news sources and search engines to provide balanced, real-time news coverage.

## 🌟 Features

### Core Capabilities
- **Multi-Source Integration**: Combines 12+ different news sources and tools
- **Smart Fallbacks**: Works with free tools, enhanced with premium APIs
- **Specialized Agents**: Dedicated agents for tech, finance, and general news
- **Interactive Mode**: Real-time querying with streaming responses
- **Source Attribution**: Cites sources and provides links when available

### Integrated Tools

#### 🆓 Free Tools (No API Key Required)
- **HackerNews**: Tech/startup news and community discussions
- **DuckDuckGo**: Privacy-focused search with news results
- **Newspaper**: Article extraction and summarization from URLs
- **ArXiv**: Academic research papers and scientific developments
- **YFinance**: Financial market data and news

#### 🔑 Premium Tools (API Key Required)
- **Reddit**: Community discussions and trending topics
- **Tavily**: AI-enhanced search and analysis
- **Google Search**: Comprehensive search results
- **Brave Search**: Privacy-focused search engine
- **Crawl4AI**: Advanced web scraping capabilities
- **Firecrawl**: Enterprise web scraping and content extraction

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp config/.env.example .env

# Edit .env with your API keys
nano .env
```

**Minimum Required:**
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 2. Install Dependencies

```bash
# Install basic requirements
pip install agno python-dotenv

# Install all optional dependencies for full functionality
pip install -r requirements-news.txt

# For GitHub trending functionality
pip install -r requirements-github.txt
```

### 3. Run the Agent

```bash
# Navigate to the news example directory
cd example/news

# Easy launcher (recommended)
python launcher.py

# Or run components directly:
# General news agents
python examples/run_news_demo.py
python examples/simple_example.py

# GitHub trending agents
python agents/github_trending_agent.py
python utils/github_trending_reporter.py

# Finance and market analysis
python agents/finance_news_agent.py

# Combined tech news hub
python agents/tech_news_hub.py
```

## 📋 Usage Examples

### Basic Usage
```python
from multisource_news_agent import create_basic_news_agent

# Create agent with free tools only
agent = create_basic_news_agent()

# Get news
response = agent.run("What are today's top tech stories?")
print(response.content)
```

### Enhanced Multi-Source Agent
```python
from multisource_news_agent import create_enhanced_news_agent

# Create agent with all available tools
agent = create_enhanced_news_agent()

# Comprehensive news analysis
response = agent.run("Give me a balanced summary of today's major news from multiple sources")
print(response.content)
```

### Specialized Agents
```python
from multisource_news_agent import create_specialized_agents

agents = create_specialized_agents()

# Tech-focused news
tech_news = agents["tech"].run("What are the latest AI breakthroughs?")

# Financial news
market_news = agents["finance"].run("What's happening in the markets today?")
```

### Finance News Agent
```python
from finance_news_agent import create_finance_news_agent

# Create specialized finance agent (default: Claude)
finance_agent = create_finance_news_agent()

# Or specify a different model
finance_agent_openai = create_finance_news_agent(model_choice="openai")
finance_agent_gemini = create_finance_news_agent(model_choice="gemini")

# Get market overview
market_overview = finance_agent.run("What's the current market overview?")

# Analyze specific stocks
stock_analysis = finance_agent.run("Analyze AAPL stock with recent news")

# Cryptocurrency markets
crypto_news = finance_agent.run("Show me cryptocurrency market trends")

# Sector analysis
sector_performance = finance_agent.run("What are the best performing sectors today?")
```

#### Model Selection
The finance agent supports multiple AI models:
- **Claude (Anthropic)** - Default, most stable
- **GPT-4 (OpenAI)** - Alternative, requires OPENAI_API_KEY
- **Gemini (Google)** - Alternative, requires GOOGLE_API_KEY

Interactive mode will prompt you to choose your preferred model.

## 🔧 Configuration

### Environment Variables

Create a `.env` file with your API keys:

```bash
# Required
ANTHROPIC_API_KEY=your_key_here

# Optional (enables additional features)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
TAVILY_API_KEY=your_tavily_key
GOOGLE_API_KEY=your_google_key
BRAVE_API_KEY=your_brave_key
FIRECRAWL_API_KEY=your_firecrawl_key

# GitHub Integration (optional)
GITHUB_TOKEN=your_github_token  # For higher rate limits
```

### API Key Setup Instructions

#### Reddit API
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Create a new app (script type)
3. Note the client ID and secret

#### Tavily API
1. Sign up at [Tavily](https://tavily.com)
2. Get your API key from the dashboard

#### Google Search API
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable Custom Search API
3. Create credentials and a Custom Search Engine

#### Brave Search API
1. Sign up at [Brave Search API](https://api.search.brave.com)
2. Get your API key

## 🎯 Agent Types

### 1. Basic News Agent
- **Tools**: HackerNews, DuckDuckGo, Newspaper
- **Use Case**: Essential news coverage without API dependencies
- **Best For**: Quick setup, reliable basic functionality

### 2. Enhanced News Agent
- **Tools**: All available tools based on API keys
- **Use Case**: Comprehensive multi-source news aggregation
- **Best For**: Professional news monitoring, research

### 3. Specialized Agents
- **Tech Agent**: HackerNews, ArXiv, Reddit tech communities
- **Finance Agent**: YFinance, financial news sources
- **Use Case**: Domain-specific news monitoring

## 📊 Tool Comparison

| Tool | Type | API Required | Strengths | Use Cases |
|------|------|-------------|-----------|-----------|
| HackerNews | Tech News | No | Tech community, startup news | Developer news, trending tech |
| DuckDuckGo | Search | No | Privacy, no limits | General search, backup |
| Reddit | Social | Yes | Community discussions | Sentiment, trending topics |
| Tavily | AI Search | Yes | AI-enhanced analysis | Deep insights, analysis |
| Google | Search | Yes | Comprehensive results | Professional research |
| Newspaper | Scraping | No | Article extraction | Content analysis |
| ArXiv | Academic | No | Research papers | Scientific developments |
| YFinance | Financial | No | Market data | Financial news, stocks |

## 🔍 Query Examples

### General News
```python
"What are today's major news stories?"
"Give me a summary of breaking news"
"What's trending globally right now?"
```

### Tech News
```python
"What are the latest AI developments?"
"Show me trending startup news"
"What's happening in the tech industry?"
```

### Financial News
```python
"What are the major market movements today?"
"Give me cryptocurrency news updates"
"What stocks are trending?"
"Analyze AAPL stock with recent news"
"Show me sector performance and rotation"
"What's the current market overview?"
"Find news about Federal Reserve policy"
"How are tech stocks performing this week?"
"Get analysis on SPY and QQQ trends"
"What are the top cryptocurrencies today?"
```

### GitHub Trending
```python
"What are the trending repositories today?"
"Show me trending Python repositories this week"
"Find trending AI repositories with news coverage"
"What's popular in the JavaScript ecosystem?"
```

### Research & Analysis
```python
"Find recent research papers on machine learning"
"What's the community saying about [topic] on Reddit?"
"Analyze the sentiment around [company/technology]"
```

## 🛠️ Customization

### Adding New Tools
```python
from agno.tools.your_custom_tool import YourCustomTool

# Add to agent creation
tools.append(YourCustomTool())
```

### Custom Instructions
```python
agent = Agent(
    model=Claude(id="claude-sonnet-4-5"),
    tools=tools,
    instructions="""
    Your custom instructions here...
    Focus on specific topics, formats, or analysis styles.
    """,
    markdown=True,
)
```

### Filtering and Focus
```python
# Create domain-specific agents
crypto_agent = Agent(
    tools=[DuckDuckGoTools(), YFinanceTools()],
    instructions="Focus only on cryptocurrency and blockchain news"
)
```

## 🚨 Troubleshooting

### Common Issues

**"ANTHROPIC_API_KEY not set"**
- Ensure your `.env` file contains the API key
- Check the file is in the correct directory

**"Tool not available"**
- Install missing dependencies: `pip install -r requirements-news.txt`
- Check if API keys are properly set

**Rate Limiting**
- Use free tools (HackerNews, DuckDuckGo) as primary sources
- Implement delays between requests for premium APIs

### Performance Tips

1. **Start with basic agent** for testing
2. **Add API keys gradually** to test each integration
3. **Use specialized agents** for focused queries
4. **Cache results** for repeated queries

## 📈 Performance Expectations

- **Basic Agent**: ~3-5 seconds per query
- **Enhanced Agent**: ~10-15 seconds per comprehensive query
- **Specialized Agents**: ~5-8 seconds per focused query

Response times depend on:
- Number of active tools
- API response times
- Query complexity
- Network conditions

## 🤝 Contributing

1. Fork the repository
2. Add new tools in the Agno framework style
3. Update configuration and documentation
4. Test with both free and premium tools
5. Submit pull request

## 📄 License

This project uses the Agno framework. See the main repository for license details.

## 🆘 Support

- **Agno Documentation**: [docs.agno.com](https://docs.agno.com)
- **Community**: [community.agno.com](https://community.agno.com)
- **Discord**: [Agno Discord](https://discord.gg/4MtYHHrgA8)

---

Built with ❤️ using the [Agno Framework](https://agno.com)