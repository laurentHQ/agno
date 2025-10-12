#!/bin/bash
# Quick configuration script for Finance News AgentOS

echo "🤖 Finance News AgentOS Configuration"
echo "====================================="

# Navigate to project directory
cd "$(dirname "$0")/.."

# Check if config file exists
if [ ! -f "config/agentos_config.yaml" ]; then
    echo "❌ Configuration file not found!"
    echo "💡 Please make sure you're in the correct directory."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp config/.env.example .env
    echo "📝 Please edit .env with your API keys and run this script again."
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Run the Python configuration script
python src/utils/configure_model.py