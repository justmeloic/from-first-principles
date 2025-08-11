#!/bin/bash
# Copyright 2025 Loïc Muhirwa
#
# Production deployment script for FastAPI AgentChat service
# This script sets up the FastAPI server to be accessible on the internet
# with proper security and performance configurations.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/.venv"
LOG_DIR="$PROJECT_ROOT/logs"
PID_FILE="$PROJECT_ROOT/uvicorn.pid"
ACCESS_LOG="$LOG_DIR/access.log"
ERROR_LOG="$LOG_DIR/error.log"

# Default values
WORKERS=${WORKERS:-4}
PORT=${PORT:-8081}
HOST=${HOST:-0.0.0.0}
RELOAD=${RELOAD:-false}

# Functions
print_banner() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "    FastAPI AgentChat Production Deployment"
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

check_requirements() {
    log_info "Checking system requirements..."

    # Check if running on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "Detected macOS system"
    fi

    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 is required but not installed"
        exit 1
    fi

    local python_version=$(python3 --version | cut -d' ' -f2)
    log_info "Python version: $python_version"

    # Check uv package manager
    if ! command -v uv &> /dev/null; then
        log_warn "uv package manager not found. Installing..."
        pip install uv
    fi

    # Check if virtual environment exists
    if [ ! -d "$VENV_PATH" ]; then
        log_warn "Virtual environment not found. Creating..."
        cd "$PROJECT_ROOT"
        uv venv
    fi

    log_info "Requirements check completed"
}

setup_environment() {
    log_info "Setting up environment..."

    # Create logs directory
    mkdir -p "$LOG_DIR"

    # Activate virtual environment and sync dependencies
    cd "$PROJECT_ROOT"
    source "$VENV_PATH/bin/activate"

    log_info "Installing/updating dependencies..."
    uv sync

    # Check if .env file exists
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_error ".env file not found. Please copy .env.example to .env and configure it."
        exit 1
    fi

    # Validate environment configuration
    log_info "Validating environment configuration..."
    python3 -c "
from src.app.core.config import settings
print(f'API Title: {settings.API_TITLE}')
print(f'Host: {settings.HOST}')
print(f'Port: {settings.PORT}')
print(f'Frontend URL: {settings.FRONTEND_URL}')
print(f'Environment: {settings.ENVIRONMENT}')
print('Environment validation successful!')
"

    log_info "Environment setup completed"
}

check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        log_warn "Port $port is already in use"
        local pid=$(lsof -ti :$port)
        log_warn "Process using port $port: PID $pid"
        read -p "Do you want to kill the process and continue? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill -9 $pid
            log_info "Process killed. Continuing..."
        else
            log_error "Deployment cancelled"
            exit 1
        fi
    fi
}

stop_server() {
    log_info "Stopping existing server..."

    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            log_info "Stopping server with PID: $pid"
            kill -TERM $pid

            # Wait for graceful shutdown
            local count=0
            while ps -p $pid > /dev/null 2>&1 && [ $count -lt 30 ]; do
                sleep 1
                count=$((count + 1))
            done

            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                log_warn "Force killing server"
                kill -9 $pid
            fi
        fi
        rm -f "$PID_FILE"
    fi

    # Kill any remaining uvicorn processes
    pkill -f "uvicorn.*src.app.main:app" 2>/dev/null || true

    log_info "Server stopped"
}

start_server() {
    log_info "Starting FastAPI server..."

    cd "$PROJECT_ROOT"
    source "$VENV_PATH/bin/activate"

    # Determine if we should use reload
    if [ "$RELOAD" = "true" ]; then
        log_warn "Running in development mode with auto-reload"
    fi

    # Production-ready uvicorn configuration
    local uvicorn_cmd="uvicorn src.app.main:app \
        --host $HOST \
        --port $PORT \
        --workers $WORKERS \
        --log-level info \
        --access-log \
        --use-colors"

    # Add reload flag for development
    if [ "$RELOAD" = "true" ]; then
        uvicorn_cmd="$uvicorn_cmd --reload"
        log_info "Starting development server with uvicorn..."
        exec $uvicorn_cmd
    else
        log_info "Starting production server with uvicorn..."

        # Create a simple background process management
        nohup $uvicorn_cmd > "$ACCESS_LOG" 2> "$ERROR_LOG" &
        local server_pid=$!
        echo $server_pid > "$PID_FILE"

        # Wait a moment for server to start
        sleep 3

        # Check if server started successfully
        if ps -p $server_pid > /dev/null 2>&1; then
            log_info "Server started successfully with PID: $server_pid"
        else
            log_error "Failed to start server"
            rm -f "$PID_FILE"
            exit 1
        fi
    fi
}

