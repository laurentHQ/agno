# News Agent Project Structure

This document outlines the organized structure of the News Agent project.

## 📁 Directory Structure

```
example/news/
├── 📁 agents/                    # Core agent implementations
│   ├── multisource_news_agent.py    # Multi-source news aggregation
│   ├── github_trending_agent.py     # GitHub trending repositories
│   └── tech_news_hub.py             # Combined tech news + GitHub
│
├── 📁 utils/                     # Utility functions and reporters
│   ├── report_utils.py              # Report generation utilities
│   ├── news_reporter.py             # News report generator
│   └── github_trending_reporter.py  # GitHub trending reports
│
├── 📁 examples/                  # Example scripts and demos
│   ├── run_news_demo.py             # Interactive demo
│   ├── simple_example.py            # Basic usage examples
│   ├── save_reports_example.py      # Report saving examples
│   └── test_github_trending.py      # GitHub functionality tests
│
├── 📁 docs/                     # Documentation
│   ├── news_agents.md               # Tool reference guide
│   └── SAVE_REPORTS_GUIDE.md        # Report generation guide
│
├── 📁 config/                   # Configuration files
│   ├── .env.example                 # Environment template
│   ├── requirements-news.txt        # News agent dependencies
│   └── requirements-github.txt      # GitHub trending dependencies
│
├── 📁 reports/                  # Generated reports (auto-created)
│   └── (generated .md files)
│
├── 📁 __pycache__/              # Python cache (auto-generated)
│
├── README.md                    # Main project documentation
└── PROJECT_STRUCTURE.md         # This file
```

## 🎯 Component Categories

### 🤖 Agents (`agents/`)
Core AI agents that provide news and repository intelligence:

- **`multisource_news_agent.py`**: Primary news aggregation agent
  - Integrates HackerNews, DuckDuckGo, Reddit, Tavily, etc.
  - Supports basic and enhanced configurations
  - Includes specialized agents for tech and finance

- **`github_trending_agent.py`**: GitHub repository specialist
  - Custom GitHubTrendingTools toolkit
  - Repository discovery and analysis
  - Integration with news sources for context

- **`tech_news_hub.py`**: Combined intelligence platform
  - Merges general tech news with GitHub trends
  - Language ecosystem analysis
  - Technology-focused reporting (AI, startups, etc.)

### 🛠️ Utilities (`utils/`)
Support functions for report generation and data processing:

- **`report_utils.py`**: Core report generation utilities
  - `quick_news_report()` - Simple one-liner reports
  - `batch_news_reports()` - Multiple report generation
  - Markdown formatting and file management

- **`news_reporter.py`**: Advanced news reporting system
  - NewsReporter class with multiple report types
  - Daily digest generation
  - Custom formatting and metadata

- **`github_trending_reporter.py`**: GitHub-specific reporting
  - Trending repository reports by language/timeframe
  - Multi-language comparisons
  - Technology trend analysis

### 📚 Examples (`examples/`)
Demonstration scripts and testing utilities:

- **`run_news_demo.py`**: Interactive demo with multiple agent types
- **`simple_example.py`**: Basic usage patterns with user choice
- **`save_reports_example.py`**: Comprehensive report generation examples
- **`test_github_trending.py`**: GitHub functionality validation

### 📖 Documentation (`docs/`)
Comprehensive guides and references:

- **`news_agents.md`**: Tool reference and usage examples
- **`SAVE_REPORTS_GUIDE.md`**: Complete guide to report generation

### ⚙️ Configuration (`config/`)
Setup and dependency management:

- **`.env.example`**: Environment variable template
- **`requirements-news.txt`**: Core news agent dependencies
- **`requirements-github.txt`**: Additional GitHub functionality

## 🚀 Quick Start Paths

### For Basic News Reports:
```bash
cd example/news
python examples/simple_example.py
```

### For GitHub Trending:
```bash
cd example/news
python agents/github_trending_agent.py
```

### For Combined Analysis:
```bash
cd example/news
python agents/tech_news_hub.py
```

### For Custom Reports:
```python
# Import from organized structure
from utils.report_utils import quick_news_report
from agents.multisource_news_agent import create_enhanced_news_agent

# Generate reports
quick_news_report("Your query here")
```

## 🔗 Import Structure

All files are designed to work from the news root directory with proper path management:

```python
# Standard pattern in all files
current_dir = Path(__file__).parent
news_root = current_dir.parent  # For files in subdirectories
sys.path.insert(0, str(news_root))
sys.path.insert(0, str(current_dir))
```

## 📊 Workflow Patterns

### 1. **Research Workflow**
`examples/` → `agents/multisource_news_agent.py` → `reports/`

### 2. **GitHub Analysis Workflow**
`examples/` → `agents/github_trending_agent.py` → `utils/github_trending_reporter.py` → `reports/`

### 3. **Comprehensive Analysis Workflow**
`examples/` → `agents/tech_news_hub.py` → `reports/`

### 4. **Custom Development Workflow**
`utils/report_utils.py` → Custom agent → `reports/`

## 🎨 Theme Organization Benefits

1. **Clear Separation of Concerns**: Agents, utilities, examples, and docs are clearly separated
2. **Scalable Structure**: Easy to add new agents, utilities, or examples
3. **Import Management**: Organized imports with proper path handling
4. **Development Workflow**: Clear progression from examples to production usage
5. **Documentation Hierarchy**: Guides and references are easily accessible

This structure supports both beginner usage (examples) and advanced development (direct agent/utility usage) while maintaining clean separation of functionality.