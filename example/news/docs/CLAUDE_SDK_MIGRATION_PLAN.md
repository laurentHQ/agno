# Claude Agent SDK Migration Plan
## Migrating News Agents from agno Framework to Claude Agent SDK

### Executive Summary

This plan outlines the migration of the current agno-based news agent system to Claude Agent SDK, evaluating feature parity, benefits, and implementation strategy.

## 📊 Feature Comparison Matrix

| Feature Category | Current agno Implementation | Claude Agent SDK | Migration Status | Notes |
|------------------|----------------------------|------------------|------------------|-------|
| **Core Agent Architecture** |
| Agent Classes | `Agent` with model/tools/instructions | `ClaudeSDKClient` with tools/hooks | ✅ **Full Parity** | Similar declarative approach |
| Model Selection | Multi-model support (Claude/OpenAI/Gemini) | Claude-only | ⚠️ **Limited** | Lose multi-model capability |
| Tool Integration | `Toolkit` classes with decorators | In-process MCP servers | ✅ **Enhanced** | Better performance, simpler deployment |
| Session Management | Basic session handling | Advanced session management | ✅ **Improved** | Built-in session persistence |
| **Tools & Integrations** |
| Web Search | DuckDuckGo, Tavily, Brave | WebSearch, WebFetch built-in | ✅ **Equivalent** | Built-in tools + MCP extensions |
| File Operations | Limited file handling | Read/Write/Grep/Glob built-in | ✅ **Enhanced** | More comprehensive file operations |
| Code Execution | Via tools | Bash built-in | ✅ **Enhanced** | Direct code execution support |
| HackerNews API | `HackerNewsTools` | Custom MCP tool needed | 🔄 **Migration Required** | Need to rebuild as MCP tool |
| YFinance API | `YFinanceTools` | Custom MCP tool needed | 🔄 **Migration Required** | Need to rebuild as MCP tool |
| Reddit API | `RedditTools` | Custom MCP tool needed | 🔄 **Migration Required** | Need to rebuild as MCP tool |
| **Streaming & Performance** |
| Async Streaming | `stream=True` | AsyncIterator built-in | ✅ **Enhanced** | Better async handling |
| Performance | Good | Optimized for Claude | ✅ **Improved** | In-process tools, no IPC overhead |
| Context Management | Manual | Automatic compaction | ✅ **Enhanced** | Built-in context optimization |
| **Development Experience** |
| Report Generation | Custom `report_utils.py` | Built-in file operations | ✅ **Simplified** | Less custom code needed |
| Error Handling | Manual try/catch | Built-in error handling | ✅ **Enhanced** | Production-ready error management |
| Testing & Debugging | Custom test scripts | Built-in monitoring | ✅ **Enhanced** | Better observability |
| **Advanced Features** |
| Multi-Agent Teams | agno Teams | Subagents | ✅ **Similar** | Different API, same capability |
| Memory/Knowledge | Built-in memory | Session-based context | ✅ **Different Approach** | Context vs persistent memory |
| Human-in-Loop | Manual implementation | Hooks system | ✅ **Enhanced** | Built-in human interaction points |
| Permissions/Security | Basic | Fine-grained control | ✅ **Enhanced** | Production security features |
| **Deployment** |
| Runtime | AgentOS FastAPI app | Single Python process | 🔄 **Different** | Simpler but lose web UI |
| Cloud Integration | Full cloud deployment | Local/cloud flexible | ✅ **Flexible** | Multiple deployment options |
| Monitoring | Built-in UI | SDK-based monitoring | 🔄 **Different** | Need custom monitoring solution |

## 🎯 Migration Strategy

### Phase 1: Foundation Setup (Week 1-2)
**Objective**: Establish Claude Agent SDK environment and migrate core utilities

#### 1.1 Environment Setup
```bash
# Install Claude Agent SDK
pip install claude-agent-sdk

# Set up authentication
export ANTHROPIC_API_KEY="your_claude_api_key"
```

