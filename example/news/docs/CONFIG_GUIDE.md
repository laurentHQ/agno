# Configuration Guide - Finance News AgentOS

Complete guide to configuring your Finance News AgentOS before running.

## 🚀 Quick Start

### 1. Interactive Configuration (Recommended)

```bash
# Navigate to project directory
cd example/news

# Run interactive configuration
./scripts/configure.sh
```

This will:
- Check your API keys
- Show current configuration
- Let you choose your preferred AI model
- Validate the final setup

### 2. Manual Configuration

Edit `config/agentos_config.yaml` directly:

```yaml
model:
  primary: "claude"  # Choose: claude, openai, gemini
```

## 📋 Configuration File Structure

### Complete Configuration Reference

```yaml
# AI Model Configuration
model:
  primary: "claude"  # Primary model to use

  claude:
    model_id: "claude-sonnet-4-5"
    display_name: "Claude 4.5 Sonnet (Anthropic)"
    temperature: 0.1
    max_tokens: 4000

  openai:
    model_id: "gpt-5-mini"
    display_name: "GPT-5 Mini (OpenAI)"
    temperature: 0.1
    max_tokens: 4000

  gemini:
    model_id: "gemini-2.5-flash"
    display_name: "Gemini 2.5 Flash (Google)"
    temperature: 0.1
    max_tokens: 4000

# Database Configuration
database:
  type: "sqlite"  # sqlite, postgresql, memory

  sqlite:
    db_file: "finance_agent.db"
    enable_history: true

  postgresql:
    schema: "finance_agent"

# Server Configuration
server:
  host: "0.0.0.0"
  port: 8080
  reload: false
  log_level: "info"
  title: "Finance News AgentOS"
  description: "Interactive web interface for Financial News and Market Analysis"

# Agent Configuration
agent:
  name: "finance-news-agent"
  description: "Specialized Financial News and Market Analysis Agent"
  interactive: false
  markdown: true

# Tools Configuration
tools:
  tavily:
    enabled: true
    search_depth: "advanced"
    max_tokens: 6000
    include_answer: true
    format: "markdown"

  duckduckgo:
    enabled: true
    max_results: 10

  reddit:
    enabled: true
    max_posts: 5

# Feature Flags
features:
  enable_sessions: true
  enable_history: true
  enable_custom_endpoints: true
  enable_swagger_ui: true
  enable_redoc: true
```

## 🤖 AI Model Selection

### Available Models

| Model | API Key Required | Strengths |
|-------|-----------------|-----------|
| **Claude** | `ANTHROPIC_API_KEY` | Best reasoning, financial analysis |
| **OpenAI** | `OPENAI_API_KEY` | Fast responses, good general knowledge |
| **Gemini** | `GOOGLE_API_KEY` | Multimodal, good with data analysis |

### Setting API Keys

Add to your `.env` file:

```bash
# Choose one or more
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key

# Optional enhancements
TAVILY_API_KEY=your_tavily_key
```

### Model Configuration Details

**Claude (Recommended for Finance)**:
- Excellent reasoning and analysis
- Strong financial knowledge
- Conservative and accurate responses

**OpenAI GPT**:
- Fast response times
- Good general knowledge
- Creative problem-solving

**Gemini**:
- Good with data analysis
- Multimodal capabilities
- Competitive performance

## 💾 Database Options

### SQLite (Default - Recommended for Development)

```yaml
database:
  type: "sqlite"
  sqlite:
    db_file: "finance_agent.db"
    enable_history: true
```

**Pros**:
- No setup required
- Persistent storage
- Perfect for development
- Single file database

**Cons**:
- Single user only
- Limited concurrent access

### PostgreSQL (Production)

```yaml
database:
  type: "postgresql"
  postgresql:
    schema: "finance_agent"
```

Set `DATABASE_URL` in `.env`:
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/finance_agent
```

**Pros**:
- Multi-user support
- High performance
- Full ACID compliance
- Production ready

**Cons**:
- Requires setup
- More complex deployment

### Memory (Testing Only)

```yaml
database:
  type: "memory"
