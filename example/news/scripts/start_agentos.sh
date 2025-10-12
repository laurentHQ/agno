#!/bin/bash
# Startup script for Finance News AgentOS

echo "🏦 Starting Finance News AgentOS..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp config/.env.example .env
    echo "💡 Please edit .env with your API keys before running again"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Check if at least one API key is available
if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ] && [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ No AI model API keys found in .env file"
    echo "💡 Please set at least one of:"
    echo "  - ANTHROPIC_API_KEY (for Claude)"
    echo "  - OPENAI_API_KEY (for GPT models)"
    echo "  - GOOGLE_API_KEY (for Gemini)"
    exit 1
fi

# Check if running in Docker
if [ "$1" = "docker" ]; then
    echo "🐳 Starting with Docker Compose..."
    docker-compose -f docker/docker-compose.yml up --build
elif [ "$1" = "lite" ]; then
    echo "⚡ Starting lightweight SQLite version..."
    python src/api/finance_agentos_lite.py
elif [ "$1" = "dev" ]; then
    echo "🔧 Starting in development mode..."
    python src/api/finance_agentos.py
else
    echo "🚀 Starting in production mode..."
    python src/api/finance_agentos.py
fi