#### 1.2 Core Utility Migration
- **Target**: `utils/report_utils.py` → Claude SDK file operations
- **Target**: Basic agent creation patterns
- **Target**: Configuration management

### Phase 2: Tool Migration (Week 3-4)
**Objective**: Rebuild existing tools as MCP servers

#### 2.1 High-Priority Tools
1. **HackerNews MCP Tool**
   ```python
   # New structure
   from claude_agent_sdk import ClaudeSDKClient
   from claude_agent_sdk.tools import Tool

   class HackerNewsTool(Tool):
       def get_trending_posts(self, limit: int = 10) -> str:
           """Get trending HackerNews posts"""
           # Implementation using requests
   ```

2. **Financial Data MCP Tool**
   ```python
   class YFinanceTool(Tool):
       def get_stock_data(self, symbol: str) -> str:
           """Get stock market data"""
           # Implementation using yfinance
   ```

#### 2.2 Enhanced Search Integration
- Leverage built-in WebSearch/WebFetch
- Integrate Tavily as custom MCP tool if needed
- Utilize built-in Grep/Glob for content analysis

### Phase 3: Agent Migration (Week 5-6)
**Objective**: Convert existing agents to Claude Agent SDK

#### 3.1 Finance News Agent
```python
# Before (agno)
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.yfinance import YFinanceTools

agent = Agent(
    model=Claude(id="claude-sonnet-4-5"),
    tools=[YFinanceTools(), DuckDuckGoTools()],
    instructions="Financial analysis agent"
)

# After (Claude Agent SDK)
from claude_agent_sdk import ClaudeSDKClient
from .tools import YFinanceTool, WebSearchTool

client = ClaudeSDKClient()
client.add_tool(YFinanceTool())
client.add_tool(WebSearchTool())

response = await client.query(
    "Analyze AAPL stock performance",
    instructions="You are a financial analysis agent"
)
```

#### 3.2 GitHub Trending Agent
```python
# Claude Agent SDK implementation
from claude_agent_sdk import ClaudeSDKClient
from .tools import GitHubTrendingTool

class GitHubNewsAgent:
    def __init__(self):
        self.client = ClaudeSDKClient()
        self.client.add_tool(GitHubTrendingTool())

    async def analyze_trends(self, language: str = None):
        query = f"Analyze GitHub trending repositories"
        if language:
            query += f" for {language}"

        return await self.client.query(
            query,
            instructions="You are a GitHub trends analyst"
        )
```

### Phase 4: Advanced Features (Week 7-8)
**Objective**: Implement advanced capabilities and optimization

#### 4.1 Multi-Agent Coordination
```python
# Subagents implementation
class NewsAgentOrchestrator:
    def __init__(self):
        self.finance_agent = FinanceNewsAgent()
        self.tech_agent = TechNewsAgent()
        self.github_agent = GitHubNewsAgent()

    async def comprehensive_analysis(self, topic: str):
        # Coordinate multiple agents
        finance_data = await self.finance_agent.analyze(topic)
        tech_news = await self.tech_agent.research(topic)
        github_trends = await self.github_agent.analyze_trends()

        # Synthesize results
        return await self.synthesize_reports([
            finance_data, tech_news, github_trends
        ])
```

#### 4.2 Hooks and Human-in-Loop
```python
class InteractiveNewsAgent(ClaudeSDKClient):
    def __init__(self):
        super().__init__()
        self.add_hook('before_tool_call', self.confirm_tool_use)
        self.add_hook('after_response', self.save_report)

    def confirm_tool_use(self, tool_name: str, args: dict):
        """Ask user before expensive operations"""
        if tool_name in ['web_search', 'financial_data']:
            return input(f"Execute {tool_name} with {args}? (y/n): ") == 'y'
        return True

    def save_report(self, response: str):
        """Auto-save reports"""
        # Save to reports/ directory
```

## 🔄 Migration Architecture

### Current Architecture
```
agno Framework
├── Agent (multi-model)
├── Tools (various APIs)
├── AgentOS Runtime
└── Built-in UI
```

