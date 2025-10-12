#!/bin/bash
# Startup script for Finance News AgentOS Web UI

echo "🌐 Starting Finance News AgentOS Web UI..."

# Navigate to web directory
cd "$(dirname "$0")/../web"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if AgentOS is running
echo "🔍 Checking AgentOS connection..."
AGENTOS_URL=${AGENTOS_URL:-"http://localhost:8080"}

if curl -s -f "${AGENTOS_URL}/health" > /dev/null 2>&1; then
    echo "✅ AgentOS is running at ${AGENTOS_URL}"
else
    echo "⚠️  AgentOS not reachable at ${AGENTOS_URL}"
    echo "💡 Make sure AgentOS is running:"
    echo "   cd .. && python src/api/finance_agentos_lite.py"
    echo ""
    echo "🚀 Starting Web UI anyway (will show connection error)..."
fi

# Set default port
PORT=${PORT:-3000}

echo ""
echo "=" * 50
echo "🌐 Finance News AgentOS Web UI"
echo "=" * 50
echo "📱 Web Interface: http://localhost:${PORT}"
echo "🔗 Backend (AgentOS): ${AGENTOS_URL}"
echo "=" * 50
echo ""

# Start the web UI
if [ "$1" = "dev" ]; then
    echo "🔧 Starting in development mode..."
    npm run dev
else
    echo "🚀 Starting production server..."
    npm start
fi