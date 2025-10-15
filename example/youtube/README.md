# 🎥 YouTube Agent AgentOS

Production-ready YouTube content analyzer with FastAPI backend and web UI. Provides comprehensive video analysis, timestamp extraction, and intelligent content summarization.

## Features

- 📹 **Video Transcript Analysis**: Extract and analyze YouTube video transcripts
- ⏱️ **Smart Timestamps**: Generate precise timestamps with topic transitions
- 📚 **Content Organization**: Break down videos into structured segments
- 🎯 **Multi-Format Support**: Tutorials, reviews, lectures, creative content
- 💾 **Session Persistence**: SQLite for development, PostgreSQL for production
- 🌐 **REST API**: Production-ready FastAPI endpoints
- 🎨 **Web UI**: Interactive web interface for video analysis

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install directly:
```bash
pip install agno openai youtube-transcript-api sqlalchemy psycopg2-binary
```

### 2. Set Environment Variables

```bash
# Required
export OPENAI_API_KEY="your-openai-api-key"

# Optional: PostgreSQL for production
export DATABASE_URL="postgresql://user:password@localhost:5432/youtube_agent"
```

### 3. Run the Agent

```bash
python youtube_agentos.py
```

## Access Points

Once running, access the agent through:

- **Web UI**: http://localhost:7777/ui
- **API Docs**: http://localhost:7777/docs (Interactive OpenAPI documentation)
- **Health Check**: http://localhost:7777/health

## Usage Examples

### Via Web UI

1. Navigate to http://localhost:7777/ui
2. Enter a YouTube URL in the chat
3. Get instant video analysis with timestamps

### Via API

```bash
# Create a new session
curl -X POST "http://localhost:7777/v1/agents/youtube-analyst/run" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze this tutorial: https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "user_id": "user123",
    "session_id": "session456"
  }'
```

### Example Prompts

**Tutorials**:
- "Break down this Python tutorial with focus on code examples"
- "Create a learning path from this web development course"
- "Extract all practical exercises from this programming guide"

**Educational Content**:
- "Create a study guide with timestamps for this math lecture"
- "Extract main theories and examples from this science video"
- "Summarize the main arguments in this academic presentation"

**Tech Reviews**:
- "List all product features mentioned with timestamps"
- "Compare pros and cons discussed in this review"
- "Extract technical specifications and benchmarks"

**Creative Content**:
- "Break down the techniques shown in this art tutorial"
- "Create a timeline of project steps in this DIY video"
- "List all tools and materials mentioned with timestamps"

## Architecture

### Components

- **Agent**: YouTube content analyzer with transcript extraction tools
- **AgentOS**: Production runtime with FastAPI backend
- **Database**: Session and chat history persistence
  - Development: SQLite (`tmp/agents.db`)
  - Production: PostgreSQL (via `DATABASE_URL`)
- **Tools**: YouTubeTools for video transcript extraction

### Database Schema

The agent automatically creates and manages:
- `youtube_sessions` table for session metadata
- Chat history with user context
- Previous analysis retrieval for personalization

## Configuration

### Model Selection

Edit `youtube_agentos.py`:
```python
OPENAI_MODEL_ID = "gpt-5-mini"  # Change to gpt-4o, gpt-4-turbo, etc.
```

### Database Configuration

**Development** (default):
```python
# Uses SQLite automatically
agent_db = SqliteDb(session_table="youtube_sessions", db_file="tmp/agents.db")
```

**Production**:
```bash
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
```

### Server Configuration

Modify the `agent_os.serve()` call:
```python
agent_os.serve(
    app="youtube_agentos:app",
    host="0.0.0.0",    # Allow external connections
    port=7777,          # Change port
    reload=False        # Disable reload for production
)
```

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY youtube_agentos.py .
ENV OPENAI_API_KEY=""
ENV DATABASE_URL=""

EXPOSE 7777
CMD ["python", "youtube_agentos.py"]
```

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# Production database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Optional: Disable telemetry
AGNO_TELEMETRY=false
```

## API Reference

### POST /v1/agents/youtube-analyst/run

Analyze a YouTube video.

**Request Body**:
```json
{
  "message": "Analyze this video: https://youtube.com/watch?v=...",
  "user_id": "user123",
  "session_id": "session456"
}
```

**Response**:
```json
{
  "content": "📹 Video Analysis...",
  "metrics": {
    "time": 2.5,
    "tokens": 1500
  }
}
```

### GET /health

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "agents": ["youtube-analyst"]
}
```

## Troubleshooting

### Video Transcript Not Available

Some videos don't have transcripts or have disabled captions:
```
Error: Transcript not available for this video
```

**Solution**: The video must have captions enabled by the creator.

### Database Connection Issues

```
Error: Could not connect to database
```

**Solution**: Verify `DATABASE_URL` is correct and PostgreSQL is running.

### API Key Errors

```
Error: OpenAI API key not found
```

**Solution**: Set `OPENAI_API_KEY` environment variable.

## Development

### Running with Hot Reload

```bash
python youtube_agentos.py
# Server automatically reloads on code changes
```

### Testing the API

```bash
# Install httpie
pip install httpie

# Test the agent
http POST localhost:7777/v1/agents/youtube-analyst/run \
  message="Analyze: https://youtube.com/watch?v=dQw4w9WgXcQ" \
  user_id="test" \
  session_id="test123"
```

## Contributing

Contributions welcome! Areas for enhancement:
- Additional video metadata extraction
- Sentiment analysis of content
- Multi-language transcript support
- Video chapter detection
- Content categorization and tagging

## License

Same as the Agno framework.
