# Finance News AgentOS

A complete web-based interface for the Finance News Agent using agno's AgentOS framework.

## 🎯 Overview

Finance News AgentOS provides a production-ready web interface for the finance news agent, featuring:

- **Interactive Web UI** with custom finance-focused dashboard
- **RESTful API** endpoints for programmatic access
- **Real-time Financial Data** with multi-source integration
- **Session Management** with optional PostgreSQL persistence
- **Docker Support** for easy deployment
- **Multi-Model AI** support (Claude, OpenAI, Gemini)

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+**
2. **API Keys** (at minimum `ANTHROPIC_API_KEY`)
3. **Docker** (optional, for full production deployment)

### 🏃‍♂️ Fastest Start (Lightweight SQLite)

```bash
# Clone and navigate
cd example/news

# Set up environment
cp config/.env.example .env
nano .env  # Add your API keys

# Install dependencies
pip install -r requirements-agentos.txt

# Configure your AI model (interactive)
./scripts/configure.sh

# Start lightweight version
python finance_agentos_lite.py

# Access at http://localhost:8080
```

### 🐳 Full Production Setup

#### Installation

1. **Clone and navigate to the news directory**:
   ```bash
   cd example/news
   ```

2. **Set up environment**:
   ```bash
   # Copy environment template
   cp config/.env.example .env

   # Edit .env with your API keys
   nano .env
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements-agentos.txt
   ```

4. **Start the AgentOS**:
   ```bash
   # Lightweight SQLite version (recommended for development)
   python finance_agentos_lite.py

   # Or use the startup script
   ./scripts/start_agentos.sh lite

   # Full version with PostgreSQL support
   python finance_agentos.py

   # Or development mode
   ./scripts/start_agentos.sh dev
   ```

5. **Access the interface**:
   - **Web Dashboard**: http://localhost:8080
   - **API Documentation**: http://localhost:8080/docs
   - **Health Check**: http://localhost:8080/health

### 🌐 Enhanced Web UI (Node.js)

For a more advanced web interface with better markdown rendering:

```bash
# Start the enhanced web UI
./scripts/start_webui.sh

# Or manually
cd webui
npm install
npm start

# Access at http://localhost:3000
```

**Web UI Features**:
- **📊 Interactive Dashboard** - Modern responsive design
- **📝 Markdown Rendering** - Beautiful formatting with syntax highlighting
- **🔍 Real-time Analysis** - Live stock analysis and market overview
- **💬 Custom Queries** - Ask any financial question
- **📱 Mobile Friendly** - Works on all devices

## 🌐 Web Interface Features

### Dashboard (/)
Interactive finance-focused dashboard with:
- **Agent Status** indicator
- **Feature Overview** cards
- **Quick Access** to all endpoints
- **API Documentation** links

### Custom Finance Endpoints

#### `/finance/quick-analysis?symbol=AAPL`
```json
{
  "symbol": "AAPL",
  "analysis": "Apple Inc. (AAPL) analysis...",
  "timestamp": "2025-01-06T12:00:00Z"
}
```

#### `/finance/market-overview`
```json
{
  "overview": "Comprehensive market analysis...",
  "timestamp": "2025-01-06T12:00:00Z"
}
```

### Standard AgentOS Endpoints

- **`GET /health`** - System health check
- **`GET /agents`** - List all agents
- **`POST /agents/{agent_name}/runs`** - Execute agent queries
- **`GET /sessions`** - View chat sessions
- **`GET /docs`** - Interactive API documentation

## 🔧 Configuration

### 🤖 AI Model Configuration

**Interactive Setup (Recommended)**:
```bash
./scripts/configure.sh
```

**Manual Configuration**:
Edit `config/agentos_config.yaml`:
```yaml
model:
  primary: "claude"  # Choose: claude, openai, gemini
```

**Available Models**:
- **Claude 4.5 Sonnet** (Anthropic) - Best for financial analysis
- **GPT-5 Mini** (OpenAI) - Fast responses, good general knowledge
- **Gemini 2.5 Flash** (Google) - Good with data analysis

📖 **Detailed Guide**: See [CONFIG_GUIDE.md](CONFIG_GUIDE.md) for complete configuration options.

### Environment Variables

Required:
```bash
ANTHROPIC_API_KEY=your_anthropic_key
```

Optional:
```bash
# Additional AI Models
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key

# Enhanced Search
TAVILY_API_KEY=your_tavily_key

# Database (default: in-memory)
DATABASE_URL=postgresql://user:pass@localhost:5432/finance_agent

# Additional APIs
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
```

### Database Configuration

**SQLite (Lightweight Default)**:
- No Docker or PostgreSQL setup required
- Persistent storage in a single file
- Perfect for development and small deployments
- Conversation history maintained between restarts

**PostgreSQL (Production)**:
```bash
# Set DATABASE_URL in .env
DATABASE_URL=postgresql://user:pass@localhost:5432/finance_agent

# Or use Docker Compose
docker compose up postgres
```

## 🐳 Docker Deployment

### Quick Deploy
```bash
# Start with Docker Compose (includes PostgreSQL)
docker compose up --build

# Access at http://localhost:8080
```

### Custom Docker
```bash
# Build image
docker build -t finance-agentos .

# Run container
docker run -p 8080:8080 \
  -e ANTHROPIC_API_KEY=your_key \
  -v $(pwd)/reports:/app/reports \
  finance-agentos
```