```

**Use only for**: Quick testing, temporary demos

## 🔧 Server Configuration

### Development Settings

```yaml
server:
  host: "127.0.0.1"  # Local only
  port: 8080
  reload: true        # Auto-reload on changes
  log_level: "debug"  # Verbose logging
```

### Production Settings

```yaml
server:
  host: "0.0.0.0"     # Accept external connections
  port: 8080
  reload: false       # Stable mode
  log_level: "info"   # Standard logging
```

## 🛠️ Tools Configuration

### Tavily AI Search (Recommended)

```yaml
tools:
  tavily:
    enabled: true
    search_depth: "advanced"  # basic, advanced
    max_tokens: 6000
    include_answer: true
    format: "markdown"
```

Requires: `TAVILY_API_KEY` in `.env`

### DuckDuckGo Search

```yaml
tools:
  duckduckgo:
    enabled: true
    max_results: 10
```

No API key required.

### Reddit Integration

```yaml
tools:
  reddit:
    enabled: true
    max_posts: 5
```

Optional: `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` in `.env`

## 🎛️ Feature Flags

Enable/disable specific features:

```yaml
features:
  enable_sessions: true      # Session management
  enable_history: true       # Conversation history
  enable_custom_endpoints: true  # /finance/* endpoints
  enable_swagger_ui: true    # /docs interface
  enable_redoc: true         # /redoc interface
```

## 📱 Usage Examples

### Switch to OpenAI

```bash
# Interactive
./scripts/configure.sh

# Or edit config/agentos_config.yaml:
model:
  primary: "openai"
```

### Custom Database Location

```bash
# Set in .env
SQLITE_DB_FILE=/path/to/my/finance.db
```

### Development Mode

```yaml
server:
  reload: true
  log_level: "debug"
```

### Production Mode

```yaml
server:
  reload: false
  log_level: "info"
database:
  type: "postgresql"
```

## 🔍 Validation and Troubleshooting

### Validate Configuration

```bash
# Check configuration
python -c "from utils.config_loader import validate_agentos_config; validate_agentos_config()"

# Or use the configuration script
./scripts/configure.sh
```

### Common Issues

**❌ "Missing API key"**
- Check your `.env` file
- Ensure the correct API key is set for your chosen model

**❌ "Configuration file not found"**
- Ensure you're in the correct directory
- Check that `config/agentos_config.yaml` exists

**❌ "Database connection failed"**
- For PostgreSQL: Check your `DATABASE_URL`
- For SQLite: Check file permissions

**❌ "Port already in use"**
- Change the port in `config/agentos_config.yaml`
- Or kill the process using the port

### Debug Mode

Enable debug logging:

```yaml
server:
  log_level: "debug"
```

## 🚀 Starting AgentOS

After configuration:

```bash
# Lightweight SQLite version
python finance_agentos_lite.py

# Or using startup script
./scripts/start_agentos.sh lite

# Full version with PostgreSQL
python finance_agentos.py
```

## 📚 Advanced Configuration

### Custom Model Parameters

```yaml
model:
  claude:
    temperature: 0.0    # More deterministic
    max_tokens: 8000    # Longer responses
```

### Multiple Environments

Create environment-specific configs:
- `config/agentos_config.dev.yaml`
- `config/agentos_config.prod.yaml`

Load with:
```python
agentos = create_finance_agentos_lite("config/agentos_config.prod.yaml")
```

### Rate Limiting

```yaml
rate_limiting:
  enabled: true
  requests_per_minute: 30
  burst_size: 5
```

---

## 🔗 Next Steps

1. **Configure your model**: `./scripts/configure.sh`
2. **Start AgentOS**: `python finance_agentos_lite.py`
3. **Access interface**: http://localhost:8080
4. **View API docs**: http://localhost:8080/docs

For more help, see the main [AGENTOS_README.md](AGENTOS_README.md).