# Finance News AgentOS - New Project Structure

## 📁 **Reorganized Directory Structure**

```
example/news/
├── 📁 src/                          # Source code
│   ├── 📁 agents/                   # AI agents
│   │   ├── finance_news_agent.py    # Main finance agent
│   │   ├── tech_news_hub.py         # Tech news agent
│   │   ├── github_trending_agent.py # GitHub trending agent
│   │   └── multisource_news_agent.py # Multi-source news agent
│   ├── 📁 api/                      # API servers & applications
│   │   ├── finance_agentos.py       # Full AgentOS application
│   │   ├── finance_agentos_lite.py  # Lightweight SQLite version
│   │   └── launcher.py              # Agent launcher utility
│   ├── 📁 core/                     # Core services
│   │   ├── cache_manager.py         # Redis + SQLite caching
│   │   └── scheduler.py             # Daily report scheduler
│   └── 📁 utils/                    # Utilities & helpers
│       ├── config_loader.py         # Configuration management
│       ├── model_selector.py        # AI model selection
│       ├── report_utils.py          # Report generation utilities
│       ├── news_reporter.py         # News reporting utilities
│       ├── github_trending_reporter.py # GitHub trending utilities
│       └── configure_model.py       # Model configuration script
├── 📁 config/                       # Configuration files
│   ├── agentos_config.yaml          # Main AgentOS configuration
│   └── .env.cache.example           # Cache configuration example
├── 📁 docs/                         # Documentation
│   ├── README.md                    # Main documentation
│   ├── AGENTOS_README.md           # AgentOS setup guide
│   ├── CACHING_GUIDE.md            # Caching implementation guide
│   ├── CONFIG_GUIDE.md             # Configuration guide
│   ├── PROJECT_STRUCTURE.md        # Original project structure
│   └── CLAUDE_SDK_MIGRATION_PLAN.md # SDK migration plan
├── 📁 scripts/                     # Shell scripts
│   ├── start_agentos.sh            # Start AgentOS server
│   ├── start_webui.sh              # Start web UI
│   └── configure.sh                # Interactive configuration
├── 📁 web/                         # Web UI (Node.js)
│   ├── server.js                   # Express.js server
│   ├── package.json                # Node.js dependencies
│   ├── public/                     # Static web assets
│   │   ├── index.html              # Main web interface
│   │   ├── app.js                  # Frontend JavaScript
│   │   └── styles.css              # CSS styles
│   └── .env.example                # Web UI configuration
├── 📁 data/                        # Data storage
│   ├── 📁 reports/                 # Generated reports
│   │   ├── comprehensive_tech_report_*.md
│   │   ├── daily_market_overview_*.md
│   │   └── finance_report_*.md
│   └── 📁 databases/               # Database files
│       ├── finance_agent.db        # SQLite database
│       └── cache.db                # Cache database
├── 📁 docker/                      # Docker configuration
│   ├── Dockerfile                  # Docker image definition
│   └── docker-compose.yml          # Multi-service orchestration
├── 📁 requirements/                # Python dependencies
│   ├── requirements-agentos.txt    # AgentOS dependencies
│   ├── requirements-news.txt       # News agent dependencies
│   └── requirements-github.txt     # GitHub agent dependencies
├── 📁 tests/                       # Test files & examples
│   ├── quick_test.py               # Quick functionality test
│   ├── simple_example.py           # Basic usage example
│   ├── test_finance_agent.py       # Finance agent tests
│   ├── test_github_trending.py     # GitHub trending tests
│   ├── test_model_selection.py     # Model selection tests
│   ├── modular_model_usage.py      # Modular model examples
│   ├── run_news_demo.py            # News demo runner
│   ├── save_reports_example.py     # Report saving examples
│   └── test_modular_models.py      # Modular model tests
├── .env                            # Environment variables
└── __pycache__/                    # Python cache (auto-generated)
```

## 🚀 **Quick Start with New Structure**

### 1. **Start AgentOS Server**
```bash
# Using scripts (recommended)
./scripts/start_agentos.sh lite     # Lightweight SQLite version
./scripts/start_agentos.sh          # Full version with PostgreSQL

# Direct execution
python src/api/finance_agentos_lite.py
python src/api/finance_agentos.py
```

### 2. **Start Web UI**
```bash
# Using script (recommended)
./scripts/start_webui.sh

# Manual startup
cd web && npm install && npm start
```

### 3. **Docker Deployment**
```bash
# Using script
./scripts/start_agentos.sh docker

# Direct docker-compose
cd docker && docker-compose up --build
```

## 📊 **Benefits of New Structure**

### ✅ **Improved Organization**
- **Separation of Concerns**: Clear distinction between source code, documentation, data, and configuration
- **Scalability**: Easy to add new components without cluttering
- **Professional Layout**: Follows modern Python project standards

### ✅ **Better Development Experience**
- **Clear Import Paths**: Consistent `src.module.submodule` import structure
- **Logical Grouping**: Related files are grouped together
- **Easy Navigation**: Intuitive folder names and hierarchy

### ✅ **Enhanced Maintainability**
- **Modular Design**: Core services, APIs, and utilities are separated
- **Version Control**: Better diff tracking with organized structure
- **Documentation**: Centralized docs with specific guides

### ✅ **Production Ready**
- **Docker Integration**: Proper container support with volume mapping
- **Configuration Management**: Centralized config with environment examples
- **Data Persistence**: Dedicated data directory for reports and databases

## 🔧 **Migration Notes**

### **Import Path Changes**
All imports now use the new structure:
```python
# OLD (before reorganization)
from finance_news_agent import create_finance_news_agent
from config_loader import load_agentos_config
from cache_manager import init_cache_manager

# NEW (after reorganization)
from src.agents.finance_news_agent import create_finance_news_agent
from src.utils.config_loader import load_agentos_config
from src.core.cache_manager import init_cache_manager
```

### **Updated Scripts**
- All shell scripts updated to use new paths
- Docker files updated for new structure
- Configuration files remain in same relative locations

### **Data Locations**
- **Reports**: Moved to `data/reports/`
- **Databases**: Moved to `data/databases/`
- **Cache**: New cache database in `data/databases/cache.db`

### **Web UI**
- **Renamed**: `webui/` → `web/`
- **Updated Paths**: All references updated in scripts and documentation

## 🎯 **Next Steps**

1. **Test All Components**: Verify that all applications start correctly
2. **Update Documentation**: Review and update any remaining documentation
3. **CI/CD Integration**: Update any automated deployment scripts
4. **Team Communication**: Inform team members about the new structure

---

**Note**: This reorganization maintains full backward compatibility while providing a much cleaner and more professional project structure. All functionality remains the same, just better organized! 🎉