show_server_info() {
    log_info "Server deployment completed!"
    echo
    echo -e "${BLUE}Server Information:${NC}"
    echo -e "  URL: ${GREEN}http://$HOST:$PORT${NC}"
    echo -e "  Docs: ${GREEN}http://$HOST:$PORT/docs${NC}"
    echo -e "  ReDoc: ${GREEN}http://$HOST:$PORT/redoc${NC}"
    echo -e "  Workers: ${GREEN}$WORKERS${NC}"
    echo -e "  PID File: ${GREEN}$PID_FILE${NC}"
    echo -e "  Access Log: ${GREEN}$ACCESS_LOG${NC}"
    echo -e "  Error Log: ${GREEN}$ERROR_LOG${NC}"
    echo
    echo -e "${BLUE}CORS Configuration:${NC}"
    echo -e "  Allowed Origins: ${GREEN}https://fromfirstprinciple.com/agent/${NC}"
    echo
    echo -e "${YELLOW}Important Security Notes:${NC}"
    echo -e "  • Server is configured to accept requests ONLY from: https://fromfirstprinciple.com/agent/"
    echo -e "  • Make sure your firewall allows incoming connections on port $PORT"
    echo -e "  • Consider setting up SSL/TLS termination with a reverse proxy (nginx/apache)"
    echo -e "  • Monitor the logs regularly for any security issues"
    echo
    echo -e "${BLUE}Management Commands:${NC}"
    echo -e "  Stop server: ${GREEN}$0 stop${NC}"
    echo -e "  Restart server: ${GREEN}$0 restart${NC}"
    echo -e "  Check status: ${GREEN}$0 status${NC}"
    echo -e "  View logs: ${GREEN}tail -f $ACCESS_LOG${NC}"
    echo -e "  View errors: ${GREEN}tail -f $ERROR_LOG${NC}"
}

check_status() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            log_info "Server is running with PID: $pid"
            echo -e "  URL: ${GREEN}http://$HOST:$PORT${NC}"
            return 0
        else
            log_warn "PID file exists but server is not running"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        log_info "Server is not running"
        return 1
    fi
}

print_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  start     Start the server (default)"
    echo "  stop      Stop the server"
    echo "  restart   Restart the server"
    echo "  status    Check server status"
    echo "  help      Show this help message"
    echo
    echo "Options:"
    echo "  --dev             Run in development mode with auto-reload"
    echo "  --workers N       Number of worker processes (default: 4)"
    echo "  --port N          Port to bind to (default: 8081)"
    echo "  --host HOST       Host to bind to (default: 0.0.0.0)"
    echo
    echo "Examples:"
    echo "  $0                          # Start server in production mode"
    echo "  $0 start --dev              # Start in development mode"
    echo "  $0 restart --workers 8      # Restart with 8 workers"
    echo "  $0 stop                     # Stop the server"
}

# Parse command line arguments
COMMAND="start"
while [[ $# -gt 0 ]]; do
    case $1 in
        start|stop|restart|status|help)
            COMMAND="$1"
            shift
            ;;
        --dev)
            RELOAD=true
            shift
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Main execution
case $COMMAND in
    start)
        print_banner
        check_requirements
        setup_environment
        check_port $PORT
        stop_server
        start_server
        show_server_info
        ;;
    stop)
        print_banner
        stop_server
        ;;
    restart)
        print_banner
        check_requirements
        setup_environment
        stop_server
        sleep 1
        start_server
        show_server_info
        ;;
    status)
        check_status
        ;;
    help)
        print_usage
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        print_usage
        exit 1
        ;;
esac
