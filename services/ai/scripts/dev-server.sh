#!/bin/bash
# Simple development server script for FastAPI AgentChat service

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting FastAPI development server..."

# Kill any existing processes on port 8081
echo "🛑 Stopping any existing servers on port 8081..."
pkill -f 8081 || true

# Navigate to project root
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    uv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
uv sync

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create one from .env.example"
    exit 1
fi

echo "✅ Environment ready!"
echo "🌐 Starting server at http://0.0.0.0:8081"
echo "📖 API docs available at http://0.0.0.0:8081/docs"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the development server
exec uvicorn src.app.main:app \
    --host 0.0.0.0 \
    --port 8081 \
    --reload \
    --log-level info
