#!/bin/bash
# Copyright 2025 Loïc Muhirwa
#
# Simple deployment script for FastAPI AgentChat service
# Runs the server and sets up ngrok tunneling in background

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/.venv"
PORT=8081
LOG_DIR="$PROJECT_ROOT/logs"
SERVER_PID_FILE="$PROJECT_ROOT/server.pid"
NGROK_PID_FILE="$PROJECT_ROOT/ngrok.pid"

print_banner() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "    AI Service Deployment"
    echo "=================================================="
    echo -e "${NC}"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    log_error "ngrok is required but not installed. Install from: https://ngrok.com/"
    exit 1
fi

# Handle stop command
if [ "$1" = "stop" ]; then
    print_banner
    log_info "Stopping all services..."
    
    # Create logs directory
    mkdir -p "$LOG_DIR"
    
    # Stop services (inline for stop command)
    if [ -f "$SERVER_PID_FILE" ]; then
        server_pid=$(cat "$SERVER_PID_FILE")
        if ps -p $server_pid > /dev/null 2>&1; then
            log_info "Stopping server (PID: $server_pid)"
            kill -TERM $server_pid 2>/dev/null || true
            sleep 2
            if ps -p $server_pid > /dev/null 2>&1; then
                kill -9 $server_pid 2>/dev/null || true
            fi
        fi
        rm -f "$SERVER_PID_FILE"
    fi

    if [ -f "$NGROK_PID_FILE" ]; then
        ngrok_pid=$(cat "$NGROK_PID_FILE")
        if ps -p $ngrok_pid > /dev/null 2>&1; then
            log_info "Stopping ngrok (PID: $ngrok_pid)"
            kill -TERM $ngrok_pid 2>/dev/null || true
        fi
        rm -f "$NGROK_PID_FILE"
    fi

    # Clean up any old PID files
    rm -f "$PROJECT_ROOT/uvicorn.pid"

    # Kill any remaining processes
    pkill -f "uvicorn.*src.app.main:app" 2>/dev/null || true
    pkill -f "ngrok.*http.*$PORT" 2>/dev/null || true
    
    # Kill any process using our port
    port_pid=$(lsof -ti:$PORT 2>/dev/null || true)
    if [ -n "$port_pid" ]; then
        log_info "Killing process using port $PORT (PID: $port_pid)"
        kill -9 $port_pid 2>/dev/null || true
    fi
    
    log_info "All services stopped"
    exit 0
fi

# Show banner
print_banner

# Create logs directory
mkdir -p "$LOG_DIR"

# Stop existing processes
stop_services() {
    if [ -f "$SERVER_PID_FILE" ]; then
        local server_pid=$(cat "$SERVER_PID_FILE")
        if ps -p $server_pid > /dev/null 2>&1; then
            log_info "Stopping existing server (PID: $server_pid)"
            kill -TERM $server_pid 2>/dev/null || true
            sleep 2
            # Force kill if still running
            if ps -p $server_pid > /dev/null 2>&1; then
                kill -9 $server_pid 2>/dev/null || true
            fi
        fi
        rm -f "$SERVER_PID_FILE"
    fi

    if [ -f "$NGROK_PID_FILE" ]; then
        local ngrok_pid=$(cat "$NGROK_PID_FILE")
        if ps -p $ngrok_pid > /dev/null 2>&1; then
            log_info "Stopping existing ngrok (PID: $ngrok_pid)"
            kill -TERM $ngrok_pid 2>/dev/null || true
        fi
        rm -f "$NGROK_PID_FILE"
    fi

    # Clean up any old PID files
    rm -f "$PROJECT_ROOT/uvicorn.pid"

    # Kill any remaining processes by name and port
    pkill -f "uvicorn.*src.app.main:app" 2>/dev/null || true
    pkill -f "ngrok.*http.*$PORT" 2>/dev/null || true
    
    # Kill any process using our port
    local port_pid=$(lsof -ti:$PORT 2>/dev/null || true)
    if [ -n "$port_pid" ]; then
        log_info "Killing process using port $PORT (PID: $port_pid)"
        kill -9 $port_pid 2>/dev/null || true
    fi
    
    # Wait a moment for ports to be released
    sleep 2
}

stop_services

# Setup virtual environment
log_info "Setting up virtual environment..."
cd "$PROJECT_ROOT"

if [ ! -d "$VENV_PATH" ]; then
    log_info "Creating virtual environment..."
    uv venv
fi

# Activate venv and sync dependencies
source "$VENV_PATH/bin/activate"
log_info "Installing/updating dependencies..."
uv sync

# Check for .env file
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    log_error ".env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Start FastAPI server in background
log_info "Starting FastAPI server on port $PORT"
cd "$PROJECT_ROOT"
source "$VENV_PATH/bin/activate"
nohup uvicorn src.app.main:app --host 0.0.0.0 --port $PORT --reload > "$LOG_DIR/server.log" 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > "$SERVER_PID_FILE"

# Wait for server to start
log_info "Waiting for server to start..."
sleep 5

# Check if server is running
if ps -p $SERVER_PID > /dev/null 2>&1; then
    log_info "Server started successfully (PID: $SERVER_PID)"
else
    log_error "Failed to start server"
    rm -f "$SERVER_PID_FILE"
    exit 1
fi

# Start ngrok in background
log_info "Starting ngrok tunnel for port $PORT"
nohup ngrok http $PORT > "$LOG_DIR/ngrok.log" 2>&1 &
NGROK_PID=$!
echo $NGROK_PID > "$NGROK_PID_FILE"

# Wait for ngrok to start
sleep 3

if ps -p $NGROK_PID > /dev/null 2>&1; then
    log_info "ngrok started successfully (PID: $NGROK_PID)"
else
    log_error "Failed to start ngrok"
    rm -f "$NGROK_PID_FILE"
fi

# Show status
log_info "Deployment completed!"
echo
echo -e "${GREEN}Services started:${NC}"
echo -e "  • FastAPI server running on http://localhost:$PORT (PID: $SERVER_PID)"
echo -e "  • ngrok tunnel forwarding to port $PORT (PID: $NGROK_PID)"
echo
echo -e "${YELLOW}Log files:${NC}"
echo -e "  • Server logs: ${GREEN}$LOG_DIR/server.log${NC}"
echo -e "  • ngrok logs: ${GREEN}$LOG_DIR/ngrok.log${NC}"
echo
echo -e "${YELLOW}Management commands:${NC}"
echo -e "  • View server logs: ${GREEN}tail -f $LOG_DIR/server.log${NC}"
echo -e "  • View ngrok logs: ${GREEN}tail -f $LOG_DIR/ngrok.log${NC}"
echo -e "  • Stop server: ${GREEN}kill \$(cat $SERVER_PID_FILE)${NC}"
echo -e "  • Stop ngrok: ${GREEN}kill \$(cat $NGROK_PID_FILE)${NC}"
echo -e "  • Stop all: ${GREEN}./scripts/deploy-server.sh stop${NC}"
echo
echo -e "${YELLOW}Check ngrok dashboard at: ${GREEN}http://localhost:4040${NC}"