### Target Architecture
```
Claude Agent SDK
├── ClaudeSDKClient (Claude-only)
├── MCP Tools (in-process)
├── Hooks System
└── Custom Monitoring
```

## ⚠️ Key Considerations

### What You Gain
1. **Performance**: In-process MCP tools, no IPC overhead
2. **Simplicity**: Single Python process, less infrastructure
3. **Claude Integration**: Optimized for Claude models
4. **Production Features**: Built-in error handling, permissions
5. **Official Support**: Anthropic-maintained SDK

### What You Lose
1. **Multi-Model Support**: Claude-only (major limitation)
2. **Built-in UI**: No AgentOS web interface
3. **Cloud Runtime**: Need custom deployment solution
4. **Tool Ecosystem**: Must rebuild existing tools as MCP

### Critical Decision Points

#### Should You Migrate?
**Migrate IF:**
- Primary use case is Claude-based agents
- Performance and simplicity are priorities
- Want official Anthropic support
- Comfortable rebuilding tools

**Stay with agno IF:**
- Need multi-model support (Claude/OpenAI/Gemini)
- Rely heavily on AgentOS runtime and UI
- Have extensive existing tool integrations
- Need immediate production deployment

## 📋 Detailed Migration Checklist

### Pre-Migration Assessment
- [ ] Catalog all existing tools and their usage
- [ ] Evaluate multi-model dependency
- [ ] Assess AgentOS runtime requirements
- [ ] Plan for monitoring/observability replacement

### Phase 1: Foundation
- [ ] Install Claude Agent SDK
- [ ] Set up development environment
- [ ] Create basic agent template
- [ ] Migrate report utilities
- [ ] Test basic functionality

### Phase 2: Tool Migration
- [ ] Create HackerNews MCP tool
- [ ] Create YFinance MCP tool
- [ ] Create Reddit MCP tool
- [ ] Test tool integration
- [ ] Performance benchmark

### Phase 3: Agent Migration
- [ ] Convert finance news agent
- [ ] Convert GitHub trending agent
- [ ] Convert tech news hub
- [ ] Convert multisource agent
- [ ] Integration testing

### Phase 4: Advanced Features
- [ ] Implement subagents
- [ ] Add hooks system
- [ ] Create monitoring solution
- [ ] Performance optimization
- [ ] Production deployment

### Validation & Testing
- [ ] Feature parity testing
- [ ] Performance comparison
- [ ] Error handling validation
- [ ] User acceptance testing
- [ ] Documentation update

## 💡 Recommendations

### Hybrid Approach (Recommended)
Consider a **hybrid approach** that leverages both frameworks:

1. **Keep agno for multi-model orchestration**
2. **Use Claude Agent SDK for Claude-specific tasks**
3. **Bridge the two via API calls**

```python
# Hybrid implementation
class HybridNewsAgent:
    def __init__(self):
        # agno for multi-model support
        self.agno_agent = Agent(
            model=GPT4(),  # For tasks requiring OpenAI
            tools=[BasicTools()]
        )

        # Claude SDK for advanced Claude features
        self.claude_client = ClaudeSDKClient()
        self.claude_client.add_tool(AdvancedAnalysisTool())

    async def comprehensive_analysis(self, query: str):
        # Use appropriate agent based on task
        if requires_advanced_reasoning(query):
            return await self.claude_client.query(query)
        else:
            return self.agno_agent.run(query)
```

### Timeline Recommendation
- **Evaluation Phase**: 2 weeks
- **Proof of Concept**: 4 weeks
- **Full Migration**: 8-12 weeks
- **Hybrid Approach**: 6 weeks

## 🎯 Conclusion

The Claude Agent SDK offers significant advantages in performance, simplicity, and Claude integration, but comes with the trade-off of losing multi-model support. A **phased migration or hybrid approach** is recommended to maximize benefits while minimizing risks.

The migration is **technically feasible** with **95% feature parity**, but requires significant effort to rebuild tools and replace AgentOS capabilities. Consider your specific requirements and constraints before proceeding.