## 📊 Usage Examples

### Python API Client
```python
import requests

# Quick analysis
response = requests.get(
    "http://localhost:8080/finance/quick-analysis?symbol=TSLA"
)
print(response.json())

# Run custom query
response = requests.post(
    "http://localhost:8080/agents/finance-news-agent/runs",
    data={"message": "Compare AAPL vs MSFT performance this quarter"}
)
print(response.json())
```

### cURL Examples
```bash
# Market overview
curl "http://localhost:8080/finance/market-overview"

# Custom analysis
curl -X POST "http://localhost:8080/agents/finance-news-agent/runs" \
  -F "message=What are the top 5 trending stocks today?"

# Health check
curl "http://localhost:8080/health"
```

### JavaScript/Fetch
```javascript
// Quick stock analysis
const response = await fetch('/finance/quick-analysis?symbol=NVDA');
const data = await response.json();
console.log(data.analysis);

// Custom query
// Using FormData for multipart/form-data
const formData = new FormData();
formData.append('message', 'Analyze cryptocurrency market trends');

const result = await fetch('/agents/finance-news-agent/runs', {
  method: 'POST',
  body: formData
});
```

## 🔧 Development

### Development Mode
```bash
# Auto-reload on changes
python finance_agentos.py

# Or with uvicorn directly
uvicorn finance_agentos:create_finance_agentos().get_app() \
  --reload --host 0.0.0.0 --port 8080
```

### Testing the API
```bash
# Test all endpoints
python -c "
from finance_agentos import create_finance_agentos
agentos = create_finance_agentos()
routes = agentos.get_routes()
print(f'Available routes: {len(routes)}')
"
```

### Custom Endpoints
Add new endpoints by modifying `finance_agentos.py`:

```python
@custom_app.get("/finance/portfolio-analysis")
async def portfolio_analysis(symbols: str):
    \"\"\"Analyze a portfolio of stocks\"\"\"
    result = finance_agent.run(f"Analyze portfolio: {symbols}")
    return {"analysis": str(result.content)}
```

## 🚨 Production Deployment

### Security Considerations
1. **Environment Variables**: Use secure secret management
2. **CORS**: Configure appropriate CORS origins
3. **Authentication**: Add JWT or API key authentication
4. **HTTPS**: Use reverse proxy (nginx) with SSL
5. **Rate Limiting**: Implement API rate limiting

### Performance Optimization
1. **Database**: Use PostgreSQL for persistence
2. **Caching**: Add Redis for response caching
3. **Load Balancing**: Multiple instances behind load balancer
4. **Monitoring**: Implement logging and metrics

### Example Production Setup
```bash
# docker compose.prod.yml
version: '3.8'
services:
  finance-agentos:
    image: finance-agentos:prod
    environment:
      - DATABASE_URL=postgresql://prod:secure@postgres:5432/finance
    depends_on:
      - postgres
      - redis

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./ssl:/etc/ssl
```

## 📈 Monitoring

### Health Endpoints
- **`/health`** - Basic health check
- **`/agents`** - Agent status
- **`/metrics`** - System metrics (if enabled)

### Logging
```python
import logging
logging.basicConfig(level=logging.INFO)

# View logs
tail -f /var/log/finance-agentos.log
```

### Database Monitoring
```sql
-- Check agent sessions
SELECT * FROM sessions ORDER BY created_at DESC LIMIT 10;

-- Monitor performance
SELECT agent_name, COUNT(*) as queries
FROM agent_runs
WHERE created_at > NOW() - INTERVAL '1 day'
GROUP BY agent_name;
```

## 🆘 Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Ensure paths are correct
export PYTHONPATH=/app:$PYTHONPATH
```

**API Key Issues**:
```bash
# Verify API keys
python -c "import os; print('ANTHROPIC_API_KEY:', bool(os.getenv('ANTHROPIC_API_KEY')))"
```

**Database Connection**:
```bash
# Test PostgreSQL connection
psql $DATABASE_URL -c "SELECT version();"
```

**Port Conflicts**:
```bash
# Use different port
uvicorn finance_agentos:app --port 8081
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug
python finance_agentos.py --debug
```

## 🔄 Version Comparison

| Feature | Standard Agent | AgentOS Lite | AgentOS Full |
|---------|---------------|--------------|--------------|
| **Interface** | CLI only | Web UI + API | Web UI + API |
| **Database** | Memory only | SQLite | SQLite/PostgreSQL |
| **Dependencies** | Minimal | Minimal | Docker/PostgreSQL |
| **Deployment** | Manual | Single file | Docker + Compose |
| **Persistence** | None | File-based | Production DB |
| **Setup Time** | < 1 min | < 2 min | 5-10 min |
| **Production Ready** | No | Small scale | Enterprise |

### AgentOS Lite vs Full

**Use AgentOS Lite when**:
- Development and testing
- Small-scale deployments
- Quick demos
- No Docker environment
- Single-user scenarios

**Use AgentOS Full when**:
- Production deployments
- Multi-user environments
- High availability requirements
- Enterprise scenarios
- Need PostgreSQL features

## 📄 License

Part of the agno News Agent framework. See main project license.

---

## 🚀 Next Steps

1. **Deploy to production** using Docker Compose
2. **Add authentication** for secure access
3. **Implement caching** with Redis
4. **Set up monitoring** with metrics
5. **Scale horizontally** with load balancing

For support, see the main agno documentation or the news agents guide.