#!/bin/bash

# Finance News Agent - Start PostgreSQL for Testing
# ================================================

cd "$(dirname "$0")/docker"

echo "🔧 Checking Docker installation..."

# Check if docker compose V2 is available
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
    echo "✅ Using Docker Compose V2"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo "✅ Using Docker Compose V1"
else
    echo "❌ Docker Compose not found!"
    echo "Install: sudo apt-get install docker-compose-v2"
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env <<'EOF'
# AI Model API Keys (at least one required)
OPENAI_API_KEY=${OPENAI_API_KEY:-}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}

# Search & News API Keys (required)
TAVILY_API_KEY=${TAVILY_API_KEY:-}
BRAVE_API_KEY=${BRAVE_API_KEY:-}

# Agent Configuration
FINANCE_AGENT_MODEL=openai
DEBUG_MODE=false
EOF
    echo "📝 Created .env template. Please edit with your API keys."
fi

# Start PostgreSQL
echo "🚀 Starting PostgreSQL..."
$COMPOSE_CMD up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if $COMPOSE_CMD exec -T postgres pg_isready -U agentos -d finance_agent &> /dev/null; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo "❌ PostgreSQL failed to start in 30 seconds"
        $COMPOSE_CMD logs postgres
        exit 1
    fi
done

# Display connection info
echo ""
echo "=============================================="
echo "PostgreSQL is running!"
echo "=============================================="
echo "Host:     localhost"
echo "Port:     5432"
echo "Database: finance_agent"
echo "User:     agentos"
echo "Password: agentos_password"
echo ""
echo "Connection string:"
echo "postgresql://agentos:agentos_password@localhost:5432/finance_agent"
echo ""
echo "Test connection:"
echo "$COMPOSE_CMD exec postgres psql -U agentos -d finance_agent"
echo ""
echo "View logs:"
echo "$COMPOSE_CMD logs -f postgres"
echo "=============================================="
